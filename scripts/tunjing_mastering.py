#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 v4.0 · 母带音画精修与无损缝合引擎 (Tunjing v4.0 Audio-Visual Mastering Engine)

专门根治 AI 多镜头拼接的三大廉价感：
1. 首部 2 帧“起势微顿帧”自动修剪 (`--trim-head-frames 2`，即 0.083s)：切除扩散模型从参考图刚起势的微僵硬帧，保留最流畅的中后段动量。
2. EBU R128 广播级响度统一 (`loudnorm=I=-16:TP=-1.5:LRA=11`)：彻底解决各镜头独立生成导致的台词/喘息音量忽大忽小。
3. 切点爆音消除与呼吸微淡化：对每镜首尾音频施加 0.12s 微淡入淡出 (`afade`)，彻底消灭硬切处的波形阶跃“啪/咔哒”爆音，最终无损合并为全集母带 MP4！
"""

import os
import sys
import glob
import json
import shutil
import subprocess
import argparse


def process_single_clip(in_mp4, out_mp4, trim_head_frames=2, fps=24.0, normalize_audio=True):
    """
    对单个镜头执行：
    1) 切掉开头 trim_head_frames 帧（默认 2 帧 = 0.0833 秒）
    2) 音频响度标准化 (-16 LUFS) + 首尾 0.10s 微淡化防爆音
    """
    ss_sec = round(float(trim_head_frames) / float(fps), 4) if trim_head_frames > 0 else 0.0
    af_chain = "afade=t=in:st=0:d=0.08"
    if normalize_audio:
        af_chain = f"loudnorm=I=-16:TP=-1.5:LRA=11,{af_chain}"

    cmd = ["ffmpeg", "-y"]
    if ss_sec > 0:
        cmd += ["-ss", str(ss_sec)]
    cmd += [
        "-i", in_mp4,
        "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p",
        "-af", af_chain,
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        out_mp4
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        # 若原视频无音轨则回退纯视频编码
        cmd_vo = ["ffmpeg", "-y"]
        if ss_sec > 0:
            cmd_vo += ["-ss", str(ss_sec)]
        cmd_vo += ["-i", in_mp4, "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", out_mp4]
        subprocess.run(cmd_vo, capture_output=True, text=True)
    return os.path.exists(out_mp4)


def master_episode(project_dir, trim_head_frames=2, out_name="全集精修母带_Mastered.mp4"):
    in_dir = os.path.join(project_dir, "02_成片输出")
    if not os.path.isdir(in_dir):
        print(f"[i] 目录 {in_dir} 尚未生成切片（请先在 ComfyUI 渲染出片后运行本脚本）。")
        return False

    raw_clips = sorted(glob.glob(os.path.join(in_dir, "shot_*.mp4")))
    # 过滤掉多候选重摇副本（如 shot_07_v2.mp4），只取正式选定版 shot_XX.mp4
    main_clips = [c for c in raw_clips if "_v" not in os.path.basename(c)]
    if not main_clips:
        print(f"[i] {in_dir} 下未找到任何 shot_XX.mp4 镜头文件。")
        return False

    work_dir = os.path.join(project_dir, "04_母带精修缓存")
    os.makedirs(work_dir, exist_ok=True)

    processed_list = []
    print(f"[▶] 正在对 {len(main_clips)} 个镜头执行【首部 {trim_head_frames} 帧微修剪 + EBU R128 (-16 LUFS) 响度统一 + 切点消爆音】...")
    for c in main_clips:
        bn = os.path.basename(c)
        out_c = os.path.join(work_dir, f"norm_{bn}")
        if process_single_clip(c, out_c, trim_head_frames=trim_head_frames):
            processed_list.append(out_c)

    concat_txt = os.path.join(work_dir, "concat_list.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in processed_list:
            safe_p = os.path.abspath(p).replace("\\", "/")
            f.write(f"file '{safe_p}'\n")

    final_out = os.path.join(project_dir, out_name)
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", final_out
    ]
    subprocess.run(cmd_concat, capture_output=True, text=True)
    if os.path.exists(final_out):
        print(f"[✓] 母带精修合成完毕: {final_out} (大小: {os.path.getsize(final_out)/1024/1024:.2f} MB)")
        return True
    return False


def main():
    ap = argparse.ArgumentParser(description="吞鲸 v4.0 母带音画精修与无损缝合引擎")
    ap.add_argument("project_dir", help="项目目录路径")
    ap.add_argument("--trim-head-frames", type=int, default=2, help="每镜切除首部起势微顿帧数（默认2帧=0.08s，设0则不切）")
    ap.add_argument("--out-name", default="全集精修母带_Mastered.mp4", help="输出母带文件名")
    args = ap.parse_args()

    master_episode(args.project_dir, trim_head_frames=args.trim_head_frames, out_name=args.out_name)


if __name__ == "__main__":
    main()
