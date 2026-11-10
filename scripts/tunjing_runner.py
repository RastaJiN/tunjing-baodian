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

    if "400" in wf:
        wf["400"]["inputs"]["lora_name"] = shot.get("lora_mystic_name", "MysticXXX_MMH3-V5-ref2va.safetensors")
        wf["400"]["inputs"]["strength_model"] = float(shot.get("lora_mystic_strength", 0.45))

    if "397" in wf and custom_seed is not None:
        wf["397"]["inputs"]["seed"] = int(custom_seed)

    if "259" in wf:
        wf["259"]["inputs"]["value"] = float(shot.get("duration", 5.0))
    if "263" in wf:
        wf["263"]["inputs"]["text"] = shot.get("prompt", "")
    if "364" in wf:
        wf["364"]["inputs"]["filename_prefix"] = prefix_override or f"TunjingV4_{shot.get('shot_id', 'shot')}_"

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
        wf = build_shot_workflow(base_wf, s)
        out_p = os.path.join(payload_dir, f"{s.get('shot_id', 'shot')}_api.json")
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(wf, f, ensure_ascii=False, indent=2)

    print(f"[✓] 已在 {payload_dir} 生成 {len(shots)} 份吞鲸 v4.0 逐镜 API 负载（已完成 LoRA 文肉分级与空间图池绑定）。")
    if args.dry_build:
        return

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
        sid = s.get("shot_id", f"shot_{idx:02d}")
        target_mp4 = os.path.join(out_video_dir, f"{sid}.mp4")

        # 断点续跑保护：非 reroll 且非 force 时，若已存在合格 mp4 则自动跳过
        if not reroll_set and not args.force and os.path.exists(target_mp4) and os.path.getsize(target_mp4) > 100_000:
            print(f"[⏭ 断点续跑跳过] {sid}.mp4 已存在且完整，直接保护跳过。")
            continue

        n_cand = max(1, args.candidates) if reroll_set else 1
        for c_idx in range(1, n_cand + 1):
            seed_val = random.randint(10**13, 9 * 10**14)
            ver_suffix = f"_v{c_idx}" if n_cand > 1 or reroll_set else ""
            prefix = f"TunjingV4_{sid}{ver_suffix}_"
            wf = build_shot_workflow(base_wf, s, custom_seed=seed_val, prefix_override=prefix)

            print(f"\n[▶] ({idx}/{len(shots)}) 提交 {sid}{ver_suffix} | Seed={seed_val} | 姿势={s.get('pose')} | 时长={s.get('duration')}s ({s.get('frames')}f) | LoRA={s.get('lora_mystic_strength')}")
            resp = http_json(f"{COMFY_URL}/prompt", method="POST", payload={"prompt": wf})
            pid = resp.get("prompt_id")
            if not pid:
                print(f"[X] {sid} 提交失败: {resp}")
                continue

            while True:
                time.sleep(5)
                hist = http_json(f"{COMFY_URL}/history/{pid}")
                if pid in hist:
                    outputs = hist[pid].get("outputs", {})
                    gifs = outputs.get("364", {}).get("gifs", [])
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
                        if os.path.exists(src_vid):
                            shutil.copy2(src_vid, dst_vid)
                            qc_jpg = os.path.join(qc_sheet_dir, f"{sid}{ver_suffix}_qc5.jpg")
                            generate_5frame_contact_sheet(dst_vid, qc_jpg)
                            print(f"[✓] {sid}{ver_suffix} 已入库 -> {dst_vid} | 五联质检板 -> {qc_jpg}")
                        else:
                            print(f"[✓] {sid}{ver_suffix} 渲染完成 -> {fn}")
                    break

            try:
                http_json(f"{COMFY_URL}/free", method="POST", payload={"unload_models": False, "free_memory": True})
            except Exception:
                pass
            time.sleep(10)


if __name__ == "__main__":
    main()
