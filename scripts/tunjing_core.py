#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 提示词装配共享核心 (Tunjing Assembly Core)

唯一装配实现，供 tunjing_scene.py 与 tunjing_storyboard.py 共同调用，杜绝双份定义。
1. 装配结构 1:1 对齐《大人的工作台》buildOfficialH3Prompt() 六段式
2. 完整移植工作台 withSceneSurface() 与 h3SceneSfxZh()，根据传入的 scene 自动把动作与声场里的“床/床单/床板”动态改写为目标场地（办公桌/沙发/浴室/车内/墙边/地面等），彻底根绝跨场景穿帮！
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

# ── 1:1 移植自工作台 h3-app.js 的 13 类场景承托面与声学映射 ──
SURFACE_PROFILES = {
    "bed":     {"noun": "床", "on": "在床上", "brace": "撑床", "grab": "抓床单", "edge": "床沿", "sitEdge": "坐在床沿", "pad": "床单", "lie": "仰卧在床上", "kneel": "跪在床上", "sfx": "床板轻响"},
    "hotel":   {"noun": "酒店床", "on": "在酒店床上", "brace": "撑酒店床", "grab": "抓酒店床单", "edge": "酒店床沿", "sitEdge": "坐在酒店床沿", "pad": "酒店床品", "lie": "仰卧在酒店床上", "kneel": "跪在酒店床上", "sfx": "床板轻响"},
    "sofa":    {"noun": "沙发", "on": "在沙发上", "brace": "撑沙发", "grab": "抓沙发垫", "edge": "沙发沿", "sitEdge": "坐在沙发边缘", "pad": "沙发软垫", "lie": "仰卧在沙发上", "kneel": "跪在沙发上", "sfx": "沙发轻响"},
    "chair":   {"noun": "椅子", "on": "在椅子上", "brace": "撑椅面或扶手", "grab": "抓椅背或扶手", "edge": "椅沿", "sitEdge": "坐在椅子上", "pad": "椅面", "lie": "坐靠在椅子上", "kneel": "跨跪在椅面上", "sfx": "椅子轻响"},
    "kitchen": {"noun": "料理台", "on": "在料理台面上", "brace": "撑台面", "grab": "抓台沿", "edge": "台沿", "sitEdge": "坐在台沿边缘", "pad": "台面", "lie": "仰靠在台面上", "kneel": "趴在台面上", "sfx": "台面轻响"},
    "bath":    {"noun": "浴室地面", "on": "在浴室里", "brace": "撑瓷砖墙或地面", "grab": "扶浴室墙面", "edge": "墙角", "sitEdge": "坐在浴室矮台边缘", "pad": "湿润瓷砖", "lie": "仰靠在浴室台边", "kneel": "跪在浴室地面上", "sfx": "水声与瓷砖回响"},
    "desk":    {"noun": "长桌", "on": "在桌面上", "brace": "撑桌面", "grab": "抓桌沿", "edge": "桌沿", "sitEdge": "坐在桌沿边缘", "pad": "桌面", "lie": "仰靠在桌面上", "kneel": "趴在桌面上", "sfx": "桌面轻响"},
    "wall":    {"noun": "墙边", "on": "靠墙", "brace": "双手撑墙", "grab": "扶墙面", "edge": "墙边", "sitEdge": "背靠墙", "pad": "墙面", "lie": "背贴墙面", "kneel": "靠墙跪立", "sfx": ""},
    "window":  {"noun": "窗台", "on": "在落地窗前", "brace": "撑窗台或玻璃", "grab": "扶窗框", "edge": "窗台沿", "sitEdge": "坐在窗台边缘", "pad": "窗台", "lie": "靠在窗台边", "kneel": "跪在窗台前", "sfx": ""},
    "rug":     {"noun": "地毯", "on": "在地毯上", "brace": "撑地毯", "grab": "抓地毯", "edge": "地毯边", "sitEdge": "坐在地毯上", "pad": "地毯", "lie": "仰卧在地毯上", "kneel": "跪在地毯上", "sfx": ""},
    "floor":   {"noun": "地面", "on": "在地面上", "brace": "撑地面", "grab": "撑地面", "edge": "地面", "sitEdge": "坐在地面上", "pad": "地面", "lie": "仰卧在地面上", "kneel": "跪在地面上", "sfx": ""},
    "car":     {"noun": "车内座椅", "on": "在车内座椅上", "brace": "撑座椅或扶手", "grab": "抓座椅靠背", "edge": "座椅沿", "sitEdge": "坐在车内座椅上", "pad": "真皮座椅", "lie": "仰靠在车座上", "kneel": "跪跨在车座上", "sfx": "座椅轻响"},
    "balcony": {"noun": "露台栏杆", "on": "在露台上", "brace": "扶栏杆或撑地", "grab": "抓紧栏杆", "edge": "栏杆边", "sitEdge": "坐在露台矮沿上", "pad": "露台地面", "lie": "仰靠在露台上", "kneel": "跪在露台地面上", "sfx": ""},
}


def detect_scene_id(scene_name):
    """根据用户传入的场景名自动识别工作台场地类型，彻底告别硬编码卧室/床"""
    s = (scene_name or "").lower()
    if any(k in s for k in ("车", "座舱", "后座", "car")):
        return "car"
    if any(k in s for k in ("浴", "淋浴", "温泉", "汤池", "bath", "shower")):
        return "bath"
    if any(k in s for k in ("沙发", "茶几", "休息室", "客厅", "包厢", "sofa")):
        return "sofa"
    if any(k in s for k in ("椅", "王座", "宝座", "老板椅", "chair", "throne")):
        return "chair"
    if any(k in s for k in ("厨", "料理", "吧台", "kitchen", "bar")):
        return "kitchen"
    if any(k in s for k in ("窗", "落地窗", "window")):
        return "window"
    if any(k in s for k in ("阳台", "露台", "天台", "balcony")):
        return "balcony"
    if any(k in s for k in ("墙", "走廊", "巷", "电梯", "楼梯", "试衣间", "wall", "elevator")):
        return "wall"
    if any(k in s for k in ("地毯", "毯", "榻榻米", "rug")):
        return "rug"
    if any(k in s for k in ("地面", "地板", "地牢", "密室", "训练室", "祭坛", "floor")):
        return "floor"
    if any(k in s for k in ("办公", "书房", "桌", "案几", "讲台", "会议", "实验室", "诊室", "desk", "office")):
        return "desk"
    if any(k in s for k in ("酒店", "宾馆", "套房", "hotel")):
        return "hotel"
    return "bed"


def with_scene_surface(act_text, scene_name):
    """复刻工作台 withSceneSurface(act)：当场景不是床时，把动作里的床/床单/床沿全部替换为当前场景承托面"""
    if not act_text:
        return act_text
    sc_id = detect_scene_id(scene_name)
    if sc_id in ("bed", "hotel"):
        return act_text
    loc = SURFACE_PROFILES.get(sc_id, SURFACE_PROFILES["desk"])
    out = str(act_text)
    reps = [
        ("坐在床的边缘", loc["sitEdge"]),
        ("坐在床边缘", loc["sitEdge"]),
        ("坐在床沿边缘", loc["sitEdge"]),
        ("坐在床沿", loc["sitEdge"]),
        ("坐床沿", loc["sitEdge"]),
        ("双手撑床或抓床单", "双手" + loc["brace"] + "或" + loc["grab"]),
        ("撑床或抓床单", loc["brace"] + "或" + loc["grab"]),
        ("双手撑在床面上", "双手" + loc["brace"]),
        ("双手撑床面上", "双手" + loc["brace"]),
        ("双手撑床", "双手" + loc["brace"]),
        ("手撑床", "手" + loc["brace"]),
        ("撑床面", loc["brace"]),
        ("撑床", loc["brace"]),
        ("抓紧床单", loc["grab"]),
        ("抓床单", loc["grab"]),
        ("抠床单", loc["grab"]),
        ("按床单", loc["grab"]),
        ("床单枕头", loc["pad"]),
        ("床单褶皱", loc["pad"]),
        ("床单", loc["pad"]),
        ("枕头", loc["pad"]),
        ("床垫", loc["pad"]),
        ("床面", loc["pad"]),
        ("床沿", loc["edge"]),
        ("床头", loc["edge"]),
        ("床板", loc["edge"]),
        ("仰卧在床上", loc["lie"]),
        ("躺在床上", loc["lie"]),
        ("跪在床上", loc["kneel"]),
        ("趴跪床上", "趴跪在" + loc["pad"] + "上"),
        ("趴在床上", loc["kneel"].replace("跪", "趴")),
        ("在床上", loc["on"]),
        ("床上", loc["on"].replace("在", "")),
    ]
    for old, new in reps:
        out = out.replace(old, new)
    return out


def build_soundscape_zh(scene_name):
    """复刻工作台 h3SceneSfxZh：根据当前场景动态生成底层环境声，杜绝在办公室/浴室里出现床板声"""
    sc_id = detect_scene_id(scene_name)
    loc = SURFACE_PROFILES.get(sc_id, SURFACE_PROFILES["bed"])
    surf_sfx = loc.get("sfx", "")
    if surf_sfx:
        tail = f"皮肤拍击、湿润声与{surf_sfx}压在底层。"
    else:
        tail = "皮肤拍击与湿润水声压在底层。"
    return f"室内安静底噪持续。湿润皮肤接触与节奏抽插声清晰可闻，皮肤拍击夹杂其中。{tail}"


def load_poses():
    with open(os.path.join(REF, "workbench_poses_matrix.json"), encoding="utf-8") as f:
        return json.load(f)


def load_recipes():
    with open(os.path.join(REF, "transition_recipes.json"), encoding="utf-8") as f:
        return json.load(f)


def header_block(dur, aspect, idea="", scene="当前场景", pose_names=""):
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


def footer_block(scene="当前场景"):
    return [
        "overall_soundscape: " + build_soundscape_zh(scene),
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
                       lines="", idea="", scene="当前场景", pose_names=""):
    """
    为「拆镜表」中的单个镜头生成完整可送模提示词（含自动承托面与声场适配）。
    """
    parts = header_block(dur, "9:16", idea=idea, scene=scene, pose_names=pose_names)

    if index == 0:
        head = "[Shot 1] Live-action cinematic."
    else:
        head = "[Shot 1] At 0.00s, this clip begins directly at this beat."

    adapted_text = with_scene_surface(shot["text"], scene)
    body = f"景别：{size_desc}。机位：{cam_desc}。{adapted_text}"
    body += insert_hint(shot.get("pose", ""))

    if lines:
        body += f" 女子A says: <d>[Chinese]{lines}</d>."

    if index == total_shots - 1:
        body += f" Final state: 人物身份不漂移，交合处仍紧密贴合、比例自然，构图稳定收住到 {dur:.2f}s。"

    parts.append("integrated_multimodal_description:")
    parts.append(f"{head} {body}")
    parts.append("")
    parts.extend(footer_block(scene))
    return "\n".join(parts)
