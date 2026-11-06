#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 提示词装配共享核心 (Tunjing Assembly Core)

唯一装配实现，供 tunjing_scene.py 与 tunjing_storyboard.py 共同调用，杜绝双份定义。
装配结构 1:1 对齐《大人的工作台》buildOfficialH3Prompt() 六段式。
"""

import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "..", "references")

FINISH_IDS = {"creampie", "cum_face", "cum_chest", "cum_belly", "cum_butt"}
ORAL_ONLY = {"bj", "squat_bj", "prone_bj", "deepthroat", "head_thrust", "facefuck",
             "sixty_nine", "cunnilingus", "sofa_cunni", "fingering", "clit_tease",
             "tip_lick", "ball_lick", "penis_slap", "handjob", "titjob"}

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


def load_poses():
    with open(os.path.join(REF, "workbench_poses_matrix.json"), encoding="utf-8") as f:
        return json.load(f)


def load_recipes():
    with open(os.path.join(REF, "transition_recipes.json"), encoding="utf-8") as f:
        return json.load(f)


def header_block(dur, aspect, idea="", scene="卧室", pose_names=""):
    """六段式的头部：Goal / Audio rule / Reference map / Consistency / 压油 / 防僵硬"""
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
    parts.append("For the target video, at 0.00 seconds into the target video, <Picture 2> and "
                 "<Picture 3> (character identity) are fully referenced for faces/bodies/clothing.")
    parts.append("Describe only the change that happens after 0.00s — do not re-describe still "
                 "appearance already shown in character refs; do not ignore scene refs.")
    parts.append("")
    parts.append("Consistency: Keep the same faces, body proportions, skin tone, hair, and clothing "
                 "state across every shot (match <Picture 2> + <Picture 3>). Keep genital scale and "
                 "junction proportions realistic and snug-fitting; contact stays close, not cavernous. "
                 "Keep the same location and ambient lighting as <Picture 1>; no set redesign, no "
                 "teleport to another place.")
    parts.append("Skin & Lighting: " + DE_OIL)
    parts.append("Motion quality（防僵硬）: 全程动作流畅连贯，符合真实人体力学："
                 "起落/抽送含预备—发力—跟随三阶段，体重转移有惯性，禁止整块平移；"
                 "二次动作——乳房与臀肉随动作有真实延迟的波浪晃动，发丝滞后轻摆，肌肉挤压回弹；"
                 "呼吸可见，肩膀与腹部随喘息起伏、节奏与动作同步；肌肉张弛交替，不锁死同一姿势；"
                 "切镜时动作不停顿，beat 间无缝衔接；加速渐进如波浪推高，不突然切档。")
    if pose_names:
        parts.append(f"Pose focus chain: {pose_names}.")
    parts.append("")
    return parts


def footer_block():
    return [
        "overall_soundscape: 室内安静底噪持续。湿润皮肤接触与节奏抽插声清晰可闻，"
        "皮肤拍击夹杂其中。皮肤拍击、湿润声与床板轻响压在底层。",
        "non_diegetic_music: N/A",
        "",
        "=== NEGATIVE ===",
        NEG,
    ]


def insert_hint(pose_id):
    """只有插入类姿势才加阴道贴合要点"""
    first = (pose_id or "").split("->")[0]
    if first in FINISH_IDS or first in ORAL_ONLY:
        return ""
    return ("；画面要点：阴茎与阴道紧密贴合插入，短行程进出清晰可读，"
            "交合处比例接近真人参考、阴唇自然包裹，不要占满画面")


def single_shot_prompt(shot, index, total_shots, dur, size_desc, cam_desc,
                       lines="", idea="", scene="卧室", pose_names=""):
    """
    为「拆镜表」中的单个镜头生成完整可送模提示词。
    shot: {pose, pose_zh, size, cam, text, type, t0, dur}
    """
    parts = header_block(dur, "9:16", idea=idea, scene=scene, pose_names=pose_names)

    if index == 0:
        head = "[Shot 1] Live-action cinematic."
    else:
        head = f"[Shot 1] At 0.00s, this clip begins directly at this beat."

    body = (f"景别：{size_desc}。机位：{cam_desc}。")
    body += shot["text"]
    body += insert_hint(shot.get("pose", ""))

    if lines:
        body += f" 女子A says: <d>[Chinese]{lines}</d>."

    if index == total_shots - 1:
        body += f" Final state: 人物身份不漂移，交合处仍紧密贴合、比例自然，构图稳定收住到 {dur:.2f}s。"

    parts.append("integrated_multimodal_description:")
    parts.append(f"{head} {body}")
    parts.append("")
    parts.extend(footer_block())
    return "\n".join(parts)
