#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 v3.0 · 提示词装配共享核心 (Tunjing Assembly Core v3.0)

唯一权威装配实现：
1. 【原厂 Full-Reference 语法集成】:
   - 彻底解耦 <Subject N> (动态可复用主体) 与 <Picture N> (物理参考图/锚点)
   - 注入 retention_analysis: 区分 fully_preserved 与 partially_preserved (脱衣镜头服装可褪，身份死锁)
   - 注入 原厂多说话人路由 <Subject N> (Sx) 与 (Sx, mouth occupied) 口交闭嘴标
   - 注入 <scenetrans> 与 <cutoff> 动态受力打断标
2. 【吞鲸工作室 v3.0 独家护城河】:
   - 双轨物理分流 (Composition Lock): 交合轨锁胯赶走人脸，面部轨锁脸赶走下半身
   - 180度轴线死锁 (Axis Lock) 与 20% 硬质背景标桩
   - 肢体减法法则: 一镜最多一只入画手
   - 13 类场地承托面 (with_scene_surface) 与声学底噪动态改写
   - Node 328 负向清零物理真相: 正向肯定句绝对压油词 (DE_OIL)
"""

import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "..", "references")

FINISH_IDS = {"creampie", "cum_face", "cum_chest", "cum_belly", "cum_butt", "squirting_climax"}
ORAL_ONLY = {"bj", "squat_bj", "prone_bj", "deepthroat", "head_thrust", "facefuck",
             "sixty_nine", "cunnilingus", "sofa_cunni", "fingering", "clit_tease",
             "tip_lick", "ball_lick", "penis_slap", "handjob", "titjob"}
FOREPLAY = {"undress", "kiss_fondle", "breast_rub", "nipple_lick",
            "kiss_pin", "kiss_force", "kiss_her", "ass_rub", "masturbation",
            "finger_masturbate", "solo_masturbate", "thigh_grind", "mirror_ear_whisper", "strip_tease"}

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

# ── 13 类场景承托面与声学映射 ──
SURFACE_PROFILES = {
    "bed":     {"noun": "bed", "on": "on the bed", "brace": "bracing against the bed", "grab": "gripping the bedsheets", "edge": "edge of bed", "sitEdge": "sitting on the edge of the bed", "pad": "wrinkled bedsheets", "lie": "lying supine on the bed", "kneel": "kneeling on the bed", "sfx": "creaking bed frame resonance"},
    "hotel":   {"noun": "hotel bed", "on": "on the hotel bed", "brace": "bracing on the hotel bed", "grab": "gripping crisp hotel sheets", "edge": "hotel bed edge", "sitEdge": "sitting on the hotel bed edge", "pad": "white hotel bedsheets", "lie": "lying on the hotel bed", "kneel": "kneeling on the hotel bed", "sfx": "muffled bedspring impact"},
    "sofa":    {"noun": "leather sofa", "on": "on the sofa", "brace": "bracing against sofa armrest", "grab": "gripping sofa cushions", "edge": "sofa edge", "sitEdge": "perched on the sofa edge", "pad": "soft leather cushions", "lie": "reclined back against the sofa cushions", "kneel": "straddling and kneeling on the sofa", "sfx": "creaking leather upholstery"},
    "chair":   {"noun": "heavy chair", "on": "on the chair", "brace": "gripping armrests", "grab": "holding the backrest", "edge": "seat edge", "sitEdge": "seated on the heavy chair", "pad": "chair seat", "lie": "leaning back into the chair", "kneel": "straddling the chair seat", "sfx": "strained wooden chair creaks"},
    "kitchen": {"noun": "kitchen island counter", "on": "on the kitchen counter", "brace": "palms flat on cold granite counter", "grab": "gripping the counter edge", "edge": "counter edge", "sitEdge": "seated on the marble counter lip", "pad": "polished cold counter surface", "lie": "arched back over the counter", "kneel": "prone across the kitchen counter", "sfx": "dull hollow countertop thuds"},
    "bath":    {"noun": "bathroom tiled floor", "on": "in the shower", "brace": "palms pressed against wet ceramic tiles", "grab": "holding tile wall ledge", "edge": "shower ledge", "sitEdge": "seated on the wet tile ledge", "pad": "slick wet bathroom tiles", "lie": "reclined against the tile wall", "kneel": "kneeling on the wet tile floor", "sfx": "splashing wet water echoes on cold tile"},
    "desk":    {"noun": "industrial metal desk", "on": "on the desk", "brace": "palms pressed on cold scratched steel desktop", "grab": "white-knuckle grip on the metal desk lip", "edge": "table rim", "sitEdge": "seated back on the rusty desk edge", "pad": "cold dark-grey steel tabletop with rivets", "lie": "upper torso flattened over the desk", "kneel": "prone belly-down over the desk rim", "sfx": "heavy metallic desk frame groan"},
    "wall":    {"noun": "solid concrete wall", "on": "against the wall", "brace": "both palms flat against the solid wall", "grab": "fingers clawing wall texture", "edge": "wall corner", "sitEdge": "back pinned flat to the wall", "pad": "solid textured wall surface", "lie": "spine flush against the cold wall", "kneel": "upright against the wall", "sfx": "heavy dull wall impacts"},
    "window":  {"noun": "floor-to-ceiling glass window", "on": "against the glass window", "brace": "palms pressed against the cold glass pane", "grab": "gripping window frame", "edge": "window sill", "sitEdge": "perched against the window sill", "pad": "steamed reflective glass window", "lie": "pressed back into the glass", "kneel": "kneeling before the window", "sfx": "glass pane vibration resonance"},
    "rug":     {"noun": "thick wool rug", "on": "on the floor rug", "brace": "palms digging into dense rug carpet", "grab": "clutching carpet fibers", "edge": "rug border", "sitEdge": "sitting on the rug", "pad": "textured thick rug", "lie": "supine across the soft rug", "kneel": "kneeling upright on the rug", "sfx": "muffled heavy floor impact"},
    "floor":   {"noun": "hardwood floor", "on": "on the bare floor", "brace": "palms braced on bare floorboards", "grab": "scratching hardwood seams", "edge": "floor edge", "sitEdge": "sitting on the floor", "pad": "polished dark hardwood floor", "lie": "flat on the hardwood floor", "kneel": "kneeling on the floor", "sfx": "solid wood floorboard resonance"},
    "car":     {"noun": "car leather seat", "on": "inside vehicle rear seat", "brace": "bracing on seat headrest or door handle", "grab": "gripping front seat back", "edge": "seat edge", "sitEdge": "cramped on the car leather seat", "pad": "contoured dark leather car seat", "lie": "tilted back in the car seat", "kneel": "straddling in the cramped car cabin", "sfx": "leather seat compression squeaks"},
    "balcony": {"noun": "balcony railing", "on": "at the balcony terrace", "brace": "holding the cold metal balcony railing", "grab": "both hands locked on the railing bar", "edge": "railing bar", "sitEdge": "leaned against the balcony ledge", "pad": "stone terrace floor", "lie": "bent forward over the terrace railing", "kneel": "kneeling on the stone balcony floor", "sfx": "wind draft and distant ambient air"},
}


def detect_scene_id(scene_name):
    s = (scene_name or "").lower()
    if any(k in s for k in ("车", "座舱", "后座", "car")): return "car"
    if any(k in s for k in ("浴", "淋浴", "温泉", "汤池", "bath", "shower")): return "bath"
    if any(k in s for k in ("沙发", "茶几", "休息室", "客厅", "包厢", "sofa")): return "sofa"
    if any(k in s for k in ("椅", "王座", "宝座", "老板椅", "chair", "throne")): return "chair"
    if any(k in s for k in ("厨", "料理", "吧台", "kitchen", "bar")): return "kitchen"
    if any(k in s for k in ("窗", "落地窗", "window")): return "window"
    if any(k in s for k in ("阳台", "露台", "天台", "balcony")): return "balcony"
    if any(k in s for k in ("墙", "走廊", "巷", "电梯", "楼梯", "试衣间", "wall", "elevator")): return "wall"
    if any(k in s for k in ("地毯", "毯", "榻榻米", "rug")): return "rug"
    if any(k in s for k in ("地面", "地板", "地牢", "密室", "训练室", "祭坛", "floor")): return "floor"
    if any(k in s for k in ("办公", "书房", "桌", "案几", "讲台", "会议", "实验室", "诊室", "desk", "office", "铁桌")): return "desk"
    if any(k in s for k in ("酒店", "宾馆", "套房", "hotel")): return "hotel"
    return "bed"


def with_scene_surface(act_text, scene_name):
    if not act_text: return act_text
    sc_id = detect_scene_id(scene_name)
    if sc_id in ("bed", "hotel"): return act_text
    loc = SURFACE_PROFILES.get(sc_id, SURFACE_PROFILES["desk"])
    out = str(act_text)
    reps = [
        ("坐在床的边缘", loc["sitEdge"]),
        ("坐在床边缘", loc["sitEdge"]),
        ("坐在床沿边缘", loc["sitEdge"]),
        ("坐在床沿", loc["sitEdge"]),
        ("坐床沿", loc["sitEdge"]),
        ("双手撑床或抓床单", loc["brace"] + " or " + loc["grab"]),
        ("撑床或抓床单", loc["brace"] + " or " + loc["grab"]),
        ("双手撑在床面上", loc["brace"]),
        ("双手撑床面上", loc["brace"]),
        ("双手撑床", loc["brace"]),
        ("手撑床", loc["brace"]),
        ("撑床面", loc["brace"]),
        ("撑床", loc["brace"]),
        ("抓紧床单", loc["grab"]),
        ("抓床单", loc["grab"]),
        ("抠床单", loc["grab"]),
        ("按床单", loc["grab"]),
        ("床单", loc["pad"]),
        ("床垫", loc["pad"]),
        ("床面", loc["pad"]),
        ("床沿", loc["edge"]),
        ("床板", loc["edge"]),
        ("仰卧在床上", loc["lie"]),
        ("躺在床上", loc["lie"]),
        ("跪在床上", loc["kneel"]),
        ("在床上", loc["on"]),
        ("床上", loc["on"]),
    ]
    for old, new in reps:
        out = out.replace(old, new)
    return out


def build_soundscape_en(scene_name):
    sc_id = detect_scene_id(scene_name)
    loc = SURFACE_PROFILES.get(sc_id, SURFACE_PROFILES["bed"])
    surf_sfx = loc.get("sfx", "")
    return (f"Quiet room tone continues throughout. Rhythmic skin-on-skin collision slaps, "
            f"viscous lubrication friction, heavy ragged breathing, and subtle {surf_sfx}. "
            f"Strictly NO subtitles, NO text, NO captions, NO watermark.")


def load_poses():
    with open(os.path.join(REF, "tunjing_poses_matrix.json"), encoding="utf-8") as f:
        return json.load(f)


def load_recipes():
    with open(os.path.join(REF, "transition_recipes.json"), encoding="utf-8") as f:
        return json.load(f)


def build_fullref_header(dur, aspect, scene="当前场景", idea="", is_undress=False):
    """
    100% 对齐 MiniMax 官方原厂 Ref2VA 指南六段式头部:
    1. subject_definitions (<Subject N> 实体与 <Picture N> 物理锚点解耦)
    2. summary (任务类型标定)
    3. retention_analysis (fully_preserved vs partially_preserved 脱衣保留度)
    4. consistency & motion locks
    """
    sc_id = detect_scene_id(scene)
    surf = SURFACE_PROFILES.get(sc_id, SURFACE_PROFILES["bed"])

    parts = []
    # 1. 目标与音频规则
    parts.append(f"Goal & Audio Contract: {dur:.2f}s duration, {aspect} vertical, 24fps. "
                 f"Live-action cinematic adult drama take with readable physical biomechanics and stable identity.")
    parts.append("Audio rule: characters may ONLY speak the exact words inside <d>...</d>; "
                 "never read directions, camera notes, or pose labels aloud. "
                 "non_diegetic_music: N/A; diegetic foley and dialogue only.")
    parts.append("")

    # 2. 官方原厂标准: subject_definitions (铁律: <Picture 1>=女主, <Picture 2>=男主, <Picture 3>=场景)
    parts.append("subject_definitions:")
    if is_undress:
        parts.append("<Subject 1> is the young woman in <Picture 1>, with pale skin, long dark hair; outfit is unfastened and peeled off in this take.")
    else:
        parts.append("<Subject 1> is the woman from <Picture 1>, with pale skin, long silky dark hair, and realistic anatomical proportions.")
    parts.append("<Subject 2> is the mature man from <Picture 2>, with strong masculine physique, weathered tan skin, and defined musculature.")
    parts.append(f"<Subject 3> is the {scene} environment anchored in <Picture 3>, featuring {surf['noun']} and ambient noir lighting.")
    parts.append("")

    # 3. 官方原厂标准: summary
    parts.append("summary:")
    parts.append(f"[reference generation + audio reference] The target video captures intimate kinetic physical drama between "
                 f"<Subject 1> and <Subject 2> within <Subject 3>. All identities strictly reference <Picture 1> and <Picture 2>.")
    parts.append("")

    # 4. 官方原厂标准: retention_analysis (脱衣镜头安全锁)
    parts.append("retention_analysis:")
    if is_undress:
        parts.append("<Subject 1>: partially_preserved - facial features and body anatomy fully preserved; clothing state transitions dynamically as clothes slide down.")
    else:
        parts.append("<Subject 1>: fully_preserved - facial features, body anatomy, and skin texture are strictly locked to <Picture 1>.")
    parts.append("<Subject 2>: fully_preserved - masculine facial identity, physique, and skin tone are strictly locked to <Picture 2>.")
    parts.append("<Subject 3>: fully_preserved - space architecture, materials, and lighting are strictly locked to <Picture 3>.")
    parts.append("")

    # 5. 一致性与材质压油死锁 (Consistency Lock)
    parts.append("Consistency: Keep the same faces, body proportions, skin tone, hair, and anatomical scale throughout. "
                 "Strictly TWO adults in frame. Keep genital scale realistic and snug-fitting; contact stays close. "
                 "180-degree axis locked on a stationary tripod. NO set redesign, NO teleportation.")
    parts.append("Skin & Lighting: " + DE_OIL)
    parts.append("Motion quality (Anti-Stiffness): Smooth continuous human kinematics with visible inertia, follow-through, "
                 "and natural breathing. Breasts and buttocks exhibit authentic delayed wave jiggle and recoil upon impact. "
                 "Seamless kinetic momentum between cuts; NO sudden freeze or popping.")
    parts.append("")
    return parts


def build_shot_description(shot, index, total_shots, dur, size_desc, cam_desc,
                           lines="", speaker="女子A", scene="当前场景"):
    """
    根据《深渊之契》双轨物理分流 (Composition Lock) 与官方原厂 detailed_description 规则编译单镜描述
    """
    pid = shot.get("pose", "")
    first_p = pid.split("->")[0]
    p_zh = shot.get("pose_zh", "")

    # 判断轨道类型
    is_oral = first_p in ORAL_ONLY or "口交" in p_zh or "深喉" in p_zh
    is_penetration = (first_p not in FOREPLAY and first_p not in ORAL_ONLY and first_p not in FINISH_IDS and "->" not in pid)
    is_climax = first_p in FINISH_IDS or "射" in p_zh or "内射" in p_zh
    is_undress = "undress" in first_p

    # 景别与双轨构图死锁 (Composition Lock)
    comp_lock = ""
    if shot["size"] in ("hip", "macro") and is_penetration:
        comp_lock = ("COMPOSITION LOCK: Camera locked low-angle at pelvic level, framed strictly from waist to mid-thigh. "
                     "HEADS, FACES, AND UPPER TORSO ARE STRICTLY OUT OF FRAME. "
                     "Only the rhythmic collision of pelvic bones and joined hips in view. ")
    elif shot["size"] in ("face", "cu") and not is_oral:
        comp_lock = ("COMPOSITION LOCK: Tight close-up locked on female side-profile and neck. "
                     "LOWER BODY AND GENITALIA STRICTLY OUT OF FRAME. "
                     "Intercourse is depicted ONLY through rhythmic shoulder trembling and hair shaking from unseen thrusts. ")
    elif is_undress:
        comp_lock = ("COMPOSITION LOCK: Medium-close framing strictly locked on shoulders, collarbone, and unbuttoning fingers. "
                     "Male is fully dressed in background. LOWER BODY AND GENITALIA STRICTLY OUT OF FRAME to prevent exposure. ")

    # 时间轴切分: [00.00s - XX.XXs] 三段式动量
    at_str = "At 0.00s, actively in motion, inheriting momentum from previous shot with NO pause or freeze. " if index > 0 else "From 0.00s: "
    adapted_action = with_scene_surface(shot.get("text", ""), scene)

    # 肢体减法与防蛇信子/防插入要点
    body_text = f"{comp_lock}{at_str}{adapted_action}."
    if any(k in pid for k in ("kiss", "kiss_fondle", "kiss_pin", "kiss_force", "kiss_her")):
        body_text += " (Anatomical constraint: lips gently parted with subtle contact; strictly NO exaggerated tongue protrusion; realistic lip anatomy)."
    
    # 只有纯结合交合镜且非微距排除人脸时才附加插入贴合
    if is_penetration and shot["size"] not in ("face", "cu"):
        body_text += " Snug anatomical junction between penis and vaginal entrance, rhythmic piston stroke clearly readable with elastic skin recoil."

    # 原厂标准台词装配: <Subject N> (Sx) 与三段式气口 (铁律: S1=Subject 1=女, S2=Subject 2=男)
    dialogue_block = ""
    if lines:
        spk_tag = "<Subject 1> (S1)" if "女" in speaker else "<Subject 2> (S2)"
        # 嘴部占用检查
        if is_oral and "女" in speaker:
            dialogue_block = f" <Subject 1> (S1, mouth occupied) stays completely silent with lips sealed around shaft."
        else:
            t_mid_start = max(1.0, round(dur * 0.25, 2))
            t_mid_end = min(dur - 0.5, round(dur * 0.75, 2))
            dialogue_block = (f" From {t_mid_start:.2f}s to {t_mid_end:.2f}s, maintaining rhythmic kinetic motion, "
                              f"{spk_tag} says: <d>[Chinese]{lines}</d>.")

    # 镜头尾部稳定收束
    tail = ""
    if index == total_shots - 1:
        tail = f" Final state: Unbroken anatomical continuity and stable composition held steady to {dur:.2f}s."

    full_shot_desc = f"[Shot {index+1}] {size_desc}. {cam_desc}. {body_text}{dialogue_block}{tail}"
    return full_shot_desc


def single_shot_prompt(shot, index, total_shots, dur, size_desc, cam_desc,
                       lines="", speaker="女子A", idea="", scene="当前场景", pose_names=""):
    """
    对外唯一装配接口: 生成包含原厂六段式 + 深渊之契双轨死锁的终极提示词
    """
    is_undress = "undress" in shot.get("pose", "")
    header = build_fullref_header(dur, "9:16", scene=scene, idea=idea, is_undress=is_undress)
    
    shot_body = build_shot_description(
        shot, index, total_shots, dur, size_desc, cam_desc,
        lines=lines, speaker=speaker, scene=scene
    )

    parts = list(header)
    parts.append("integrated_multimodal_description:")
    parts.append(shot_body)
    parts.append("")
    parts.append("overall_soundscape: " + build_soundscape_en(scene))
    parts.append("non_diegetic_music: N/A")
    parts.append("")
    parts.append("=== NEGATIVE ===")
    parts.append(NEG)
    return "\n".join(parts)
