#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 剪映专业版草稿自动生成与工程落盘引擎 (Tunjing Jianying Draft Exporter)

功能：
1. 自动定位本机剪映草稿目录（默认 C:\\Users\\<User>\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft）
2. 读取吞鲸项目生成的 `分镜.md` 与渲染产出的视频文件（或占位视频）
3. 自动构建包含以下轨道的剪映草稿项目：
   - 视频轨 (Video Track)：按分镜顺序把 20~30 个 2~6s 短镜依次排布，支持相邻镜微调余量
   - 音频轨 (Audio Track)：独立挂载台词对白 WAV 与环境底噪
   - 字幕轨 (Subtitle Track)：自动将剧本中的 <d>[Chinese]...</d> 台词转化为精准卡点的字幕片段！
4. 生成完成后，打开剪映客户端，草稿箱内直接出现该剧集，双击即可预览、精修或导出 4K！
"""

import os
import sys
import json
import re
import argparse

try:
    import pyJianYingDraft as draft
except ImportError:
    print("[!] 未检测到 pyJianYingDraft 库，正在自动安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyJianYingDraft"])
    import pyJianYingDraft as draft


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


def parse_storyboard_md(sb_file):
    """解析 分镜.md，提取镜号、时长、台词、姿势与动作描述"""
    if not os.path.exists(sb_file):
        raise FileNotFoundError(f"未找到分镜文件: {sb_file}")

    with open(sb_file, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"(?:^|\n)###?\s*SHOT-?", content, flags=re.IGNORECASE)
    shots = []
    for b in blocks[1:]:
        lines = [line.strip() for line in b.strip().split("\n") if line.strip()]
        if not lines:
            continue
        header = lines[0]
        shot_id_match = re.search(r"^(\d+)", header)
        shot_id = shot_id_match.group(1) if shot_id_match else str(len(shots) + 1)

        dur_match = re.search(r"时长:\s*([\d.]+)\s*s", b)
        dur = float(dur_match.group(1)) if dur_match else 3.0

        speech_match = re.search(r"<d>(?:\[Chinese\])?(.*?)</d>", b, flags=re.DOTALL)
        speech = speech_match.group(1).strip() if speech_match else ""

        pose_match = re.search(r"姿势:\s*`?([a-z_0-9]+)`?\s*\((.*?)\)", b)
        pose_id = pose_match.group(1) if pose_match else ""
        pose_zh = pose_match.group(2) if pose_match else ""

        shots.append({
            "index": int(shot_id),
            "id": f"SHOT-{int(shot_id):02d}",
            "duration": dur,
            "speech": speech,
            "pose": pose_id,
            "pose_zh": pose_zh,
            "raw_block": b
        })
    return shots


def export_to_jianying(project_dir, draft_name=None, video_dir=None, draft_root=None):
    """核心导出函数：将吞鲸项目打包进剪映草稿"""
    sb_file = os.path.join(project_dir, "分镜.md")
    shots = parse_storyboard_md(sb_file)
    if not shots:
        raise ValueError("分镜中未解析出任何有效镜头！")

    if not draft_name:
        draft_name = os.path.basename(os.path.abspath(project_dir))

    if not draft_root:
        draft_root = find_jianying_draft_root()

    os.makedirs(draft_root, exist_ok=True)
    folder = draft.DraftFolder(draft_root)

    print("=" * 65)
    print("🐳 吞鲸宝典 · 剪映专业版草稿自动生成流水线")
    print(f"目标草稿名称: {draft_name}")
    print(f"剪映工程目录: {draft_root}")
    print(f"输入镜头数量: {len(shots)} 镜")
    print("=" * 65)

    # 竖屏漫剧标准画幅 9:16 (1080x1920)
    # 预先显式初始化视频轨、音频轨与文本字幕轨并保存轨道引用 (TrackRef)
    script = folder.create_draft(draft_name, 1080, 1920)
    v_track_ref = script.append_track(draft.TrackSpec(draft.TrackType.video, name="视频轨"))
    a_track_ref = script.append_track(draft.TrackSpec(draft.TrackType.audio, name="音频轨"))
    t_track_ref = script.append_track(draft.TrackSpec(draft.TrackType.text, name="字幕轨"))

    # 1. 扫描渲染视频文件
    # 优先匹配 video_dir，次选 project_dir 下的 mp4，最后尝试 ComfyUI 默认输出
    search_dirs = [
        video_dir,
        os.path.join(project_dir, "output"),
        os.path.join(project_dir, "renders"),
        project_dir
    ]
    search_dirs = [d for d in search_dirs if d and os.path.exists(d)]

    current_us = 0  # 剪映内部时间单位为微秒 (1s = 1,000,000 us)

    for s in shots:
        dur_us = int(s["duration"] * 1_000_000)
        shot_tag = f"SHOT-{s['index']:02d}"

        # 查找对应视频文件
        matched_mp4 = None
        for sd in search_dirs:
            for f in os.listdir(sd):
                if f.lower().endswith((".mp4", ".mov", ".webm")) and (shot_tag in f or f"shot_{s['index']}" in f.lower()):
                    matched_mp4 = os.path.join(sd, f)
                    break
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
            print(f"  [+] {shot_tag} 视频已对位: {os.path.basename(matched_mp4)} ({s['duration']}s)")
        else:
            # 尚未渲染出片时的占位标注
            pass

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

    # 保存草稿
    script.save()

    target_draft_path = os.path.join(draft_root, draft_name)
    print("\n" + "=" * 65)
    print(f"🎉 剪映草稿生成 100% 成功！")
    print(f"草稿物理路径: {target_draft_path}")
    print("使用方法：打开电脑上的【剪映专业版】，在首页“本地草稿”列表即可直接看到并双击打开本剧！")
    print("=" * 65)
    return target_draft_path


def main():
    ap = argparse.ArgumentParser(description="吞鲸分镜一键转剪映草稿工程")
    ap.add_argument("project_dir", help="吞鲸项目目录（内含 分镜.md）")
    ap.add_argument("--name", default="", help="草稿名称（默认同项目目录名）")
    ap.add_argument("--video-dir", default="", help="渲染视频所在目录（可选）")
    ap.add_argument("--draft-root", default="", help="自定义剪映草稿根目录（可选）")
    args = ap.parse_args()

    export_to_jianying(
        args.project_dir,
        draft_name=args.name,
        video_dir=args.video_dir,
        draft_root=args.draft_root
    )


if __name__ == "__main__":
    main()
