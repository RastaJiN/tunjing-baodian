#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 v4.0 · 全剧集导演调度与提示词装配共享核心 (Tunjing Assembly Core v4.0)

核心融合特性（《不完全手册》×《吞鲸宝典》终极合体版）：
1. 全面对齐 R1~R12 全肯定无否定式语法（Positive-Only Grammar）：
   - 正向送模文本彻底剥离 `=== NEGATIVE ===` 负向清单（防 Node 328 清零后正向反噬画油光/断肢）
   - 废除 `OUT OF FRAME / no / without` 否定词根，全面改用正面物理存在边界（Positive Cropping & Anatomy Lock）
   - 注入 `MOTION FLOOR:` 底噪生命力锁（破除台词合成时身体 PSNR 42dB 僵尸定格）
   - 注入唯一 `Camera:` 量化运镜行与独立 `SPEECH:` 台词行
2. 原生支持 9 图 + 3 音（`<Audio 1>` / `<Audio 2>` 人物固定声线克隆）动态锚定
3. 原生支持 8 大非肉戏导演调度原语（环境空镜、双人封堵、男正打 srs_male、女反打 srs_female、信物微距 prop_insert、生理阻断 cut_insert、空间转移 spatial_shift、尾声独处 outro_solo）与 55 套肉戏真源无缝混排
4. 13 类场地中英双轨承托面 (`with_scene_surface`) 动态改写
"""

import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "..", "references")

STAGING_IDS = {
    "env_establish", "blocking_2s", "srs_male", "srs_female",
    "prop_insert", "cut_insert", "spatial_shift", "outro_solo",
    "empty_cut", "corridor_cut"
}
FINISH_IDS = {"creampie", "cum_face", "cum_chest", "cum_belly", "cum_butt", "squirting_climax"}
ORAL_ONLY = {"bj", "squat_bj", "prone_bj", "deepthroat", "head_thrust", "facefuck",
             "sixty_nine", "cunnilingus", "sofa_cunni", "fingering", "clit_tease",
             "tip_lick", "ball_lick", "penis_slap", "handjob", "titjob"}
FOREPLAY = {"undress", "kiss_fondle", "breast_rub", "nipple_lick",
            "kiss_pin", "kiss_force", "kiss_her", "ass_rub", "masturbation",
            "finger_masturbate", "solo_masturbate", "thigh_grind", "mirror_ear_whisper", "strip_tease"}

# R4 全肯定正向压油词（彻底剔除 without / non- / zero 等否定前缀，100% 物理肯定词）
DE_OIL = (
    "authentic matte velvet skin finish, powdered dry complexion texture, natural human skin with "
    "visible fine pores and subtle dermal grain, soft subsurface scattering with gentle matte light absorption, "
    "heavily diffused soft ambient illumination, organic 35mm cinema film grain, photorealistic human anatomy, "
    "clean full-bleed raw 35mm cinema frame"
)

MOTION_FLOOR = (
    "MOTION FLOOR: Continuous organic human micro-kinematics throughout every second; visible ribcage and collarbone "
    "breathing expansion of 1 cm, subtle weight shifts across the support surface, natural hair strand micro-sway, "
    "and realistic soft-tissue recoil."
)

OFFICIAL_CUT_PHRASES = (
    "the camera cuts to",
    "the shot cuts to",
    "the shot transitions to",
    "the shot changes to",
    "the shot switches to",
)

EMOTION_MUSCLE_CUES = {
    "forbearance": "jaw clenched tight, throat bobbing once in a swallow, gaze dropping 10 cm then rising while knuckles whiten",
    "mockery": "one corner of the mouth lifting 2 mm, eyelids half-lowered sweeping a glance across while fingers tap twice",
    "provocation": "chin tilted up 15 degrees, steady eye contact locked forward while collarbones rise",
    "submission": "eyelashes trembling with gaze lowered toward the floor, lower lip pressed between teeth as shoulders sink 2 cm",
    "ecstasy": "pupils dilated with upward gaze, head tilting back against the support as neck tendons tense",
    "default": "jaw muscles tensing with visible chest breathing and natural head micro-shifts of 2 cm",
}

# 仅供离线审计或独立字段存档，严禁拼入送模正向 Node 263 文本！
NEG = """Subtitles, captions, watermarks, UI, logos, on-screen text
Face swap, identity drift, deformed limbs, extra fingers, melting bodies
Detached anatomy, orbiting camera, fast zoom, static frozen frames"""

# ── 13 类场景承托面与声学映射 ──
SURFACE_PROFILES = {
    "bed":     {"noun": "bed", "on": "on the bed", "brace": "bracing against the bed", "grab": "gripping the bedsheets", "edge": "edge of bed", "sitEdge": "sitting on the edge of the bed", "pad": "wrinkled bedsheets", "lie": "lying supine on the bed", "kneel": "kneeling on the bed", "sfx": "creaking bed frame resonance"},
    "hotel":   {"noun": "hotel bed", "on": "on the hotel bed", "brace": "bracing on the hotel bed", "grab": "gripping crisp hotel sheets", "edge": "hotel bed edge", "sitEdge": "sitting on the hotel bed edge", "pad": "white hotel bedsheets", "lie": "lying on the hotel bed", "kneel": "kneeling on the hotel bed", "sfx": "muffled bedspring impact"},
    "sofa":    {"noun": "leather sofa", "on": "on the sofa", "brace": "bracing against sofa armrest", "grab": "gripping sofa cushions", "edge": "sofa edge", "sitEdge": "perched on the sofa edge", "pad": "soft leather cushions", "lie": "reclined back against the sofa cushions", "kneel": "straddling and kneeling on the sofa", "sfx": "creaking leather upholstery"},
    "chair":   {"noun": "heavy chair", "on": "on the chair", "brace": "gripping armrests", "grab": "holding the backrest", "edge": "seat edge", "sitEdge": "seated on the heavy chair", "pad": "chair seat", "lie": "leaning back into the chair", "kneel": "straddling the chair seat", "sfx": "strained wooden chair creaks"},
    "kitchen": {"noun": "kitchen island counter", "on": "on the kitchen counter", "brace": "palms flat on cold granite counter", "grab": "gripping the counter edge", "edge": "counter edge", "sitEdge": "seated on the marble counter lip", "pad": "polished cold counter surface", "lie": "arched back over the counter", "kneel": "prone across the kitchen counter", "sfx": "dull hollow countertop thuds"},
    "bath":    {"noun": "bathroom tiled floor", "on": "in the shower", "brace": "palms pressed against wet ceramic tiles", "grab": "holding tile wall ledge", "edge": "shower ledge", "sitEdge": "seated on the wet tile ledge", "pad": "slick wet bathroom tiles", "lie": "reclined against the tile wall", "kneel": "kneeling on the wet tile floor", "sfx": "splashing wet water echoes on cold tile"},
    "desk":    {"noun": "industrial metal desk", "on": "on the desk", "brace": "palms pressed on cold scratched steel desktop", "grab": "white-knuckle grip on the metal desk lip", "edge": "table rim", "sitEdge": "seated back on the desk edge", "pad": "cold dark-grey steel tabletop", "lie": "upper torso flattened over the desk", "kneel": "prone belly-down over the desk rim", "sfx": "heavy metallic desk frame groan"},
    "wall":    {"noun": "solid concrete wall", "on": "against the wall", "brace": "both palms flat against the solid wall", "grab": "fingers pressing wall texture", "edge": "wall corner", "sitEdge": "back pinned flat to the wall", "pad": "solid textured wall surface", "lie": "spine flush against the cold wall", "kneel": "upright against the wall", "sfx": "heavy dull wall impacts"},
    "window":  {"noun": "floor-to-ceiling glass window", "on": "against the glass window", "brace": "palms pressed against the cold glass pane", "grab": "gripping window frame", "edge": "window sill", "sitEdge": "perched against the window sill", "pad": "steamed reflective glass window", "lie": "pressed back into the glass", "kneel": "kneeling before the window", "sfx": "glass pane vibration resonance"},
    "rug":     {"noun": "thick wool rug", "on": "on the floor rug", "brace": "palms pressing into dense rug carpet", "grab": "clutching carpet fibers", "edge": "rug border", "sitEdge": "sitting on the rug", "pad": "textured thick rug", "lie": "supine across the soft rug", "kneel": "kneeling upright on the rug", "sfx": "muffled heavy floor impact"},
    "floor":   {"noun": "hardwood floor", "on": "on the bare floor", "brace": "palms braced on bare floorboards", "grab": "gripping hardwood seams", "edge": "floor edge", "sitEdge": "sitting on the floor", "pad": "polished dark hardwood floor", "lie": "flat on the hardwood floor", "kneel": "kneeling on the floor", "sfx": "solid wood floorboard resonance"},
    "car":     {"noun": "car leather seat", "on": "inside vehicle rear seat", "brace": "bracing on seat headrest", "grab": "gripping front seat back", "edge": "seat edge", "sitEdge": "cramped on the car leather seat", "pad": "contoured dark leather car seat", "lie": "tilted back in the car seat", "kneel": "straddling in the car cabin", "sfx": "leather seat compression squeaks"},
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
    if any(k in s for k in ("墙", "走廊", "巷", "电梯", "楼梯", "试衣间", "镜", "wall", "elevator", "mirror")): return "wall"
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

    reps_en = [
        (r"\bsitting on the edge of the bed\b", loc["sitEdge"]),
        (r"\bsits on the edge of the bed\b", loc["sitEdge"]),
        (r"\bon the edge of the bed\b", f"at the {loc['edge']}"),
        (r"\bon the bed edge\b", f"at the {loc['edge']}"),
        (r"\bbed edge\b", loc["edge"]),
        (r"\bedge of bed\b", loc["edge"]),
        (r"\bgripping the bedsheets\b", loc["grab"]),
        (r"\bgripping the sheets\b", loc["grab"]),
        (r"\bbracing bed/his thighs\b", f"{loc['brace']} or his thighs"),
        (r"\bbraces thigh/bed\b", f"braces thigh or {loc['pad']}"),
        (r"\bbedsheets\b", loc["pad"]),
        (r"\bbedsheet\b", loc["pad"]),
        (r"\bmattress\b", loc["pad"]),
        (r"\bpillow\b", loc["pad"]),
        (r"\bon the bed\b", loc["on"]),
        (r"\binto the bed\b", f"against the {loc['pad']}"),
        (r"\bthe bed\b", f"the {loc['noun']}"),
    ]
    for pat, repl in reps_en:
        out = re.sub(pat, repl, out, flags=re.IGNORECASE)
    return out


def build_soundscape_en(scene_name, is_staging=False):
    sc_id = detect_scene_id(scene_name)
    loc = SURFACE_PROFILES.get(sc_id, SURFACE_PROFILES["bed"])
    surf_sfx = loc.get("sfx", "subtle surface resonance")
    if is_staging:
        return (f"Quiet interior room tone continues throughout. Crisp fabric rustle, measured footsteps, "
                f"tense breathing, and subtle {surf_sfx}.")
    return (f"Quiet room tone continues throughout. Rhythmic skin-on-skin collision slaps, "
            f"viscous lubrication friction, heavy ragged breathing, and subtle {surf_sfx}.")


def load_poses():
    with open(os.path.join(REF, "tunjing_poses_matrix.json"), encoding="utf-8") as f:
        return json.load(f)


def load_recipes():
    with open(os.path.join(REF, "transition_recipes.json"), encoding="utf-8") as f:
        return json.load(f)


def build_fullref_header(
    dur,
    aspect,
    scene="hotel suite",
    idea="",
    is_undress=False,
    is_staging=False,
    tier="A_two_shot",
    female_desc="young woman anchored in <Picture 1>, preserving her exact facial structure, hairstyle, skin tone, and anatomical proportions",
    male_desc="mature man anchored in <Picture 2>, preserving his exact masculine facial identity, hairstyle, skin tone, and muscular build",
    scene_props="",
    has_audio_refs=True,
):
    """
    吞鲸 v4.0 权威头部装配：
    - 100% 遵循 R1~R12 全肯定语法（零否定词）
    - 支持单人正反打/空镜槽位物理隔离描述
    - 支持 <Audio 1> / <Audio 2> 角色声线参考声明
    - 显式内嵌 MOTION FLOOR 与场景弱构图引用锁
    """
    sc_id = detect_scene_id(scene)
    surf = SURFACE_PROFILES.get(sc_id, SURFACE_PROFILES["bed"])
    scene_en_map = {
        "bed": "master bedroom", "hotel": "luxury hotel suite", "sofa": "lounge room",
        "chair": "private study", "kitchen": "modern kitchen", "bath": "steamy bathroom",
        "desk": "executive office", "wall": "dimly lit interior wall", "window": "high-rise suite",
        "rug": "living room", "floor": "interior room", "car": "luxury sedan cabin",
        "balcony": "private terrace"
    }
    scene_en = scene if not re.search(r"[\u4e00-\u9fff]", str(scene)) else scene_en_map.get(sc_id, "interior room")
    props_clause = f", featuring {scene_props}" if scene_props and not re.search(r"[\u4e00-\u9fff]", scene_props) else f", featuring {surf['noun']}"

    parts = []
    # 1. Goal & Audio Contract (全肯定描述)
    parts.append(f"Goal & Audio Contract: Generate a {dur:.2f}-second {aspect} live-action cinema video "
                 f"with readable physical biomechanics, locked identity consistency, and synchronized native audio.")
    parts.append("Audio rule: characters vocalize exclusively the exact words enclosed inside <d>...</d> tags; "
                 "all other moments contain pure physical foley and natural breathing.")
    parts.append("")

    # 2. Anchoring & subject_definitions
    parts.append("Anchoring & Consistency:")
    parts.append("subject_definitions:")
    if tier == "C_empty_cut":
        parts.append(f"<Subject 3> is the pure architectural {scene_en} environment anchored in <Picture 3>{props_clause} and ambient lighting.")
    elif tier == "B_solo_female":
        parts.append(f"<Subject 1> is the {female_desc}.")
        parts.append(f"<Subject 3> is the {scene_en} support surface and background environment anchored in <Picture 3>{props_clause}.")
    elif tier == "B_solo_male":
        parts.append(f"<Subject 2> is the {male_desc}.")
        parts.append(f"<Subject 3> is the {scene_en} support surface and background environment anchored in <Picture 3>{props_clause}.")
    else:
        if is_undress:
            parts.append(f"<Subject 1> is the {female_desc}; her outer garment unfastens and slides down during this take.")
        else:
            parts.append(f"<Subject 1> is the {female_desc}.")
        parts.append(f"<Subject 2> is the {male_desc}.")
        parts.append(f"<Subject 3> is the {scene_en} environment anchored in <Picture 3>{props_clause} and ambient lighting.")

    if has_audio_refs and tier != "C_empty_cut":
        parts.append("Audio timbre anchors: <Audio 1> locks the vocal timbre of <Subject 1> (S1); <Audio 2> locks the vocal timbre of <Subject 2> (S2).")
    parts.append("")

    # 3. summary
    parts.append("summary:")
    if tier == "C_empty_cut":
        parts.append("[reference generation] Pure architectural environment establishing shot within <Subject 3> anchored in <Picture 3>.")
    elif tier == "B_solo_female":
        parts.append("[reference generation + audio reference] Tight single-subject emotional reaction of <Subject 1> within <Subject 3>.")
    elif tier == "B_solo_male":
        parts.append("[reference generation + audio reference] Tight single-subject dominant focus on <Subject 2> within <Subject 3>.")
    else:
        parts.append("[reference generation + audio reference] High-tension dramatic interaction between <Subject 1> and <Subject 2> within <Subject 3>.")
    parts.append("")

    # 4. retention_analysis
    parts.append("retention_analysis:")
    if tier != "C_empty_cut":
        if is_undress:
            parts.append("<Subject 1>: partially_preserved - facial features, hairstyle, and body anatomy fully preserved from <Picture 1>; clothing transitions smoothly.")
        else:
            parts.append("<Subject 1>: fully_preserved - facial identity, exact hairstyle, body anatomy, and skin texture are strictly locked to <Picture 1>.")
        parts.append("<Subject 2>: fully_preserved - masculine facial identity, physique, and skin tone are strictly locked to <Picture 2>.")
    parts.append(f"<Subject 3>: fully_preserved for spatial geometry, {surf['noun']} texture, and lighting direction from <Picture 3>; weak_reference for exact camera framing.")
    parts.append("")

    # 5. Consistency, Skin & Lighting, MOTION FLOOR
    if tier == "C_empty_cut":
        parts.append("Consistency: Empty architectural space containing exclusively furniture, structure, and lighting from <Picture 3>.")
    elif tier in ("B_solo_female", "B_solo_male"):
        subj = "<Subject 1>" if tier == "B_solo_female" else "<Subject 2>"
        parts.append(f"Consistency: Single subject {subj} in frame with 20% shallow depth-of-field background showing <Subject 3> texture from <Picture 3>.")
    else:
        parts.append("Consistency: Keep the same faces, body proportions, skin tone, hairstyle, and anatomical scale throughout. "
                     "Two adults in frame. The camera stays on the same side of them throughout; <Subject 1> is on the left, <Subject 2> is on the right.")
    parts.append("Skin & Lighting: " + DE_OIL)
    parts.append("Motion quality (Anti-Stiffness): Smooth continuous human kinematics with visible inertia, follow-through, "
                 "and natural breathing. Breasts and buttocks exhibit authentic delayed wave jiggle and recoil upon impact.")
    parts.append(MOTION_FLOOR)
    parts.append("")
    return parts


def sanitize_positive_only(text):
    """
    R4 正向全肯定净化器：将残留的否定短语转化为纯正面物理描述，确保 100% 通过 h3_lint R4
    """
    if not text:
        return text
    out = str(text)
    replacements = [
        (r"HEADS,\s*FACES,\s*AND\s*UPPER\s*TORSO\s*ARE\s*STRICTLY\s*OUT\s*OF\s*FRAME\.?",
         "The frame is tightly cropped from waist to mid-thigh, containing exclusively the lower torso, hips, and pelvic contact junction."),
        (r"LOWER\s*BODY\s*AND\s*GENITALIA\s*STRICTLY\s*OUT\s*OF\s*FRAME\.?",
         "The frame is tightly cropped from chest and collarbones up to the head, containing exclusively the upper torso, neck, and face."),
        (r"\bno exaggerated tongue protrusion\b", "tongue stays naturally inside the oral cavity"),
        (r"\bwithout cutting\b", "in one continuous unbroken take"),
        (r"\bno hard cuts\b", "continuous unbroken motion"),
        (r"\bwithout surface reflection\b", "with gentle matte light absorption"),
        (r"\bnon-greasy complexion\b", "dry velvet complexion"),
        (r"\bzero hard directional light\b", "even ambient illumination"),
        (r"\bunobstructed\b", "clean"),
    ]
    for pat, rep in replacements:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)
    return out


def build_shot_description(shot, index, total_shots, dur, size_desc, cam_desc,
                           lines="", speaker="女子A", scene="hotel suite",
                           emotion="default", voiceover=False, hold_last_second=False):
    """
    编译单镜画面与独立 SPEECH 行（100% 对齐 R1~R12 全肯定语法 + 分号分割律 + 唯一 Camera 行）
    """
    pid = shot.get("pose", "")
    first_p = pid.split("->")[0]
    p_zh = shot.get("pose_zh", "")
    is_transition = "->" in pid or shot.get("type") == "transition"
    is_staging = first_p in STAGING_IDS

    is_oral = first_p in ORAL_ONLY or "口交" in p_zh or "深喉" in p_zh
    is_penetration = (first_p not in FOREPLAY and first_p not in ORAL_ONLY and first_p not in FINISH_IDS
                      and not is_staging and not is_transition)
    is_undress = "undress" in first_p

    # 防呆熔断 1：若交合微距镜 (hip/macro) 或空镜/道具镜带了台词，自动转为 off-screen voiceover 画外音
    effective_vo = bool(voiceover)
    if lines and (shot.get("size") in ("hip", "macro") or first_p in ("env_establish", "prop_insert", "cut_insert")):
        effective_vo = True

    # 防呆熔断 2：双轨物理分流构图死锁（R4 全肯定物理切边描述，零 OUT OF FRAME / NO 否定词）
    comp_lock = ""
    if first_p == "env_establish":
        comp_lock = ("COMPOSITION LOCK: Pure architectural environment framing anchored in <Picture 3>, "
                     "focusing exclusively on spatial geometry, lighting, and existing interior furnishings. ")
    elif first_p in ("prop_insert", "cut_insert"):
        comp_lock = ("COMPOSITION LOCK: Extreme macro framing cropped tightly on the hand and surface contact area, "
                     "with 20% shallow depth-of-field background anchored in <Picture 3>. ")
    elif first_p == "srs_male":
        comp_lock = ("COMPOSITION LOCK: Tight single-subject focus cropped from chest to head on <Subject 2>, "
                     "capturing exclusively his facial expression, jawline tension, and shoulder drive against <Picture 3> background. ")
    elif first_p == "srs_female":
        comp_lock = ("COMPOSITION LOCK: Tight single-subject reaction cropped from collarbones to head on <Subject 1>, "
                     "capturing exclusively her trembling eyelashes, lips, and rhythmic shoulder vibration against <Picture 3> support surface. ")
    elif shot.get("size") in ("hip", "macro") and is_penetration and (not lines or effective_vo):
        comp_lock = ("COMPOSITION LOCK: Low-angle pelvic framing cropped tightly from waist to mid-thigh, "
                     "containing exclusively the lower torso, joined hips, and rhythmic pelvic collision against <Picture 3> surface. ")
    elif shot.get("size") in ("face", "cu") and not is_oral and not is_transition:
        comp_lock = ("COMPOSITION LOCK: Tight close-up cropped from collarbones to head on facial profile and neck. "
                     "Physical momentum is conveyed through rhythmic shoulder trembling and hair shaking. ")
    elif is_undress:
        comp_lock = ("COMPOSITION LOCK: Medium-close framing cropped from chest to head on shoulders, collarbone, and unbuttoning fingers, "
                     "with <Subject 2> in full wardrobe. ")

    # 唯一 Camera: 指令行 + 分号 (;) 黄金分割律
    if index == 0:
        shot_prefix = f"Camera: {size_desc}, {cam_desc}.\n[Shot 1] Live-action cinematic, {size_desc}, {cam_desc}; "
        if first_p == "env_establish":
            at_str = "From 0.00s, within <Subject 3>: "
        elif first_p == "srs_female" or first_p == "outro_solo":
            at_str = "From 0.00s, <Subject 1> within <Subject 3>: "
        elif first_p == "srs_male":
            at_str = "From 0.00s, <Subject 2> within <Subject 3>: "
        else:
            at_str = "From 0.00s, <Subject 1> and <Subject 2> in <Subject 3>: "
    else:
        cut_phrase = OFFICIAL_CUT_PHRASES[index % len(OFFICIAL_CUT_PHRASES)]
        t0_val = shot.get("t0", round(index * dur, 2))
        shot_prefix = f"Camera: {size_desc}, {cam_desc}.\n[Shot {index+1}] At {t0_val:.2f}s, {cut_phrase} {size_desc}, {cam_desc}; "
        at_str = "At 0.00s, actively in motion, inheriting kinetic momentum from the previous shot: "

    raw_action = shot.get("text_en") or shot.get("text") or ""
    adapted_action = sanitize_positive_only(with_scene_surface(raw_action, scene))

    body_text = f"{comp_lock}{at_str}{adapted_action}."
    if any(k in pid for k in ("kiss", "kiss_fondle", "kiss_pin", "kiss_force", "kiss_her")):
        body_text += " (Anatomical lock: lips gently parted 5 mm with subtle contact and natural lip geometry; his left hand is the single hand in frame)."

    if is_penetration and shot.get("size") not in ("face", "cu"):
        body_text += " Snug anatomical junction between penis and vaginal entrance, rhythmic piston strokes of 10 cm clearly readable with elastic skin recoil."

    tail = ""
    if hold_last_second or first_p == "outro_solo":
        tail += " The movement stops and the picture holds still for the last second."
    if index == total_shots - 1 and first_p != "outro_solo":
        tail += f" Final state: Continuous anatomical alignment and stable composition held steady to {dur:.2f}s."

    # 独立成段的 SPEECH: 行（100% 符合《不完全手册》R2/R8 规范）
    speech_line = ""
    if lines:
        is_female_spk = ("女" in speaker or "S1" in speaker or "Subject 1" in speaker)
        spk_tag = "<Subject 1> (S1)" if is_female_spk else "<Subject 2> (S2)"
        listener_tag = "<Subject 2> (S2)" if is_female_spk else "<Subject 1> (S1)"
        spk_pronoun = "her" if is_female_spk else "his"
        listener_pronoun = "his" if is_female_spk else "her"
        muscle_cue = EMOTION_MUSCLE_CUES.get(emotion, EMOTION_MUSCLE_CUES["default"])

        if is_oral and is_female_spk and not effective_vo:
            speech_line = (f"\nSPEECH: <Subject 1> (S1) says in an off-screen voiceover: <d>[Chinese]{lines}</d> "
                           f"while her lips remain completely closed and sealed around the shaft.")
        elif effective_vo:
            speech_line = (f"\nSPEECH: {spk_tag} says in an off-screen voiceover: <d>[Chinese]{lines}</d> "
                           f"while {spk_pronoun} lips remain completely closed.")
        else:
            t_mid_start = max(0.8, round(dur * 0.25, 2))
            t_mid_end = min(dur - 0.5, round(dur * 0.75, 2))
            speech_line = (f"\nSPEECH: From {t_mid_start:.2f}s to {t_mid_end:.2f}s, with {muscle_cue}, "
                           f"{spk_tag} says: <d>[Chinese]{lines}</d> while {listener_tag} keeps {listener_pronoun} lips completely closed and motionless.")

    full_shot_desc = f"{shot_prefix}{body_text}{tail}{speech_line}"
    return sanitize_positive_only(full_shot_desc)


def single_shot_prompt(shot, index, total_shots, dur, size_desc, cam_desc,
                       lines="", speaker="女子A", idea="", scene="hotel suite", pose_names="",
                       female_desc="young woman anchored in <Picture 1>, preserving her exact facial structure, hairstyle, skin tone, and anatomical proportions",
                       male_desc="mature man anchored in <Picture 2>, preserving his exact masculine facial identity, hairstyle, skin tone, and muscular build",
                       scene_props="", emotion="default", voiceover=False, hold_last_second=False,
                       tier="A_two_shot", has_audio_refs=True):
    """
    吞鲸 v4.0 对外唯一装配接口：
    - 输出纯净正向送模提示词（不含 === NEGATIVE ===，杜绝正向反噬）
    - 100% 兼容 R1~R12 全肯定语法与吞鲸六段式结构锚点
    """
    pid = shot.get("pose", "")
    first_p = pid.split("->")[0]
    is_undress = "undress" in first_p
    is_staging = first_p in STAGING_IDS

    header = build_fullref_header(
        dur, "9:16", scene=scene, idea=idea, is_undress=is_undress,
        is_staging=is_staging, tier=tier,
        female_desc=female_desc, male_desc=male_desc, scene_props=scene_props,
        has_audio_refs=has_audio_refs
    )

    shot_body = build_shot_description(
        shot, index, total_shots, dur, size_desc, cam_desc,
        lines=lines, speaker=speaker, scene=scene,
        emotion=emotion, voiceover=voiceover, hold_last_second=hold_last_second
    )

    parts = list(header)
    parts.append("Integrated Multimodal Description:")
    parts.append("integrated_multimodal_description:")
    parts.append(shot_body)
    parts.append("")
    parts.append("Overall Soundscape:")
    parts.append("overall_soundscape: " + build_soundscape_en(scene, is_staging=is_staging))
    parts.append("non_diegetic_music: N/A")
    return "\n".join(parts)


def header_block(dur, aspect="9:16", idea="", scene="hotel suite", pose_names=""):
    return build_fullref_header(dur, aspect, scene=scene, idea=idea)


def footer_block(scene="hotel suite"):
    return [
        "Overall Soundscape:",
        "overall_soundscape: " + build_soundscape_en(scene),
        "non_diegetic_music: N/A",
    ]


def insert_hint(pose_id=""):
    first_p = (pose_id or "").split("->")[0]
    if first_p not in FOREPLAY and first_p not in ORAL_ONLY and first_p not in FINISH_IDS and first_p not in STAGING_IDS and "->" not in (pose_id or ""):
        return " Snug anatomical junction between penis and vaginal entrance, rhythmic piston strokes of 10 cm clearly readable."
    return ""
