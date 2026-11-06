#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 分镜→提示词 自动装配引擎 (Tunjing Storyboard Compiler)

复刻桌面《大人的工作台》真实链路：
  orderPosesPhysically → expandPosesWithTransitions → buildShotTimeBounds → buildOfficialH3Prompt

用途：分镜写完后，把每个镜头的姿势链丢进来，自动吐出工作台同款提示词。
所有动作文本 1:1 来自 references/ 下的三个真源 JSON，零脑补。

用法：
    python tunjing_storyboard.py --shot "cowgirl,doggy" --dur 10 --lines "嗯…啊…"
    python tunjing_storyboard.py --episode 分镜.md          # 批量跑整集
    python tunjing_storyboard.py --list-poses / --list-trans
"""

import json, os, sys, argparse, re

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "..", "references")

FINISH_IDS = {"creampie", "cum_face", "cum_chest", "cum_belly", "cum_butt"}

# 姿态族（用于转场配方 fallback，取工作台 poseFamily 的近似）
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


def load():
    with open(os.path.join(REF, "workbench_poses_matrix.json"), encoding="utf-8") as f:
        poses = json.load(f)
    with open(os.path.join(REF, "transition_recipes.json"), encoding="utf-8") as f:
        recipes = json.load(f)
    return poses, recipes


def order_physically(seq):
    """复刻 orderPosesPhysically：finish 类永远排到最后"""
    main = [p for p in seq if p not in FINISH_IDS]
    fin = [p for p in seq if p in FINISH_IDS]
    return main + fin


def find_transition(recipes, a, b):
    """复刻 buildPoseTransition 的 key → famKey 查表"""
    key = f"{a}->{b}"
    if key in recipes:
        return recipes[key], key
    fam = f"{FAMILY.get(a, a)}->{FAMILY.get(b, b)}"
    if fam in recipes:
        return recipes[fam], fam
    # 退到 finish 通配
    if b in FINISH_IDS:
        for cand in (f"{FAMILY.get(a,a)}->finish", f"{a}->finish"):
            if cand in recipes:
                return recipes[cand], cand
    return None, None


def expand_poses(seq, poses, recipes):
    """复刻 expandPosesWithTransitions：每姿势展开建立/推进/衔接转场/收束"""
    seq = order_physically(seq)
    actions = []
    for i, pid in enumerate(seq):
        p = poses.get(pid)
        if not p:
            continue
        name = p.get("nameZh") or pid
        beats = p.get("beatsZh") or []
        b0 = beats[0] if len(beats) > 0 else name
        b1 = beats[1] if len(beats) > 1 else None
        b2 = beats[2] if len(beats) > 2 else None

        actions.append({"kind": "establish", "pose": pid,
                        "text": f"（{name}·建立）{b0}"})
        if b1:
            actions.append({"kind": "push", "pose": pid,
                            "text": f"（{name}·推进）{b1}。手腿腰同前。"})
        if i < len(seq) - 1:
            tr, key = find_transition(recipes, pid, seq[i + 1])
            if tr:
                actions.append({"kind": "transition", "pose": f"{pid}->{seq[i+1]}",
                                "recipe": key, "text": f"（衔接转场）{tr}"})
            else:
                nxt = poses.get(seq[i + 1], {}).get("nameZh", seq[i + 1])
                actions.append({"kind": "transition", "pose": f"{pid}->{seq[i+1]}",
                                "recipe": None,
                                "text": f"（衔接转场·无内置配方，需人工补写）从「{name}」物理过渡到「{nxt}」"})
        elif b2:
            actions.append({"kind": "finish", "pose": pid,
                            "text": f"（{name}·收束）{b2}。手腿腰同前。"})
    return actions


def is_finish_segment(act):
    """复刻 actionIsFinishSegment"""
    t = act["text"]
    if act["kind"] == "transition":
        return bool(re.search(r"射在|内射|自撸|猛地.*拔出|快速滑出|对准臀|对准脸|对准小腹|cum_|颜射|扶根对准", t))
    return bool(re.search(r"射在|内射|边撸边射|自撸|pull-out|快速滑出|髋部猛|直接射精|不撸管", t))


def shot_time_bounds(dur, n, actions):
    """复刻 buildShotTimeBounds：射精段压到片尾约4秒"""
    dur = max(2, float(dur))
    if n < 2:
        return [{"t0": 0.0, "t1": dur}]
    first = -1
    for i, a in enumerate(actions):
        if is_finish_segment(a):
            first = i
            break
    if first <= 0:
        beat = dur / n
        return [{"t0": round(i * beat, 1),
                 "t1": dur if i == n - 1 else round((i + 1) * beat, 1)} for i in range(n)]

    finish_sec = 4 if dur >= 12 else min(4, max(2.5, round(dur * 0.3, 1)))
    main_n, fin_n = first, n - first
    main_dur = max(1, round(dur - finish_sec, 1))
    fin_dur = round(dur - main_dur, 1)
    bounds = []
    for i in range(main_n):
        bounds.append({"t0": round(i * main_dur / main_n, 1),
                       "t1": round((i + 1) * main_dur / main_n, 1)})
    for i in range(fin_n):
        t0 = round(main_dur + i * fin_dur / fin_n, 1)
        t1 = dur if i == fin_n - 1 else round(main_dur + (i + 1) * fin_dur / fin_n, 1)
        bounds.append({"t0": t0, "t1": t1})
    return bounds


DE_OIL = ("authentic matte velvet skin finish, powdered dry texture, natural human skin with "
          "visible fine pores and subtle imperfections, soft subsurface scattering without "
          "surface reflection, non-greasy complexion, heavily diffused soft ambient light, "
          "zero hard directional light, 35mm film grain, photorealistic anatomy")

NEG = """No subtitles, captions, watermarks, UI, logos, or on-screen text
No face swap or identity drift; keep the same faces and bodies throughout
No deformed limbs, extra fingers, melting bodies, fused genitals, or ghosting
Only one mouth speaks in any given second
No ripped-off, torn-off, or detached penis; the penis stays attached to the man's body at the root
No genital amputation, floating disembodied shaft, or cock torn away from the pelvis
No orbiting camera, multi-cam cuts, fast zoom, or chaotic reframing
No voice-over, narration, or reading of constraints aloud
Never speak stage directions, pose labels, intensity tags, or phrases like 姿势重点/男人主动/女人主动/逻辑上/勿朗读
Only character dialogue inside <d> tags may be spoken; otherwise only moans or breath; never read the prompt
No cartoon drift, messy background, or focus collapse
No stiff, robotic, or frozen motion; bodies move with inertia, follow-through, and visible breathing
No pose popping or teleporting limbs between beats; motion continues seamlessly through cuts"""


ORAL_ONLY = {"bj", "squat_bj", "prone_bj", "deepthroat", "head_thrust", "facefuck",
             "sixty_nine", "cunnilingus", "sofa_cunni", "fingering", "clit_tease",
             "tip_lick", "ball_lick", "penis_slap", "handjob", "titjob"}


def build_prompt(seq, dur=10.0, aspect="9:16", lines=None, idea="", scene="卧室"):
    """完整装配一个镜头的 H3 提示词"""
    poses, recipes = load()
    actions = expand_poses(seq, poses, recipes)
    # 镜头数：复刻工作台真实策略 —— 不超6镜；压缩时优先合并同姿势的「建立+推进」
    n = min(6, max(3, len(actions)))
    if len(actions) > n:
        merged = []
        i = 0
        while i < len(actions):
            cur = actions[i]
            nxt = actions[i + 1] if i + 1 < len(actions) else None
            # 同一姿势的 建立 + 推进 → 合成一镜（绝不丢姿势）
            if (nxt and cur["kind"] == "establish" and nxt["kind"] == "push"
                    and cur.get("pose") == nxt.get("pose")):
                merged.append({
                    "kind": "establish",
                    "pose": cur["pose"],
                    "text": cur["text"] + "；" + nxt["text"],
                })
                i += 2
                continue
            merged.append(cur)
            i += 1
        actions = merged
        # 仍超限：合并中间转场进前一个建立镜（转场文本必须保留）
        while len(actions) > n:
            # 找第一个可合并的转场（非末镜）
            idx = next((k for k, a in enumerate(actions)
                        if a["kind"] == "transition" and k > 0 and k < len(actions) - 1), None)
            if idx is None:
                break
            actions[idx - 1]["text"] += "；" + actions[idx]["text"]
            actions.pop(idx)
    while len(actions) < n:
        actions.append(actions[-1])
    actions = actions[:n]
    bounds = shot_time_bounds(dur, n, actions)

    pose_names = "→".join(poses.get(p, {}).get("nameZh", p) for p in order_physically(seq))
    parts = []
    parts.append(f"Goal: Generate a {dur:.2f}-second {aspect} live-action adult video with "
                 f"readable physical contact, stable identity, and native dialogue audio.")
    parts.append("Audio rule: characters may only speak the exact words inside <d>...</d>; "
                 "never read pose, intensity, camera, or negative instructions aloud. "
                 "用户介绍、姿势名称、动作描述都不是台词，禁止念出；任何角色只能念 <d> 内的文字。")
    parts.append("表情自然；有浪叫或台词时张嘴，口型跟声音。")
    if idea:
        parts.append(f"用户介绍（必须体现）：{idea}")
    parts.append("")
    parts.append("Reference map (upload order = Picture number):")
    parts.append(f"<Picture 1> = {scene}：场景环境参考，锁定空间结构、陈设、材质与环境光线；仅锁场景，不作人物身份或姿势参考。")
    parts.append("<Picture 2> = 女子A：人物身份参考，锁定脸、发型、身材、肤色与服装状态。")
    parts.append("<Picture 3> = 男子A：人物身份参考，锁定脸、发型、身材、肤色与服装状态。")
    parts.append("角色与参考对应：女子A=<Picture 2>，男子A=<Picture 3>；场景与参考对应：" + scene + "=<Picture 1>")
    parts.append("For the target video, at 0.00 seconds into the target video, <Picture 2> and <Picture 3> "
                 "(character identity) are fully referenced for faces/bodies/clothing.")
    parts.append("Describe only the change that happens after 0.00s — do not re-describe still "
                 "appearance already shown in character refs; do not ignore scene refs.")
    parts.append("")
    parts.append("Consistency: Keep the same faces, body proportions, skin tone, hair, and clothing "
                 "state across every shot (match <Picture 2> + <Picture 3>). Keep genital scale and "
                 "junction proportions realistic and snug-fitting; contact stays close, not cavernous. "
                 "Keep the same location and ambient lighting as <Picture 1>; no set redesign, no "
                 "teleport to another place. One continuous take: no hard cuts, no teleportation, "
                 "no hidden transitions.")
    parts.append("Skin & Lighting: " + DE_OIL)
    parts.append("Motion quality（防僵硬）: 全程动作流畅连贯，符合真实人体力学："
                 "起落/抽送含预备—发力—跟随三阶段，体重转移有惯性，禁止整块平移；"
                 "二次动作——乳房与臀肉随动作有真实延迟的波浪晃动，发丝滞后轻摆，肌肉挤压回弹；"
                 "呼吸可见，肩膀与腹部随喘息起伏、节奏与动作同步；肌肉张弛交替，不锁死同一姿势；"
                 "切镜时动作不停顿，beat 间无缝衔接；加速渐进如波浪推高，不突然切档。")
    parts.append(f"Pose focus chain: {pose_names}.")
    parts.append("")
    parts.append("integrated_multimodal_description:")

    spoken = False
    for i, (act, bd) in enumerate(zip(actions, bounds)):
        head = "[Shot 1] Live-action cinematic." if i == 0 else \
               f"[Shot {i+1}] At {bd['t0']:.2f}s, the shot continues without cutting."
        body = act["text"]
        if i == 0:
            body = "镜头保持固定机位。" + body
            # 只有「本镜动作本身是插入类」时才加阴道贴合要点（口交/指插镜不加）
            this_pose = act.get("pose", "")
            first_pose = this_pose.split("->")[0]
            if first_pose not in FINISH_IDS and first_pose not in ORAL_ONLY:
                body += "；画面要点：阴茎与阴道紧密贴合插入，短行程进出清晰可读，交合处比例接近真人参考、阴唇自然包裹，不要占满画面"
        # 台词：只在本镜第一次出现时给，且同一句全片只念一次
        if lines and not spoken and i in (0, n // 2, n - 1):
            body += f" 女子A says: <d>[Chinese]{lines}</d>."
            spoken = True
        if i == n - 1:
            body += f" Final state: 人物身份不漂移，交合处仍紧密贴合、比例自然，构图稳定收住到 {dur:.2f}s。"
        parts.append(f"{head} {body}")
        parts.append("")

    parts.append("overall_soundscape: 室内安静底噪持续。湿润皮肤接触与节奏抽插声清晰可闻，"
                 "皮肤拍击夹杂其中。皮肤拍击、湿润声与床板轻响压在底层。")
    parts.append("non_diegetic_music: N/A")
    parts.append("")
    parts.append("=== NEGATIVE ===")
    parts.append(NEG)
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description="吞鲸分镜→提示词自动装配引擎")
    ap.add_argument("--shot", help="姿势链，逗号分隔，如 cowgirl,doggy")
    ap.add_argument("--dur", type=float, default=10.0, help="镜头时长秒")
    ap.add_argument("--lines", default="", help="台词")
    ap.add_argument("--idea", default="", help="用户介绍")
    ap.add_argument("--scene", default="卧室", help="场景名")
    ap.add_argument("--list-poses", action="store_true")
    ap.add_argument("--list-trans", action="store_true")
    args = ap.parse_args()

    poses, recipes = load()
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
