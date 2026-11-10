#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 v3.0 · 剪映专业版草稿自动生成与工程落盘引擎 (Tunjing Jianying Draft Exporter v3.0)

功能：
1. 自动定位本机剪映草稿目录（默认 C:\\Users\\<User>\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft）
2. 强兼容解析吞鲸项目的 `分镜.md`（支持行内 `时长: 5.875s`、Markdown 表格 `| 时长 | 5.875s |`、标题行 `### SHOT-01 (5.875s | 141帧)` 三种格式）
3. 严禁静默兜底：任何镜头解析不出时长立即抛出 ValueError 中止导出，绝不编造非法秒数污染时间轴
4. 自动校验 H3 物理帧长公式 F = 5 + 17N
5. 自动构建包含视频轨、音频轨、字幕轨的剪映草稿（显式绑定 TrackRef），并支持 --dry-run 解析预检
"""

import os
import sys
import json
import re
import shutil
import argparse
import subprocess


def _import_draft():
    """按需导入 pyJianYingDraft，兼容 uv 与 pip 环境"""
    try:
        import pyJianYingDraft as draft
        return draft
    except ImportError:
        print("[!] 未检测到 pyJianYingDraft 库，正在尝试自动安装...")
        uv_bin = shutil.which("uv")
        if uv_bin:
            subprocess.check_call([uv_bin, "pip", "install", "--python", sys.executable, "pyJianYingDraft"])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyJianYingDraft"])
        import pyJianYingDraft as draft
        return draft



def register_in_root_meta_info(draft_root, draft_name, total_duration_us):
    """
    自动将新建草稿写入剪映 6.x 的 root_meta_info.json 总索引，确保打开剪映首页即可识别并双击打开！
    """
    import uuid, time
    rmi_path = os.path.join(draft_root, "root_meta_info.json")
    now_us = int(time.time() * 1_000_000)
    fold_norm = os.path.abspath(os.path.join(draft_root, draft_name)).replace("\\", "/")
    root_norm = os.path.abspath(draft_root).replace("\\", "/")

    data = {"all_draft_store": [], "draft_ids": 1}
    if os.path.exists(rmi_path):
        try:
            with open(rmi_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    store = data.get("all_draft_store", [])
    # 移除同名旧条目
    store = [x for x in store if x.get("draft_name") != draft_name]

    new_entry = {
        "cloud_draft_cover": False,
        "cloud_draft_sync": False,
        "draft_cloud_last_action_download": False,
        "draft_cloud_purchase_info": "",
        "draft_cloud_template_id": "",
        "draft_cloud_tutorial_info": "",
        "draft_cloud_videocut_purchase_info": "",
        "draft_cover": f"{fold_norm}\\draft_cover.jpg",
        "draft_fold_path": fold_norm,
        "draft_id": str(uuid.uuid4()).upper(),
        "draft_is_ai_shorts": False,
        "draft_is_cloud_temp_draft": False,
        "draft_is_infinite_canvas_draft": False,
        "draft_is_invisible": False,
        "draft_is_pippit_draft": False,
        "draft_is_web_article_video": False,
        "draft_json_file": f"{fold_norm}\\draft_content.json",
        "draft_name": draft_name,
        "draft_new_version": "164.0.0",
        "draft_root_path": root_norm,
        "draft_timeline_materials_size": 0,
        "draft_type": "",
        "draft_web_article_video_enter_from": "",
        "pippit_avatar_url": "",
        "pippit_extra_info": "",
        "pippit_id": "",
        "pippit_user_name": "",
        "streaming_edit_draft_ready": True,
        "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1,
        "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1,
        "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1,
        "tm_draft_create": now_us,
        "tm_draft_modified": now_us,
        "tm_draft_removed": 0,
        "tm_duration": int(total_duration_us),
    }
    store.insert(0, new_entry)
    data["all_draft_store"] = store
    with open(rmi_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    return new_entry["draft_id"]


def find_jianying_draft_root():
    """智能探测本机剪映草稿总目录"""
    candidates = [
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "JianyingPro", "User Data", "Projects", "com.lveditor.draft"),
        r"D:\JianyingPro Drafts",
        r"E:\JianyingPro Drafts",
        r"D:\JianyingPro\User Data\Projects\com.lveditor.draft",
        r"E:\JianyingPro\User Data\Projects\com.lveditor.draft",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]


def _cell(block, *keys):
    """从 Markdown 表格或行内写法取值。
    | 时长 | 5.875s |   →  _cell(b, "时长") == "5.875s"
    时长: 5.875s        →  同样返回 "5.875s"
    - **时长**：5.875s  →  同样返回 "5.875s"
    """
    for k in keys:
        # 1. 表格：| 时长 | 5.875s |
        m = re.search(rf"\|\s*\*{{0,2}}{re.escape(k)}\*{{0,2}}\s*\|\s*([^|\n]+?)\s*\|", block, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
        # 2. 行内：时长: 5.875s 或 - **时长**：5.875s
        m = re.search(rf"(?:^|[\n\-*•\s])\*{{0,2}}{re.escape(k)}\*{{0,2}}\s*[:：]\s*([^\n|]+)", block, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


def _clean(txt):
    """去掉反引号、粗体星号、首尾空白。"""
    return re.sub(r"[`*]", "", txt or "").strip()


def check_frame_legal(frames):
    """H3 帧长公式 F = 5 + 17N。"""
    return frames >= 5 and (frames - 5) % 17 == 0


def h3_frames(sec):
    """按 MiniMax H3 节点公式换算严格物理帧数: length = 5 + 17 * N"""
    raw = max(5, round(float(sec) * 24))
    return raw + (5 - (raw % 17)) % 17


def parse_storyboard_md(sb_file):
    """解析 分镜.md，支持行内、Markdown表格、标题行括号三种格式；缺失时长立即抛 ValueError 中止"""
    if not os.path.exists(sb_file):
        raise FileNotFoundError(f"未找到分镜文件: {sb_file}")

    with open(sb_file, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"(?:^|\n)###?\s*\[?SHOT[-_\s]*", content, flags=re.IGNORECASE)
    shots = []
    missing = []

    for b in blocks[1:]:
        lines = [line.strip() for line in b.strip().split("\n") if line.strip()]
        if not lines:
            continue
        header = lines[0]
        shot_id_match = re.search(r"^([A-Za-z]*\d+)", header)
        raw_id = shot_id_match.group(1) if shot_id_match else str(len(shots) + 1)
        num_m = re.search(r"(\d+)", raw_id)
        shot_idx = int(num_m.group(1)) if num_m else (len(shots) + 1)
        shot_tag = f"SHOT-{shot_idx:02d}" if raw_id.isdigit() else f"SHOT-{raw_id}"

        # ── 时长四级解析：标题行括号 → 表格 → 行内 → 报错（严禁静默兜底 3.0）──
        dur = None

        # 1. 标题行括号：### SHOT-01 (5.875s | 141帧 | wide | static_rear)
        m = re.search(r"\(([\d.]+)\s*s(?:\s*\||\s*\)|\b)", header, flags=re.IGNORECASE)
        if m:
            dur = float(m.group(1))

        # 2. 表格或通用键值：| 时长 | 5.875s |
        if dur is None:
            dur_txt = _cell(b, "时长", "duration", "时长(s)", "单镜时长")
            if dur_txt:
                m = re.search(r"([\d.]+)", dur_txt)
                if m:
                    dur = float(m.group(1))

        # 3. 行内：时长: 5.875s
        if dur is None:
            m = re.search(r"时长\s*[:：]\s*([\d.]+)\s*s", b)
            if m:
                dur = float(m.group(1))

        # 4. 全失败 → 记录缺失镜号，统一抛错中止
        if dur is None:
            missing.append(shot_tag)
            continue

        # ── 帧数提取与合法性检查 ──
        frames = None
        fm = re.search(r"(?:H3帧数|帧数|frames)\s*[:：]?\s*(\d+)\s*(?:帧|f\b|frames)?|(?<!Re)(\d+)\s*帧", header + "\n" + b, flags=re.IGNORECASE)
        if fm:
            frames = int(fm.group(1) or fm.group(2))
        else:
            f_txt = _cell(b, "帧数", "H3帧数", "frames")
            if f_txt:
                fm2 = re.search(r"(\d+)", f_txt)
                if fm2:
                    frames = int(fm2.group(1))
        if frames is None:
            frames = round(dur * 24)

        # ── 台词提取（支持 <d>[Chinese]...</d>、<d>...</d> 及表格台词列）──
        speech_matches = re.findall(r"<d>(?:\[Chinese\])?(.*?)</d>", b, flags=re.DOTALL)
        if speech_matches:
            speech = " / ".join(s.strip() for s in speech_matches if s.strip())
        else:
            sp_cell = _clean(_cell(b, "台词", "对白", "dialogue"))
            speech = "" if sp_cell in ("无", "—", "-", "N/A", "None") else sp_cell

        # ── 体位双格式提取（行内 + 表格 + 标题括号）──
        pose_id, pose_zh = "", ""
        pose_raw = _cell(b, "体位", "姿势", "姿势代号", "姿势类别", "pose", "pose_id")
        if pose_raw:
            m_id = re.search(r"`?([a-z][a-z_0-9->]{1,40})`?", pose_raw)
            if m_id:
                pose_id = m_id.group(1)
            m_zh = re.search(r"[（(](.*?)[）)]", pose_raw)
            if m_zh:
                pose_zh = m_zh.group(1).strip()
            elif not pose_id:
                pose_zh = _clean(pose_raw)

        # ── 景别、机位、场景兼容提取（优先表格/行内，次选标题行竖线分隔）──
        framing = _clean(_cell(b, "景别", "景别与机位", "framing"))
        camera = _clean(_cell(b, "机位", "camera"))
        scene = _clean(_cell(b, "场景", "场景与空间", "scene"))

        if not framing or not camera:
            hdr_parts = [p.strip() for p in re.findall(r"\((.*?)\)", header)]
            if hdr_parts:
                segs = [x.strip() for x in hdr_parts[0].split("|")]
                for seg in segs:
                    if seg in ("wide", "mcu", "cu", "macro", "hip", "face") and not framing:
                        framing = seg
                    elif seg.startswith(("static_", "low_", "high_", "slow_", "follow_", "ots")) and not camera:
                        camera = seg
                    elif re.match(r"^[a-z][a-z_0-9->]+$", seg) and not pose_id:
                        pose_id = seg

        shots.append({
            "index": shot_idx,
            "id": shot_tag,
            "duration": dur,
            "frames": frames,
            "frame_legal": check_frame_legal(frames),
            "speech": speech,
            "pose": pose_id,
            "pose_zh": pose_zh,
            "framing": framing,
            "camera": camera,
            "scene": scene,
            "raw_block": b
        })

    if missing:
        raise ValueError(
            "以下镜头解析不出时长，已中止导出（避免时间轴被静默压错）：\n  "
            + "\n  ".join(missing)
            + "\n请检查 分镜.md 中每镜是否有 `| 时长 | X.XXXs |` 或 `时长: X.XXXs` 或标题行 `(X.XXXs | ...)`。"
        )

    return shots



def _fmt_srt_time(sec):
    ms = int(round((sec - int(sec)) * 1000))
    s = int(sec) % 60
    m = (int(sec) // 60) % 60
    h = int(sec) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def export_srt_file(shots, out_srt_path):
    """生成与分镜时间轴毫秒级对齐的标准 SRT 字幕文件（防剪映 6.x 加密拦截的终极双保险）"""
    lines = []
    cur = 0.0
    sub_idx = 1
    for s in shots:
        dur = float(s["duration"])
        sp = (s.get("speech") or "").strip()
        if sp:
            # 对齐三段式念白窗口（取镜头中间段或全镜）
            t0 = cur + min(0.5, dur * 0.15)
            t1 = cur + max(dur - 0.2, dur * 0.90)
            lines.append(str(sub_idx))
            lines.append(f"{_fmt_srt_time(t0)} --> {_fmt_srt_time(t1)}")
            lines.append(sp)
            lines.append("")
            sub_idx += 1
        cur += dur
    with open(out_srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return sub_idx - 1


def print_dryrun_summary(sb_file, shots):
    """打印 --dry-run 解析统计"""
    total_dur = sum(s["duration"] for s in shots)
    n_speech = sum(1 for s in shots if s["speech"])
    n_pose = sum(1 for s in shots if s["pose"])
    n_framing = sum(1 for s in shots if s["framing"])
    n_cam = sum(1 for s in shots if s["camera"])
    illegal_frames = [f"{s['id']}({s['frames']}f)" for s in shots if not s["frame_legal"]]

    print("=" * 65)
    print("🐳 吞鲸宝典 · 剪映草稿解析器预检 (--dry-run)")
    print(f"分镜文件     : {sb_file}")
    print(f"镜头数       : {len(shots)}")
    print(f"总时长       : {total_dur:.3f}s")
    print(f"兜底 3.0s    : 0 镜")
    print(f"台词命中     : {n_speech} 处")
    print(f"景别命中     : {n_framing} 镜")
    print(f"机位命中     : {n_cam} 镜")
    print(f"体位命中     : {n_pose} 镜")
    if illegal_frames:
        print(f"[!] 帧长预警 : 以下镜头不满足 F=5+17N: {', '.join(illegal_frames)}")
    else:
        print(f"帧数校验     : {len(shots)}/{len(shots)} 全部符合 F=5+17N")
    print("=" * 65)


def export_to_jianying(project_dir=None, storyboard_file=None, draft_name=None,
                       video_dir=None, draft_root=None, dry_run=False):
    """核心导出函数：将吞鲸项目打包进剪映草稿"""
    if storyboard_file:
        sb_file = os.path.abspath(storyboard_file)
        if not project_dir:
            project_dir = os.path.dirname(sb_file)
    elif project_dir:
        project_dir = os.path.abspath(project_dir)
        sb_file = os.path.join(project_dir, "分镜.md")
    else:
        raise ValueError("必须提供 project_dir 或 --storyboard 分镜文件路径！")

    shots = parse_storyboard_md(sb_file)
    if not shots:
        raise ValueError("分镜中未解析出任何有效镜头！")

    srt_path = os.path.join(project_dir, '全集卡点字幕.srt')
    n_subs = export_srt_file(shots, srt_path)
    print(f'[✓] 已同步生成剪映通用毫秒级卡点字幕 ({n_subs} 条): {srt_path}')
    if dry_run:
        print_dryrun_summary(sb_file, shots)
        return None

    draft = _import_draft()

    if not draft_name:
        draft_name = os.path.basename(os.path.abspath(project_dir))

    if not draft_root:
        draft_root = find_jianying_draft_root()

    os.makedirs(draft_root, exist_ok=True)
    folder = draft.DraftFolder(draft_root)

    total_dur = sum(s["duration"] for s in shots)
    print("=" * 65)
    print("🐳 吞鲸宝典 · 剪映专业版草稿自动生成流水线")
    print(f"目标草稿名称: {draft_name}")
    print(f"剪映工程目录: {draft_root}")
    print(f"输入镜头数量: {len(shots)} 镜 | 解析总时长: {total_dur:.3f}s | 兜底 3.0s: 0 镜")
    print("=" * 65)

    illegal = [f"{s['id']}({s['duration']}s/{s['frames']}f)" for s in shots if not s["frame_legal"]]
    if illegal:
        print(f"[!] 警告：检测到非标准 H3 帧长镜头 (不满足 F=5+17N): {', '.join(illegal)}")

    # 竖屏漫剧标准画幅 9:16 (1080x1920)
    # 预先显式初始化视频轨、音频轨与文本字幕轨并保存轨道引用 (TrackRef)
    script = folder.create_draft(draft_name, 1080, 1920, allow_replace=True)
    v_track_ref = script.append_track(draft.TrackSpec(draft.TrackType.video, name="视频轨"))
    a_track_ref = script.append_track(draft.TrackSpec(draft.TrackType.audio, name="音频轨"))
    t_track_ref = script.append_track(draft.TrackSpec(draft.TrackType.text, name="字幕轨"))

    # 1. 扫描渲染视频文件
    search_dirs = [
        video_dir,
        os.path.join(project_dir, "04_母带精修缓存"),
        os.path.join(project_dir, "02_成片输出"),
        os.path.join(project_dir, "output"),
        os.path.join(project_dir, "renders"),
        os.path.join(project_dir, "batch"),
        project_dir
    ]
    search_dirs = [d for d in search_dirs if d and os.path.exists(d)]

    current_us = 0  # 剪映内部时间单位为微秒 (1s = 1,000,000 us)

    for s in shots:
        dur_us = int(round(s["duration"] * 1_000_000))
        shot_tag = s["id"]

        # 查找对应视频文件
        matched_mp4 = None
        for sd in search_dirs:
            for f in sorted(os.listdir(sd)):
                fl = f.lower()
                if fl.endswith((".mp4", ".mov", ".webm")) and (
                    shot_tag.lower() in fl
                    or f"shot_{s['index']:02d}" in fl
                    or f"shot_{s['index']}." in fl
                    or f"shot-{s['index']:02d}" in fl
                ):
                    matched_mp4 = os.path.join(sd, f)
                    if fl.endswith("-audio.mp4"):
                        break  # 优先取带音轨的 -audio.mp4
            if matched_mp4:
                break

        # 挂载视频轨道
        if matched_mp4 and os.path.exists(matched_mp4):
            v_mat = draft.VideoMaterial(matched_mp4)
            v_seg = draft.VideoSegment(
                v_mat,
                target_timerange=draft.Timerange(current_us, dur_us)
            )
            script.add_segment(v_seg, track=v_track_ref)
            print(f"  [+] {shot_tag} 视频已对位: {os.path.basename(matched_mp4)} ({s['duration']:.3f}s)")

        # 挂载字幕轨道（若本镜有对白台词）
        if s["speech"]:
            txt_seg = draft.TextSegment(
                s["speech"],
                draft.Timerange(current_us, dur_us),
                style=draft.TextStyle(size=8.0, color=(1.0, 1.0, 1.0)),
                border=draft.TextBorder(color=(0.0, 0.0, 0.0), width=0.15),
                clip_settings=draft.ClipSettings(transform_y=-0.75)
            )
            script.add_segment(txt_seg, track=t_track_ref)
            print(f"  [+] {shot_tag} 字幕已卡点: 「{s['speech']}」")

        current_us += dur_us

    # 保存草稿并自动写入剪映 root_meta_info.json 首页总索引
    script.save()
    reg_id = register_in_root_meta_info(draft_root, draft_name, current_us)
    print(f'[✓] 已自动登记至剪映首页 root_meta_info.json 总索引 (Draft ID: {reg_id})')

    target_draft_path = os.path.join(draft_root, draft_name)
    print("\n" + "=" * 65)
    print("🎉 剪映草稿生成 100% 成功！")
    print(f"草稿物理路径: {target_draft_path}")
    print("使用方法：打开电脑上的【剪映专业版】，在首页“本地草稿”列表即可直接看到并双击打开本剧！")
    print("=" * 65)
    return target_draft_path


def main():
    ap = argparse.ArgumentParser(description="吞鲸分镜一键转剪映草稿工程 (支持三种分镜格式与严格帧长校验)")
    ap.add_argument("project_dir", nargs="?", default="", help="吞鲸项目目录（内含 分镜.md）")
    ap.add_argument("--storyboard", default="", help="直接指定 分镜.md 文件路径")
    ap.add_argument("--name", default="", help="草稿名称（默认同项目目录名）")
    ap.add_argument("--video-dir", default="", help="渲染视频所在目录（可选）")
    ap.add_argument("--draft-root", default="", help="自定义剪映草稿根目录（可选）")
    ap.add_argument("--dry-run", action="store_true", help="仅解析分镜并打印时长/帧长/台词统计，不写入剪映目录")
    args = ap.parse_args()

    if not args.project_dir and not args.storyboard:
        ap.print_help()
        sys.exit(1)

    export_to_jianying(
        project_dir=args.project_dir,
        storyboard_file=args.storyboard,
        draft_name=args.name,
        video_dir=args.video_dir,
        draft_root=args.draft_root,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
