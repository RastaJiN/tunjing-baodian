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

    # 时长分配：转场桥固定 2.0s，动作镜均摊剩余
    n_tr = sum(1 for s in shots if s["type"] == "transition")
    tr_sec = 2.0 * n_tr
    n_act = len(shots) - n_tr
    remain = max(n_act * 2.0, total_sec - tr_sec)
    per = remain / n_act if n_act else 3.0
    per = max(2.0, min(6.0, per))

    t = 0.0
    for s in shots:
        d = 2.0 if s["type"] == "transition" else per
        s["t0"] = round(t, 1)
        s["t1"] = round(t + d, 1)
        s["dur"] = round(d, 1)
        t += d
    return shots, round(t, 1)


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

    print("=" * 96)
    print("=== 逐镜完整送模提示词（每镜独立一文件，可直接贴进 H3）===")
    print("=" * 96)
    for i, s in enumerate(shots, 1):
        size_desc = SHOT_SIZES[s["size"]]
        cam_desc = CAMS[s["cam"]]
        prompt = single_shot_prompt(
            s, i - 1, len(shots), s["dur"], size_desc, cam_desc,
            lines=lines, idea=idea, scene=scene, pose_names=pose_names,
        )
        print(f"\n{'─' * 96}")
        print(f"### SHOT {i:02d}  {s['dur']}s  ({s['t0']}-{s['t1']}s)  "
              f"{SHOT_SIZES[s['size']]} / {CAMS[s['cam']]} / {s['pose_zh']}")
        print(f"{'─' * 96}")
        print(prompt)


def main():
    ap = argparse.ArgumentParser(description="吞鲸整段床戏拆镜引擎（拆镜 + 逐镜出完整提示词）")
    ap.add_argument("--chain", help="姿势链，逗号分隔")
    ap.add_argument("--total", type=float, default=120.0, help="整段总时长秒（默认120）")
    ap.add_argument("--lines", default="", help="本段台词")
    ap.add_argument("--idea", default="", help="用户介绍/剧情描述")
    ap.add_argument("--scene", default="卧室", help="场景名")
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
    print_table(shots, actual, args.total, lines=args.lines, idea=args.idea,
                scene=args.scene, pose_names=pose_names,
                emit_prompts=not args.table_only)


if __name__ == "__main__":
    main()
