#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 v4.0 · ComfyUI 全自动后台批跑与微创重摇点火器 (Tunjing v4.0 Auto-Runner & Surgical Re-roller)

核心能力：
1. 断点续跑 (Checkpoint Resume)：崩溃或中断后重启自动跳过已落盘合格镜头，绝不重头白跑。
2. 点名微创重摇 (`--reroll 7,19 --candidates 2`)：只针对指定镜号更换随机 Seed 重跑 N 个候选版本 (`shot_07_v2.mp4`)，其余合格镜头物理锁死不动。
3. 自动五联抽帧质检板 (5-Frame Contact Sheet)：每镜落盘后自动用 FFmpeg 抽取 2%/25%/50%/75%/94% 五张关键帧拼成单张横条质检图 (`03_五联质检板/shot_XX_qc.jpg`)，一眼看穿有无多手/鬼影/字幕。
4. 跨集资产与声线锁死账本 (`series_bible.json`)：自动读取或初始化全剧统一的角色母版、空间图池、固定干声 WAV 与黄金 LoRA 配方，跨集拍 EP02~EP20 绝不失忆变脸。
5. 真实目录动态同步 + 文戏/肉戏 LoRA 权重动态切换 (`0.0` vs `0.45`) + 优先提取 `-audio.mp4` + 每镜 `/free` 冷却 10 秒。
"""

import os
import re
import sys
import json
import time
import random
import shutil
import subprocess
import argparse
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WF = os.path.join(BASE_DIR, "..", "references", "workflows", "tunjing_v4_master_api.json")
COMFY_URL = "http://127.0.0.1:8188"


def http_json(url, method="GET", payload=None, timeout=15):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw.strip() else {}


def load_or_init_series_bible(project_dir):
    """
    跨集资产与声线锁死账本 (series_bible.json)：
    优先查找父目录（剧集总目录）或当前项目目录下的 series_bible.json；若不存在则自动生成标准模板并锁死。
    """
    parent_bible = os.path.join(os.path.dirname(os.path.abspath(project_dir)), "series_bible.json")
    local_bible = os.path.join(project_dir, "series_bible.json")
    bible_path = parent_bible if os.path.exists(parent_bible) else local_bible

    if os.path.exists(bible_path):
        with open(bible_path, "r", encoding="utf-8") as f:
            return json.load(f), bible_path

    default_bible = {
        "schema": "tunjing-series-bible-v4",
        "locked_models": {
            "unet": "minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors",
            "clip": "qwen3vl_32b_minimax_h3_ultra_uncensored_heretic_int8_convrot.safetensors",
            "lora_dmad": {"name": "minimax_h3_dmad_full_dareties_v4_step600_comfy_fro.safetensors", "strength": 0.80},
            "lora_mystic": {"name": "MysticXXX_MMH3-V5-ref2va.safetensors", "drama_strength": 0.0, "action_strength": 0.45},
            "lora_style": {"name": "H3_RuMengSiHuan_1536-e8.safetensors", "strength": 0.80}
        },
        "characters": {
            "female_lead": {
                "dressed_master": "female_dressed.png",
                "nude_master": "female_nude.png",
                "voice_ref": "female_voice.wav"
            },
            "male_lead": {
                "dressed_master": "male_dressed.png",
                "nude_master": "male_nude.png",
                "voice_ref": "male_voice.wav"
            }
        },
        "spatial_pool": {
            "wide_main": "scene_main.png",
            "wall_elevation": "scene_wall.png",
            "close_surface": "scene_close.png"
        },
        "approved_seeds": {}
    }
    with open(local_bible, "w", encoding="utf-8") as f:
        json.dump(default_bible, f, ensure_ascii=False, indent=2)
    return default_bible, local_bible


def generate_5frame_contact_sheet(video_path, out_jpg_path):
    """
    使用 FFmpeg 抽取视频 2% / 25% / 50% / 75% / 94% 五个时间点的帧并横向拼接为单张质检板
    """
    if not os.path.exists(video_path):
        return False
    try:
        # 获取视频时长
        cmd_probe = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        r = subprocess.run(cmd_probe, capture_output=True, text=True, timeout=15)
        dur = float(r.stdout.strip() or "5.0")
        pcts = [0.02, 0.25, 0.50, 0.75, 0.94]
        tmp_frames = []
        os.makedirs(os.path.dirname(out_jpg_path), exist_ok=True)
        for idx, p in enumerate(pcts):
            ts = max(0.0, round(dur * p, 2))
            tf = f"{out_jpg_path}_tmp_{idx}.jpg"
            subprocess.run(
                ["ffmpeg", "-y", "-ss", str(ts), "-i", video_path, "-frames:v", "1", "-q:v", "3", tf],
                capture_output=True, timeout=15
            )
            if os.path.exists(tf):
                tmp_frames.append(tf)
        if len(tmp_frames) == 5:
            cmd_tile = [
                "ffmpeg", "-y",
                "-i", tmp_frames[0], "-i", tmp_frames[1], "-i", tmp_frames[2],
                "-i", tmp_frames[3], "-i", tmp_frames[4],
                "-filter_complex", "hstack=inputs=5", "-q:v", "2", out_jpg_path
            ]
            subprocess.run(cmd_tile, capture_output=True, timeout=20)
        for tf in tmp_frames:
            if os.path.exists(tf):
                os.remove(tf)
        return os.path.exists(out_jpg_path)
    except Exception:
        return False


def sync_assets_to_comfy(project_dir, comfy_input_dir):
    asset_dir = os.path.join(project_dir, "00_资产")
    if not os.path.isdir(asset_dir) or not comfy_input_dir or not os.path.isdir(comfy_input_dir):
        return 0
    copied = 0
    for fn in os.listdir(asset_dir):
        src = os.path.join(asset_dir, fn)
        if os.path.isfile(src) and all(ord(c) < 128 for c in fn):
            dst = os.path.join(comfy_input_dir, fn)
            shutil.copy2(src, dst)
            copied += 1
    return copied


def build_shot_workflow(base_wf, shot, custom_seed=None, prefix_override=None):
    import copy
    wf = copy.deepcopy(base_wf)
    ref_imgs = shot.get("ref_images", ["female_master.png", "male_master.png", "scene_main.png"])
    while len(ref_imgs) < 3:
        ref_imgs.append("scene_main.png")

    if "51" in wf:
        wf["51"]["inputs"]["image"] = ref_imgs[0]
    if "49" in wf:
        wf["49"]["inputs"]["image"] = ref_imgs[1]
    if "50" in wf:
        wf["50"]["inputs"]["image"] = ref_imgs[2]
    # 动态挂载第 4~9 扩展参考图槽位 (<Picture 4>~<Picture 9> -> Nodes 43, 19, 23, 199, 200, 201)
    # 有道具/扩展图时自动连上 Node 265，无道具镜自动断开 ref_image_3..8（绝不拔掉 Node 50 场景槽顶替！）
    extra_slot_nodes = [(3, "43"), (4, "19"), (5, "23"), (6, "199"), (7, "200"), (8, "201")]
    for slot_idx, node_id in extra_slot_nodes:
        port_key = f"ref_images.ref_image_{slot_idx}"
        if len(ref_imgs) > slot_idx and ref_imgs[slot_idx]:
            if node_id in wf:
                wf[node_id]["inputs"]["image"] = ref_imgs[slot_idx]
            if "265" in wf:
                wf["265"]["inputs"][port_key] = [node_id, 0]
        elif "265" in wf and port_key in wf["265"]["inputs"]:
            del wf["265"]["inputs"][port_key]

    if "400" in wf:
        wf["400"]["inputs"]["lora_name"] = shot.get("lora_mystic_name", "MysticXXX_MMH3-V5-ref2va.safetensors")
        wf["400"]["inputs"]["strength_model"] = float(shot.get("lora_mystic_strength", 0.45))

    if "397" in wf and custom_seed is not None:
        wf["397"]["inputs"]["seed"] = int(custom_seed)

    if "259" in wf:
        wf["259"]["inputs"]["value"] = float(shot.get("duration", 5.0))
    if "263" in wf:
        wf["263"]["inputs"]["text"] = shot.get("prompt", "")
    if "265" in wf:
        wf["265"]["inputs"]["ref_image_size"] = "match"
    if "364" in wf:
        num_m = re.search(r"(\d+)", str(shot.get("shot_id") or shot.get("id") or "1"))
        s_num = int(num_m.group(1)) if num_m else 1
        default_pfx = shot.get("filename_prefix") or f"EP001_SHOT_{s_num:03d}"
        wf["364"]["inputs"]["filename_prefix"] = prefix_override or default_pfx

    return wf


def parse_reroll_targets(reroll_str):
    if not reroll_str:
        return set()
    targets = set()
    for part in reroll_str.split(","):
        part = part.strip().lower().replace("shot_", "").replace("shot-", "")
        if part.isdigit():
            targets.add(int(part))
    return targets


def main():
    ap = argparse.ArgumentParser(description="吞鲸 v4.0 ComfyUI 全自动后台批跑与微创重摇点火器")
    ap.add_argument("project_dir", help="项目目录（内含 批量任务.json）")
    ap.add_argument("--dry-build", action="store_true", help="仅在本地生成逐镜就绪的 API JSON 包与跨集账本")
    ap.add_argument("--only-first", action="store_true", help="仅渲染第 1 镜用于首镜五联切片抽检")
    ap.add_argument("--reroll", default="", help="点名微创重摇指定镜号（逗号分隔，如 --reroll 7,19）")
    ap.add_argument("--candidates", type=int, default=1, help="每个重摇镜头生成的候选版本数（默认1，可设2~3挑片）")
    ap.add_argument("--force", action="store_true", help="忽略断点续跑缓存，强制重跑全部目标镜头")
    ap.add_argument("--confirm-token", default="", help="监制审阅《监制五维核对签字单.md》后签发的 8 位 SHA-256 点火授权码（未提供严禁连接 ComfyUI 渲染！）")
    args = ap.parse_args()

    bj_path = os.path.join(args.project_dir, "批量任务.json")
    if not os.path.exists(bj_path):
        print(f"[X] 未找到 {bj_path}！")
        sys.exit(1)

    bible, bible_path = load_or_init_series_bible(args.project_dir)
    print(f"[✓] 已加载跨集连续性锁死账本: {bible_path}")

    with open(bj_path, "r", encoding="utf-8") as f:
        batch = json.load(f)
    with open(DEFAULT_WF, "r", encoding="utf-8") as f:
        base_wf = json.load(f)

    all_shots = batch.get("batch_shots", [])
    reroll_set = parse_reroll_targets(args.reroll)

    if reroll_set:
        shots = [s for idx, s in enumerate(all_shots, 1) if idx in reroll_set]
        print(f"[🎯 微创重摇模式] 仅针对点名镜号 {sorted(reroll_set)} 重摇 {args.candidates} 个候选版本，其余镜头物理保护锁死！")
    elif args.only_first and all_shots:
        shots = all_shots[:1]
    else:
        shots = all_shots

    payload_dir = os.path.join(args.project_dir, "01_ComfyUI就绪负载")
    out_video_dir = os.path.join(args.project_dir, "02_成片输出")
    qc_sheet_dir = os.path.join(args.project_dir, "03_五联质检板")
    os.makedirs(payload_dir, exist_ok=True)
    os.makedirs(out_video_dir, exist_ok=True)
    os.makedirs(qc_sheet_dir, exist_ok=True)

    for s in shots:
        # ── 字幕物理自检锁 (Subtitle Physical-Gate)：提交前用引擎同源正则硬核弹回任何可能画字的提示词 ──
        #   这是全链路最后一道、也是唯一一道模型绕不过去的闸门：
        #   之前 7 次字幕翻车，根因都是「门禁查关键词，模型改关键词」的古德哈特循环。
        #   本锁不看关键词，只看三个物理事实：①有没有真人名 ②每条 <d> 前有没有 <Subject N> says 口型锚点 ③says: 是否与 <d> 断行。
        prompt = s.get("prompt", "")
        if prompt:
            real_name = re.search(r'(唐曼|陆骁|沈峥|许宁)', prompt)
            if real_name:
                print(f"[X 字幕物理自检熔断] {s.get('shot_id')} 提示词含真人名 '{real_name.group(1)}'！speaker 只能写女子A/男子A，否则触发性别熔断→画外音→闭唇→台词被画成字幕。拒绝提交，请回引擎重装配！")
                sys.exit(1)
            for dd in re.findall(r'<d>\[Chinese\].*?</d>', prompt, re.DOTALL):
                dd_ctx = prompt[max(0, prompt.find(dd) - 120):prompt.find(dd)]
                has_anchor = re.search(r'(?:<subject\s*\d+>\s*\(?s\d+\)?|女子a|男子a|subject\s*\d+)\s*.*?(?:says|speaks|whispers|gasps|moans|murmurs)\s*:\s*$', dd_ctx, re.IGNORECASE)
                if not has_anchor:
                    print(f"[X 字幕物理自检熔断] {s.get('shot_id')} 存在无说话人口型锚点的真实台词 '<d>[Chinese]…</d>'！模型会把无锚点台词当字幕画进画面。拒绝提交，请回引擎重装配！")
                    sys.exit(1)
            if re.search(r'says:\s*\n\s*<d>', prompt, re.IGNORECASE):
                print(f"[X 字幕物理自检熔断] {s.get('shot_id')} 检测到 'says:' 与 '<d>' 断行（SRT字幕格式诱导）！必须同行写 'says: <d>…</d>'。拒绝提交，请回引擎重装配！")
                sys.exit(1)

        wf = build_shot_workflow(base_wf, s)
        out_p = os.path.join(payload_dir, f"{s.get('shot_id', 'shot')}_api.json")
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(wf, f, ensure_ascii=False, indent=2)

    print(f"[✓] 已在 {payload_dir} 生成 {len(shots)} 份吞鲸 v4.0 逐镜 API 负载（已完成 LoRA 文肉分级与空间图池绑定）。")
    if args.dry_build:
        return

    # ── 物理防擅自开跑死锁 (Anti-Autostart Ignition Lock) ──
    # 1) 必须已通过 Gate 1 ~ Gate 5
    import hashlib
    status_file = os.path.join(args.project_dir, ".tunjing_status.json")
    if not os.path.exists(status_file):
        print("[X 越权拦截] 未找到 .tunjing_status.json！严禁跳过 Gate 1~5 擅自启动 ComfyUI 渲染！")
        sys.exit(1)
    st_data = json.load(open(status_file, "r", encoding="utf-8"))
    if not {1, 2, 3, 4, 5}.issubset(set(st_data.get("passed_steps", []))):
        print(f"[X 越权拦截] Gate 1~5 尚未全部通过 (当前仅通过: {st_data.get('passed_steps')})！严禁擅自提交渲染！")
        sys.exit(1)

    # 2) 必须校验 --confirm-token 与当前 批量任务.json 的前 8 位 SHA-256 一致
    h = hashlib.sha256()
    with open(bj_path, "rb") as bf:
        h.update(bf.read())
    expected_token = h.hexdigest()[:8]
    if args.confirm_token.strip() != expected_token:
        receipt_path = os.path.join(args.project_dir, "监制五维核对签字单.md")
        print("=" * 75)
        print("🛑 【吞鲸防擅自开跑物理死锁 (Ignition Lock) 触发】")
        print("原因：Agent 严禁在未经监制明确批准的情况下擅自向 ComfyUI 提交渲染任务！")
        print(f"请先向监制呈报对账表：{receipt_path}")
        print(f"待监制确认「参考图对齐、体位正确、交合特写齐备、台词无误」并下令渲染后，")
        print(f"方可使用当前任务包唯一授权码点火：--confirm-token {expected_token}")
        print("=" * 75)
        sys.exit(1)

    try:
        stats = http_json(f"{COMFY_URL}/system_stats")
    except Exception as e:
        print(f"[i] ComfyUI ({COMFY_URL}) 当前未启动 ({e})，已为您保存全部就绪负载至 {payload_dir}。")
        return

    argv = stats.get("system", {}).get("argv", [])
    input_dir = ""
    output_dir = ""
    for i, a in enumerate(argv):
        if a == "--input-directory" and i + 1 < len(argv):
            input_dir = argv[i + 1]
        if a == "--output-directory" and i + 1 < len(argv):
            output_dir = argv[i + 1]
    n_sync = sync_assets_to_comfy(args.project_dir, input_dir)
    print(f"[✓] ComfyUI 在线 | 已同步 {n_sync} 个 ASCII 资产至真实 Input 目录: {input_dir}")

    for idx, s in enumerate(shots, 1):
        ep_m = re.search(r"EP(\d+)", str(batch.get("project", "")) + " " + os.path.basename(os.path.abspath(args.project_dir)), re.IGNORECASE)
        ep_tag = f"EP{int(ep_m.group(1)):03d}" if ep_m else "EP001"
        sid_raw = str(s.get("shot_id") or s.get("id") or f"{idx:03d}")
        num_m = re.search(r"(\d+[A-Za-z]?)", sid_raw)
        s_tok = num_m.group(1) if num_m else f"{idx:03d}"
        if s_tok.isdigit():
            std_shot_name = f"{ep_tag}_SHOT_{int(s_tok):03d}"
        else:
            # 兼容如 04B 这种拆分镜号 -> EP001_SHOT_004B
            d_part = re.match(r"(\d+)([A-Za-z]+)", s_tok)
            std_shot_name = f"{ep_tag}_SHOT_{int(d_part.group(1)):03d}{d_part.group(2).upper()}" if d_part else f"{ep_tag}_SHOT_{idx:03d}"
        sid = s.get("filename_prefix") or std_shot_name
        target_mp4 = os.path.join(out_video_dir, f"{sid}.mp4")

        # 断点续跑保护：非 reroll 且非 force 时，若已存在合格 mp4 则自动跳过
        if not reroll_set and not args.force and os.path.exists(target_mp4) and os.path.getsize(target_mp4) > 100_000:
            print(f"[⏭ 断点续跑跳过] {sid}.mp4 已存在且完整，直接保护跳过。")
            continue

        n_cand = max(1, args.candidates) if reroll_set else 1
        for c_idx in range(1, n_cand + 1):
            seed_val = random.randint(10**13, 9 * 10**14)
            ver_suffix = f"_v{c_idx}" if n_cand > 1 or reroll_set else ""
            prefix = f"{sid}{ver_suffix}"
            wf = build_shot_workflow(base_wf, s, custom_seed=seed_val, prefix_override=prefix)

            # 反作弊锁 4A：提交前核验本镜 3 张参考图在 ComfyUI 真实 input 目录中物理存在（彻底杜绝空占位符 0.0s 秒退）
            if input_dir and os.path.isdir(input_dir):
                missing_refs = [r for r in s.get("ref_images", []) if not os.path.exists(os.path.join(input_dir, r))]
                if missing_refs:
                    print(f"[X 致命阻断] {sid} 绑定的参考图 {missing_refs} 在 ComfyUI Input 目录 ({input_dir}) 中不存在！拒绝提交空跑！")
                    sys.exit(1)

            t_start = time.time()
            print(f"\n[▶] ({idx}/{len(shots)}) 提交 {sid}{ver_suffix} | Seed={seed_val} | 姿势={s.get('pose')} | 时长={s.get('duration')}s ({s.get('frames')}f) | LoRA={s.get('lora_mystic_strength')}")
            resp = http_json(f"{COMFY_URL}/prompt", method="POST", payload={"prompt": wf})
            pid = resp.get("prompt_id")
            if not pid:
                print(f"[X] {sid} 提交失败: {resp}")
                sys.exit(1)

            while True:
                time.sleep(5)
                hist = http_json(f"{COMFY_URL}/history/{pid}")
                if pid in hist:
                    elapsed = round(time.time() - t_start, 1)
                    st_info = hist[pid].get("status", {})
                    outputs = hist[pid].get("outputs", {})
                    gifs = outputs.get("364", {}).get("gifs", [])
                    # 反作弊锁 4B：拦截 0.0s 秒退或无 MP4 产物的假完成！
                    if st_info.get("status_str") == "error" or not gifs or elapsed < 10.0:
                        print(f"[X 渲染异常中断] {sid} 耗时仅 {elapsed}s 且未产出有效视频！底层状态: {st_info}")
                        sys.exit(1)
                    picked = None
                    for g in gifs:
                        fn = g.get("filename", "")
                        if fn.endswith("-audio.mp4"):
                            picked = g
                            break
                    if not picked and gifs:
                        picked = gifs[0]
                    if picked:
                        fn = picked.get("filename")
                        sub = picked.get("subfolder", "")
                        src_vid = os.path.join(output_dir, sub, fn) if output_dir else fn
                        dst_vid = os.path.join(out_video_dir, f"{sid}{ver_suffix}.mp4")
                        if os.path.exists(src_vid) and os.path.getsize(src_vid) > 100_000:
                            shutil.copy2(src_vid, dst_vid)
                            qc_jpg = os.path.join(qc_sheet_dir, f"{sid}{ver_suffix}_qc5.jpg")
                            generate_5frame_contact_sheet(dst_vid, qc_jpg)
                            print(f"[✓] {sid}{ver_suffix} 真实渲染入库 ({elapsed}s) -> {dst_vid} | 五联质检板 -> {qc_jpg}")
                        else:
                            print(f"[X] {sid}{ver_suffix} 产物文件缺失或损坏: {src_vid}")
                            sys.exit(1)
                    break

            try:
                urllib.request.urlopen(urllib.request.Request(f"{COMFY_URL}/free", data=json.dumps({"unload_models": False, "free_memory": True}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST"), timeout=10).read()
            except Exception:
                pass
            time.sleep(10)


    # ── 全集渲染收官后：全自动串联【母带响度精修 + 自动打包打入剪映本地草稿箱】──
    if not reroll_set and not args.only_first:
        print("\n" + "=" * 70)
        print("🎬 全集镜头渲染完毕！正在自动启动【母带精修 (-16 LUFS) ➔ 自动导入剪映草稿箱】流水线...")
        print("=" * 70)
        master_script = os.path.join(BASE_DIR, "tunjing_mastering.py")
        jy_script = os.path.join(BASE_DIR, "export_jianying_draft.py")
        subprocess.run([sys.executable, master_script, args.project_dir])
        subprocess.run([sys.executable, jy_script, args.project_dir])


if __name__ == "__main__":
    main()
