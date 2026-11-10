#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 单镜多节拍精修引擎 (Tunjing Single-Shot Beat Refiner)

与 tunjing_scene.py（整段 120s 拆成 20~30 个独立短镜的主引擎）互补：
本脚本用于在需要把 2~3 个连续动作压进同一个 8~12s 镜头内部（一镜到底微节拍）时使用。
所有底层常量、头部/尾部装配、场地承托面改写 (with_scene_surface) 100% 调用 tunjing_core，零重复定义！
"""

import argparse
import re
from tunjing_core import (
    load_poses,
    load_recipes,
    FINISH_IDS,
    ORAL_ONLY,
    header_block,
    footer_block,
    insert_hint,
    with_scene_surface,
)

FAMILY = {
    "bj": "kneel_oral", "squat_bj": "kneel_oral", "prone_bj": "kneel_oral",
    "deepthroat": "kneel_oral", "head_thrust": "kneel_oral", "facefuck": "kneel_oral",
    "sixty_nine": "kneel_oral", "tip_lick": "kneel_oral", "ball_lick": "kneel_oral",
    "penis_slap": "kneel_oral", "titjob": "kneel_oral", "handjob": "side_manual",
    "missionary": "supine", "cunnilingus": "supine", "sofa_cunni": "supine",
    "fingering": "supine", "clit_tease": "supine",
    "doggy": "rear_kneel", "table_doggy": "rear_kneel", "anal": "rear_kneel",
    "stand_doggy_wall": "stand_rear", "stand_bend_doggy": "stand_rear",
    "bedside_stand": "stand_rear",
    "cowgirl": "cowgirl", "cowgirl_upright": "cowgirl", "reverse_cowgirl": "cowgirl",
    "squat_cowgirl": "cowgirl", "lap_sit_back": "cowgirl",
    "stand_face_hug": "stand_face", "carry_insert": "stand_face", "face_insert": "stand_face",
    "side_face": "side", "creampie": "finish", "cum_face": "finish",
    "cum_chest": "finish", "cum_belly": "finish", "cum_butt": "finish",
}


def order_physically(seq):
    main = [p for p in seq if p not in FINISH_IDS]
    fin = [p for p in seq if p in FINISH_IDS]
    return main + fin


def find_transition(recipes, a, b):
    key = f"{a}->{b}"
    if key in recipes:
        return recipes[key], key
    fam = f"{FAMILY.get(a, a)}->{FAMILY.get(b, b)}"
    if fam in recipes:
        return recipes[fam], fam
    if b in FINISH_IDS:
        for cand in (f"{FAMILY.get(a, a)}->finish", f"{a}->finish"):
            if cand in recipes:
                return recipes[cand], cand
    return None, None


def expand_poses(seq, poses, recipes):
    seq = order_physically(seq)
    actions = []
    for i, pid in enumerate(seq):
        p = poses.get(pid)
        if not p:
            continue
        name = p.get("nameEn") or pid
        beats = p.get("beatsEn") or []
        b0 = beats[0] if len(beats) > 0 else name
        b1 = beats[1] if len(beats) > 1 else None
        b2 = beats[2] if len(beats) > 2 else None

        actions.append({"kind": "establish", "pose": pid, "text": b0})
        if b1:
            actions.append({"kind": "push", "pose": pid, "text": b1})
        if i < len(seq) - 1:
            nxt = poses.get(seq[i + 1], {}).get("nameEn", seq[i + 1])
            actions.append({
                "kind": "transition",
                "pose": f"{pid}->{seq[i+1]}",
                "recipe": f"{pid}->{seq[i+1]}",
                "text": f"Continuous physical transition from {name} into {nxt}, shifting center of gravity smoothly over two seconds"
            })
        elif b2:
            actions.append({"kind": "finish", "pose": pid, "text": b2})
    return actions


def is_finish_segment(act):
    t = act["text"]
    if act["kind"] == "transition":
        return bool(re.search(r"射在|内射|自撸|猛地.*拔出|快速滑出|对准臀|对准脸|对准小腹|cum_|颜射|扶根对准", t))
    return bool(re.search(r"射在|内射|边撸边射|自撸|pull-out|快速滑出|髋部猛|直接射精|不撸管", t))


def shot_time_bounds(dur, n, actions):
    dur = max(2.0, float(dur))
    if n < 2:
        return [{"t0": 0.0, "t1": dur}]
    first = next((i for i, a in enumerate(actions) if is_finish_segment(a)), -1)
    if first <= 0:
        beat = dur / n
        return [{"t0": round(i * beat, 1), "t1": dur if i == n - 1 else round((i + 1) * beat, 1)} for i in range(n)]
    finish_sec = 4.0 if dur >= 12 else min(4.0, max(2.5, round(dur * 0.3, 1)))
    main_n, fin_n = first, n - first
    main_dur = max(1.0, round(dur - finish_sec, 1))
    fin_dur = round(dur - main_dur, 1)
    bounds = [{"t0": round(i * main_dur / main_n, 1), "t1": round((i + 1) * main_dur / main_n, 1)} for i in range(main_n)]
    for i in range(fin_n):
        t0 = round(main_dur + i * fin_dur / fin_n, 1)
        t1 = dur if i == fin_n - 1 else round(main_dur + (i + 1) * fin_dur / fin_n, 1)
        bounds.append({"t0": t0, "t1": t1})
    return bounds


def build_prompt(seq, dur=10.0, aspect="9:16", lines="", idea="", scene="当前场景"):
    poses, recipes = load_poses(), load_recipes()
    actions = expand_poses(seq, poses, recipes)
    n = min(6, max(3, len(actions)))
    if len(actions) > n:
        merged = []
        i = 0
        while i < len(actions):
            cur = actions[i]
            nxt = actions[i + 1] if i + 1 < len(actions) else None
            if nxt and cur["kind"] == "establish" and nxt["kind"] == "push" and cur.get("pose") == nxt.get("pose"):
                merged.append({"kind": "establish", "pose": cur["pose"], "text": cur["text"] + "；" + nxt["text"]})
                i += 2
                continue
            merged.append(cur)
            i += 1
        actions = merged
        while len(actions) > n:
            idx = next((k for k, a in enumerate(actions) if a["kind"] == "transition" and 0 < k < len(actions) - 1), None)
            if idx is None:
                break
            actions[idx - 1]["text"] += "；" + actions[idx]["text"]
            actions.pop(idx)
    while len(actions) < n:
        actions.append(actions[-1])
    actions = actions[:n]
    bounds = shot_time_bounds(dur, n, actions)

    pose_names = "→".join(poses.get(p, {}).get("nameZh", p) for p in order_physically(seq))
    parts = header_block(dur, aspect, idea=idea, scene=scene, pose_names=pose_names)
    parts.append("integrated_multimodal_description:")

    spoken = False
    for i, (act, bd) in enumerate(zip(actions, bounds)):
        head = "[Shot 1] Live-action cinematic, medium close-up, camera locked static on a heavy tripod;" if i == 0 else f"[Shot {i+1}] At {bd['t0']:.2f}s, the shot transitions to medium close-up, camera locked static on a heavy tripod;"
        body = with_scene_surface(act["text"], scene)
        if i == 0:
            body = body + insert_hint(act.get("pose", ""))
        if lines and not spoken and i in (0, n // 2, n - 1):
            body += f" <Subject 1> (S1) says: <d>[Chinese]{lines}</d> while <Subject 2> (S2) keeps his lips completely closed."
            spoken = True
        if i == n - 1:
            body += f" Final state: Unbroken anatomical continuity and stable composition held steady to {dur:.2f}s."
        parts.append(f"{head} {body}")
        parts.append("")

    parts.extend(footer_block(scene))
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description="吞鲸单镜多节拍精修引擎")
    ap.add_argument("--shot", help="单镜内姿势链，逗号分隔，如 cowgirl,doggy")
    ap.add_argument("--dur", type=float, default=10.0, help="单镜时长秒")
    ap.add_argument("--lines", default="", help="台词")
    ap.add_argument("--idea", default="", help="剧情描述")
    ap.add_argument("--scene", default="当前场景", help="场景名（自动适配承托面与声场）")
    ap.add_argument("--list-poses", action="store_true")
    ap.add_argument("--list-trans", action="store_true")
    args = ap.parse_args()

    poses, recipes = load_poses(), load_recipes()
    if args.list_poses:
        for pid, p in poses.items():
            print(f"{pid:20s} | {p.get('nameZh','')}")
        return
    if args.list_trans:
        for k in recipes:
            print(k)
        return
    if not args.shot:
        ap.print_help()
        return
    seq = [s.strip() for s in args.shot.split(",") if s.strip()]
    print(build_prompt(seq, args.dur, lines=args.lines, idea=args.idea, scene=args.scene))


if __name__ == "__main__":
    main()
