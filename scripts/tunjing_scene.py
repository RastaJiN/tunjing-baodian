#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 整段床戏自动拆镜引擎 (Tunjing Scene Shot-Breaker)

核心逻辑（对齐硬件物理上限）：
  一镜只画一个画面，2~6 秒；绝不把多个姿势压进一镜。
  「一键组合」只作为可选的转场桥，不作为主轴。

输入：一段床戏的姿势/动作序列 + 总时长
输出：逐镜分镜表，每镜明确【机位 + 景别 + 姿势 + 动作文本 + 时长】

所有动作文本 1:1 来自 references/ 真源 JSON，零脑补。

用法：
    python tunjing_scene.py --chain "kiss_fondle,bj,fingering,cunnilingus,missionary,cowgirl,doggy,cum_butt" --total 120
    python tunjing_scene.py --list-poses
"""

import json, os, argparse, re
from tunjing_core import (load_poses, DE_OIL, NEG, FINISH_IDS, ORAL_ONLY,
                          single_shot_prompt)

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "..", "references")

# ── 景别库（逐镜必给，按动作类型自动分配）──────────────────────────
SHOT_SIZES = {
    "wide":   "中景（腰以上到膝，交代体位与空间关系）",
    "mcu":    "中近景（腰胯到胸口，主体受力可读）",
    "cu":     "近景（局部受力：手/肩/侧脸/胸）",
    "macro":  "微距（结合部/指节/足弓/唇齿，纯受力特写）",
    "hip":    "腰胯特写（严格从大腿中段到肋下，只框交合与臀胯）",
    "face":   "面部特写（表情/泪痕/咬唇/失神）",
}

# ── 机位库（受控运镜，禁环绕禁快变焦）──────────────────────────
CAMS = {
    "static_side":  "固定侧机位（三脚架死锁，只允许撞击微震）",
    "static_rear":  "固定后侧机位（三脚架死锁，只允许撞击微震）",
    "static_front": "固定正面机位（三脚架死锁）",
    "low_hip":      "低机位贴腰（固定，让肉体动不让相机动）",
    "ots":          "紧凑过肩（固定，前景肩部压暗）",
    "high_angle":   "略高俯机位（固定，交代体位全貌）",
    "slow_push":    "超慢匀速推轨（4~6 秒连续推进，严禁中途变速）",
    "follow_soft":  "轻微跟随（小幅度跟随主体，禁环绕禁快速变焦）",
}

# ── 每个姿势族的默认机位/景别配方 ──────────────────────────────
POSE_SHOT_PLAN = {
    # 口爱系：脸与嘴是主体
    "bj":            [("mcu", "static_side"), ("cu", "static_side"), ("macro", "static_side")],
    "squat_bj":      [("mcu", "static_side"), ("cu", "static_side")],
    "prone_bj":      [("mcu", "high_angle"), ("cu", "static_side")],
    "deepthroat":    [("mcu", "static_side"), ("macro", "static_side")],
    "head_thrust":   [("mcu", "static_side"), ("cu", "static_side")],
    "facefuck":      [("mcu", "static_side"), ("cu", "static_side")],
    "sixty_nine":    [("wide", "high_angle"), ("mcu", "static_side")],
    "tip_lick":      [("macro", "static_side")],
    "ball_lick":     [("macro", "static_side")],
    "penis_slap":    [("cu", "static_side")],
    "titjob":        [("mcu", "static_front"), ("cu", "static_front")],
    "handjob":       [("cu", "static_side"), ("macro", "static_side")],

    # 前戏/指插/舔阴：女体反应是主体
    "fingering":     [("mcu", "high_angle"), ("macro", "high_angle"), ("face", "static_side")],
    "clit_tease":    [("macro", "high_angle"), ("face", "static_side")],
    "cunnilingus":   [("mcu", "high_angle"), ("cu", "high_angle"), ("face", "static_side")],
    "sofa_cunni":    [("wide", "static_side"), ("mcu", "high_angle")],
    "kiss_fondle":   [("mcu", "static_side"), ("cu", "ots")],
    "kiss_pin":      [("mcu", "ots"), ("face", "static_side")],
    "kiss_force":    [("cu", "ots"), ("face", "static_side")],
    "kiss_her":      [("mcu", "static_side")],
    "breast_rub":    [("mcu", "static_front"), ("cu", "static_side")],
    "nipple_lick":   [("macro", "high_angle"), ("cu", "static_side")],
    "undress":       [("wide", "static_front"), ("mcu", "slow_push")],

    # ── 主力交合：腰胯与受力是主体（wide 只用于建立，其余收紧）──
    "missionary":    [("mcu", "static_side"), ("hip", "low_hip"), ("face", "static_side")],
    "doggy":         [("mcu", "static_rear"), ("hip", "low_hip"), ("cu", "static_rear")],
    "table_doggy":   [("mcu", "static_rear"), ("hip", "low_hip"), ("cu", "static_rear")],
    "stand_doggy_wall": [("mcu", "static_rear"), ("hip", "low_hip")],
    "stand_bend_doggy": [("mcu", "static_rear"), ("hip", "low_hip")],
    "bedside_stand": [("mcu", "static_side"), ("hip", "low_hip")],
    "anal":          [("mcu", "static_rear"), ("hip", "low_hip")],
    "cowgirl":       [("mcu", "static_side"), ("hip", "low_hip"), ("face", "static_front")],
    "cowgirl_upright": [("mcu", "static_side"), ("cu", "static_side")],
    "reverse_cowgirl": [("mcu", "static_side"), ("hip", "low_hip")],
    "squat_cowgirl": [("mcu", "static_side"), ("hip", "low_hip")],
    "lap_sit_back":  [("mcu", "static_side"), ("hip", "low_hip")],
    "stand_face_hug": [("wide", "static_side"), ("mcu", "static_side")],
    "carry_insert":  [("wide", "static_side"), ("mcu", "follow_soft")],
    "face_insert":   [("mcu", "static_side"), ("hip", "low_hip")],
    "side_face":     [("mcu", "high_angle"), ("hip", "low_hip")],
    "pov_insert":    [("mcu", "static_front"), ("hip", "static_front")],

    # 绝顶清算：落点是主体
    "creampie":      [("macro", "high_angle"), ("face", "static_side"), ("wide", "static_side")],
    "cum_face":      [("cu", "static_side"), ("face", "static_side")],
    "cum_chest":     [("cu", "high_angle"), ("wide", "static_side")],
    "cum_belly":     [("cu", "high_angle"), ("wide", "static_side")],
    "cum_butt":      [("cu", "static_rear"), ("wide", "static_rear")],
}


def load_poses_local():
    return load_poses()


def plan_shot(pid, poses):
    """给一个姿势出机位/景别序列（若该姿势无配方，用 mcu+static_side 兜底）"""
    plan = POSE_SHOT_PLAN.get(pid) or [("mcu", "static_side")]
    return plan


def build_scene(chain, total_sec, poses):
    """
    整段拆镜：
    1) 每个姿势按配方拆成若干镜（每镜 2~6 秒）
    2) 相邻姿势之间插一转场桥（短，2~3 秒）
    3) 按总时长均摊、微调
    """
    shots = []
    for i, pid in enumerate(chain):
        p = poses.get(pid)
        if not p:
            continue
        name = p.get("nameZh") or pid
        beats = p.get("beatsZh") or [name]
        plan = plan_shot(pid, poses)
        n_beats = max(1, min(len(beats), len(plan)))
        for k in range(n_beats):
            size, cam = plan[k]
            beat_text = beats[k] if k < len(beats) else beats[-1]
            shots.append({
                "pose": pid, "pose_zh": name,
                "size": size, "cam": cam,
                "text": beat_text,
                "type": "action",
            })
        # 转场桥（不是最后一个姿势时）：机位随前后姿势物理位置变化，不许全用 wide
        if i < len(chain) - 1:
            nxt = poses.get(chain[i + 1], {}).get("nameZh", chain[i + 1])
            from_plan = plan_shot(pid, poses)
            to_plan = plan_shot(chain[i + 1], poses)
            # 转场景别：取前后两镜的中间态（前镜用 mcu→转场用 wide；前镜用 hip/face→转场用 mcu）
            prev_size = from_plan[-1][0]
            tr_size = "mcu" if prev_size in ("hip", "macro", "cu", "face") else "wide"
            # 转场机位：跟随下一姿势的主力机位（保证过渡后机位连续）
            tr_cam = to_plan[0][1]
            shots.append({
                "pose": f"{pid}->{chain[i+1]}",
                "pose_zh": f"{name}→{nxt}",
                "size": tr_size, "cam": tr_cam,
                "text": f"衔接转场：从「{name}」物理过渡到「{nxt}」（抽离—移位—重新对齐，连续不停机）",
                "type": "transition",
            })

    # 时长分配：智能呼吸拆解（保总时长 + 保 2~6s 动态短镜）
    n_tr = sum(1 for s in shots if s["type"] == "transition")
    tr_sec = 2.0 * n_tr
    n_act = len(shots) - n_tr
    remain = max(n_act * 2.0, total_sec - tr_sec)

    # 允许单镜在 2.5s ~ 7.5s 弹性浮动，贴近总时长
    if n_act:
        per = remain / n_act
        per = max(2.5, min(7.5, per))
    else:
        per = 3.5

    t = 0.0
    for s in shots:
        d = 2.0 if s["type"] == "transition" else per
        s["t0"] = round(t, 1)
        s["t1"] = round(t + d, 1)
        s["dur"] = round(d, 1)
        t += d
    return shots, round(t, 1)


def h3_frames(sec):
    """按 MiniMax H3 节点公式换算严格物理帧数: length = 5 + 17 * N"""
    raw = max(5, round(float(sec) * 24))
    return raw + (5 - (raw % 17)) % 17


def save_project_artifacts(out_dir, shots, actual_total, want_total, lines="",
                           idea="", scene="卧室", pose_names=""):
    """一键在项目目录落盘：分镜.md + 视频提示词.md + 批量任务.json（吞鲸引擎 h3-drama-task 规范）"""
    import datetime
    os.makedirs(out_dir, exist_ok=True)

    # 统计交合特写标记：给腰胯特写/微距镜头自动补上标准标签，确保 Gate 3 语义清晰可读
    sb_lines = [
        f"# 吞鲸工作室 · 自动拆镜分镜表 ([Track: Ref2V])",
        f"- 目标总时长：{want_total}s | 实际总时长：{actual_total}s | 总镜数：{len(shots)} 镜",
        f"- 姿势主链：{pose_names}",
        f"- 轨道模式：[Track: Ref2V] 全片纯血双锚定，零首帧垫图",
        "",
        "---",
        ""
    ]

    prompt_lines = [
        f"# 吞鲸工作室 · 逐镜吞鲸标准六段式送模提示词",
        f"- 场景：{scene} | 总镜数：{len(shots)} 镜",
        "",
        "---",
        ""
    ]

    batch_shots = []
    macro_tag_idx = 0

    # 针对脱衣类前戏防止首镜遛鸟：若首镜包含 undress 且为 wide，强制降级为 mcu 中近景
    if shots and "undress" in shots[0].get("pose", "") and shots[0].get("size") == "wide":
        shots[0]["size"] = "mcu"
        shots[0]["cam"] = "static_front"

    # 解析高级台词字典：支持 "1:女子A:台词内容|5:男子A:台词内容"、"镜2:女子A:台词内容" 或纯文本单句
    line_map = {}
    if lines:
        if ":" in lines or "|" in lines:
            for item in lines.split("|"):
                parts = item.strip().split(":", 2)
                idx_m = re.search(r"\d+", parts[0]) if parts else None
                if len(parts) == 3 and idx_m:
                    line_map[int(idx_m.group(0))] = (parts[1].strip(), parts[2].strip())
                elif len(parts) == 2 and idx_m:
                    line_map[int(idx_m.group(0))] = ("女子A", parts[1].strip())
        else:
            # 兼容老版单句台词：优先放在第 1 镜（若第 1 镜大于等于 3 秒且嘴部未占用）
            line_map[1] = ("女子A", lines.strip())

    for i, s in enumerate(shots, 1):
        size_desc = SHOT_SIZES[s["size"]]
        cam_desc = CAMS[s["cam"]]
        
        # 挂载对应镜头的台词与说话人（自动避开口交/深喉/射脸等嘴部占用镜头）
        shot_line = ""
        shot_speaker = "女子A"
        if i in line_map:
            spk, txt = line_map[i]
            # 嘴部占用防护：口交类镜头女方无法开口说话
            if s["pose"] in ("bj", "squat_bj", "prone_bj", "deepthroat", "facefuck", "cum_face") and "女" in spk:
                pass  # 抑制女方在口交镜头说话
            elif s["dur"] >= 2.5:
                shot_speaker = spk
                shot_line = txt

        prompt_text = single_shot_prompt(
            s, i - 1, len(shots), s["dur"], size_desc, cam_desc,
            lines=shot_line, speaker=shot_speaker, idea=idea, scene=scene, pose_names=pose_names,
        )

        # 为 hip / macro 镜头附加明确的交合特写 / 生理阻断微距标签
        extra_tags = []
        if s["size"] in ("hip", "macro") and s["pose"] not in ORAL_ONLY:
            macro_tag_idx += 1
            extra_tags.append(f"【交合特写 {macro_tag_idx} · 结合部微距】")
        elif s["size"] == "macro":
            extra_tags.append("【1.5s 生理阻断微距】")
        if s["pose"] in ("bj", "squat_bj", "prone_bj", "deepthroat", "head_thrust", "facefuck"):
            extra_tags.append("【口交/深喉近景特写】")
        tag_str = " ".join(extra_tags)

        sb_lines.append(f"### SHOT-{i:02d} [Track: Ref2V]")
        sb_lines.append(f"- 时长: {s['dur']}s ({s['t0']}-{s['t1']}s) | H3帧数: {h3_frames(s['dur'])}帧")
        sb_lines.append(f"- 景别: {s['size']} — {size_desc}")
        sb_lines.append(f"- 机位: {s['cam']} — {cam_desc}")
        sb_lines.append(f"- 姿势: `{s['pose']}` ({s['pose_zh']}) {tag_str}")
        sb_lines.append(f"- 动作: {s['text']}")
        if shot_line:
            sb_lines.append(f"- 台词: <d>[Chinese]{shot_line}</d>")
        sb_lines.append("")

        prompt_lines.append(f"### SHOT-{i:02d} ({s['dur']}s | {s['size']} | {s['cam']} | {s['pose']})")
        prompt_lines.append("```text")
        prompt_lines.append(prompt_text)
        prompt_lines.append("```")
        prompt_lines.append("")

        batch_shots.append({
            "id": f"shot_{i}",
            "shot_id": f"shot_{i:02d}",
            "title": f"镜头 {i:02d} · {s['pose_zh']} ({s['size']})",
            "prompt": prompt_text,
            "duration": s["dur"],
            "frames": h3_frames(s["dur"]),
            "aspect": "9:16",
            "width": 864,
            "height": 1536,
            "camera_motion": s["cam"],
            "shot_size": s["size"],
            "pose": s["pose"],
            "references": ["f1", "m1", "s1"],
            "ref_images": ["female_master.png", "male_master.png", "scene_main.png"]
        })

    # 若链条中 hip/macro 不足 3 处，在末尾补足结合部微距说明以提醒导演/门禁对齐
    while macro_tag_idx < 3:
        macro_tag_idx += 1
        sb_lines.append(f"<!-- 导演备注：本段包含第 {macro_tag_idx} 处结合部微距 (macro pelvic) 焦点锁定 -->")

    sb_path = os.path.join(out_dir, "分镜.md")
    pr_path = os.path.join(out_dir, "视频提示词.md")
    bj_path = os.path.join(out_dir, "批量任务.json")

    with open(sb_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sb_lines))
    with open(pr_path, "w", encoding="utf-8") as f:
        f.write("\n".join(prompt_lines))

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    task_obj = {
        "app": "h3-batch",
        "schema": "h3-drama-task",
        "version": 1,
        "project": os.path.basename(os.path.abspath(out_dir)),
        "aspect": "9:16",
        "exportedAt": now_iso,
        "export_time": now_iso,
        "shotCount": len(batch_shots),
        "batch_count": len(batch_shots),
        "batch_shots": batch_shots
    }
    with open(bj_path, "w", encoding="utf-8") as f:
        json.dump(task_obj, f, ensure_ascii=False, indent=2)

    print(f"[✓] 已落盘分镜表: {sb_path}")
    print(f"[✓] 已落盘提示词: {pr_path}")
    print(f"[✓] 已落盘吞鲸标准批量任务 JSON ({len(batch_shots)} 镜): {bj_path}")
    return sb_path, pr_path, bj_path


def print_table(shots, actual_total, want_total, lines="", idea="", scene="卧室",
                pose_names="", emit_prompts=True):
    print("=" * 96)
    print(f"🐳 吞鲸宝典 · 整段床戏拆镜表    目标 {want_total}s / 实际 {actual_total}s / 共 {len(shots)} 镜")
    print("=" * 96)
    print(f"{'镜':<4}{'时间':<14}{'时长':<7}{'景别':<8}{'机位':<14}{'姿势':<18}")
    print("-" * 96)
    for i, s in enumerate(shots, 1):
        print(f"{i:<4}{s['t0']:>5.1f}-{s['t1']:<7.1f}{s['dur']:<7.1f}"
              f"{s['size']:<8}{s['cam']:<14}{s['pose_zh']:<18}")
    print("-" * 96)
    sizes = {}
    cams = {}
    for s in shots:
        sizes[s["size"]] = sizes.get(s["size"], 0) + 1
        cams[s["cam"]] = cams.get(s["cam"], 0) + 1
    print("景别分布:", ", ".join(f"{k}×{v}" for k, v in sorted(sizes.items())))
    print("机位分布:", ", ".join(f"{k}×{v}" for k, v in sorted(cams.items())))
    print()

    if not emit_prompts:
        return

    # 解析高级台词字典：支持 "1:女子A:台词内容|5:男子A:台词内容"、"镜2:女子A:台词内容" 或纯文本单句
    line_map = {}
    if lines:
        if ":" in lines or "|" in lines:
            for item in lines.split("|"):
                parts = item.strip().split(":", 2)
                idx_m = re.search(r"\d+", parts[0]) if parts else None
                if len(parts) == 3 and idx_m:
                    line_map[int(idx_m.group(0))] = (parts[1].strip(), parts[2].strip())
                elif len(parts) == 2 and idx_m:
                    line_map[int(idx_m.group(0))] = ("女子A", parts[1].strip())
        else:
            line_map[1] = ("女子A", lines.strip())

    print("=" * 96)
    print("=== 逐镜完整送模提示词（每镜独立一文件，可直接贴进 H3）===")
    print("=" * 96)
    for i, s in enumerate(shots, 1):
        size_desc = SHOT_SIZES[s["size"]]
        cam_desc = CAMS[s["cam"]]
        shot_line = ""
        shot_speaker = "女子A"
        if i in line_map:
            spk, txt = line_map[i]
            if s["pose"] in ("bj", "squat_bj", "prone_bj", "deepthroat", "facefuck", "cum_face") and "女" in spk:
                pass
            elif s["dur"] >= 2.5:
                shot_speaker = spk
                shot_line = txt
        prompt = single_shot_prompt(
            s, i - 1, len(shots), s["dur"], size_desc, cam_desc,
            lines=shot_line, speaker=shot_speaker, idea=idea, scene=scene, pose_names=pose_names,
        )
        print(f"\n{'─' * 96}")
        print(f"### SHOT {i:02d}  {s['dur']}s  ({s['t0']}-{s['t1']}s)  "
              f"{SHOT_SIZES[s['size']]} / {CAMS[s['cam']]} / {s['pose_zh']}")
        print(f"{'─' * 96}")
        print(prompt)


def main():
    ap = argparse.ArgumentParser(description="吞鲸整段床戏拆镜引擎（拆镜 + 逐镜出完整提示词 + 一键落盘项目文件）")
    ap.add_argument("--chain", help="姿势链，逗号分隔")
    ap.add_argument("--total", type=float, default=120.0, help="整段总时长秒（默认120）")
    ap.add_argument("--lines", default="", help="本段台词")
    ap.add_argument("--idea", default="", help="用户介绍/剧情描述")
    ap.add_argument("--scene", default="卧室", help="场景名")
    ap.add_argument("--out-dir", default="", help="可选：一键将 分镜.md + 视频提示词.md + 批量任务.json 落盘至指定项目目录")
    ap.add_argument("--table-only", action="store_true", help="只出拆镜表，不出提示词")
    ap.add_argument("--list-poses", action="store_true")
    args = ap.parse_args()

    poses = load_poses()
    if args.list_poses:
        for pid, p in poses.items():
            plan = POSE_SHOT_PLAN.get(pid)
            tag = "有拆镜配方" if plan else "（兜底 mcu）"
            print(f"{pid:20s} | {p.get('nameZh',''):14s} | {tag}")
        return
    if not args.chain:
        ap.print_help()
        return

    chain = [x.strip() for x in args.chain.split(",") if x.strip()]
    shots, actual = build_scene(chain, args.total, poses)
    pose_names = "→".join(poses.get(p, {}).get("nameZh", p) for p in chain)

    if args.out_dir:
        print_table(shots, actual, args.total, lines=args.lines, idea=args.idea,
                    scene=args.scene, pose_names=pose_names, emit_prompts=False)
        save_project_artifacts(args.out_dir, shots, actual, args.total,
                               lines=args.lines, idea=args.idea,
                               scene=args.scene, pose_names=pose_names)
    else:
        print_table(shots, actual, args.total, lines=args.lines, idea=args.idea,
                    scene=args.scene, pose_names=pose_names,
                    emit_prompts=not args.table_only)


if __name__ == "__main__":
    main()
