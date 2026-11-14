#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 场景自动识别体位引擎 (Tunjing Scene-to-Pose Selector)

解决「肉戏体位被写死默认几招、不从场景出发」的根本症结。

本引擎把「剧本场景描述」翻译成「吞鲸 90 套体位序列」，真正实现
  场景 → 姿势 → 体位提示词(beats/景别/机位/运镜/音效) 的自动链。

核心逻辑：
1. 场景关键词 → 体位 ID 映射（先看剧本写了什么位姿词）
2. 剧本没写位姿词时，按「剧情张力阶段」推断骨架（前戏→交合→换姿→高潮→收尾）
3. 推断时按「场景承托面」匹配体位（床/沙发/桌/墙/椅/车…），不是固定四招
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "..", "references")
POSE_DB = os.path.join(REF, "tunjing_poses_matrix.json")


def load_poses():
    with open(POSE_DB, encoding="utf-8") as f:
        return json.load(f)


# ── 中文体位/姿势词 → 吞鲸体位 ID 映射（剧本写了这些词，就命中对应体位）──
# 键是剧本里常见的中文动作词，值是对应的吞鲸体位 ID（按出现顺序排布）
POSE_KEYWORD_MAP = {
    # 口交系
    "口交": "bj", "深喉": "deepthroat", "舔阴": "cunnilingus", "舔逼": "cunnilingus",
    "乳交": "titjob", "撸管": "handjob", "打桩": "facefuck", "69": "sixty_nine",
    "舔蛋": "ball_lick", "舔龟头": "tip_lick", "颜射拍脸": "penis_slap",
    # 前戏系
    "脱衣": "undress", "揉胸": "breast_rub", "舔乳头": "nipple_lick", "舌吻": "kiss_fondle",
    "接吻": "kiss_pin", "强吻": "kiss_force", "手指": "fingering", "揉阴蒂": "clit_tease",
    "自慰": "solo_masturbate", "指交": "fingering",
    # 交合系（女上位）
    "女上位": "cowgirl", "观音坐莲": "cowgirl", "骑乘": "cowgirl", "倒浇蜡烛": "cowgirl",
    "反向骑乘": "reverse_cowgirl", "背对他": "reverse_cowgirl", "蹲坐骑乘": "squat_cowgirl",
    "坐怀": "lap_sit", "坐怀背对": "lap_sit_back",
    # 交合系（后入）
    "后入": "doggy", "趴跪": "doggy", "狗爬": "doggy", "肛交": "anal", "后庭": "anal",
    "站立后入": "stand_doggy_wall", "撑墙": "stand_doggy_wall", "撑桌": "table_doggy",
    "桌上后入": "table_doggy", "弯腰后入": "stand_bend_doggy", "侧卧后入": "side_spoon",
    # 交合系（传教士/正面）
    "传教士": "missionary", "正面": "missionary", "扛腿": "missionary_legup",
    "面对面": "stand_face_hug", "抬腿插入": "face_insert", "抱起插入": "carry_insert",
    "床边": "bedside_stand", "侧卧面对面": "side_face", "地板": "floor_missionary",
    "POV": "pov_insert", "第一人称": "pov_insert",
    # 其他交合
    "足交": "footjob", "骑脸": "facesit", "臀缝摩擦": "ass_rub",
    # 高潮/收尾
    "内射": "creampie", "射在脸": "cum_face", "射在胸": "cum_chest",
    "射在腹": "cum_belly", "射在臀": "cum_butt",
    "射脸": "cum_face", "射胸": "cum_chest", "射腹": "cum_belly", "射臀": "cum_butt",
    "颜射": "cum_face",
    "喷水": "squirting_climax", "潮吹": "squirting_climax",
}


# ── 场景承托面 → 适合的体位（剧本没写位姿词时，按场景匹配体位）──
# 键是场景词，值是「这个场景最自然的体位 ID 列表」（按剧情推进排序）
SCENE_POSE_MAP = {
    "床": ["undress", "kiss_fondle", "missionary", "cowgirl", "doggy", "creampie"],
    "沙发": ["undress", "kiss_fondle", "sofa_cunni", "lap_sit", "cowgirl", "cum_face"],
    "桌": ["undress", "kiss_pin", "table_doggy", "missionary", "cum_belly"],
    "墙": ["undress", "wall_caging", "stand_doggy_wall", "stand_face_hug", "cum_belly"],
    "椅": ["undress", "lap_sit", "cowgirl_upright", "creampie"],
    "厨房": ["undress", "kiss_fondle", "stand_bend_doggy", "creampie"],
    "浴室": ["undress", "breast_rub", "stand_doggy_wall", "cum_butt"],
    "车": ["undress", "kiss_force", "cowgirl", "creampie"],
    "窗": ["undress", "kiss_pin", "stand_doggy_wall", "cum_belly"],
    "地毯": ["undress", "kiss_fondle", "floor_missionary", "cowgirl", "creampie"],
    "地面": ["undress", "kiss_fondle", "floor_missionary", "doggy", "creampie"],
    "阳台": ["undress", "kiss_pin", "stand_doggy_wall", "cum_belly"],
}


def detect_scene_key(scene_text):
    """从场景描述里识别承托面关键词"""
    for key in ("厨房", "浴室", "阳台", "地毯", "沙发", "桌", "墙", "椅", "车", "窗", "地面", "床"):
        if key in scene_text:
            return key
    return "床"


def select_poses_from_script(script_text, scene_text=""):
    """
    从剧本自动识别体位序列：
    1. 先按 POSE_KEYWORD_MAP 找剧本里明确写的中文体位词（按出现顺序）
    2. 没写体位词时，按场景承托面匹配 SCENE_POSE_MAP
    返回 (pose_ids, 命中来源)
    """
    poses = load_poses()
    found = []
    found_source = []

    # 1) 剧本明确写了体位词
    txt = script_text or ""
    for kw, pid in POSE_KEYWORD_MAP.items():
        if kw in txt and pid != "shower":
            # 按关键词在剧本中的位置排序
            found.append((txt.find(kw), pid, kw))

    if found:
        found.sort()
        ids = [p for _, p, _ in found]
        # 去相邻重复
        dedup = []
        for p in ids:
            if not dedup or dedup[-1] != p:
                dedup.append(p)
        return dedup, "剧本显式体位词"

    # 2) 剧本没写体位词 → 按场景承托面匹配
    scene_key = detect_scene_key(scene_text or txt)
    scene_poses = SCENE_POSE_MAP.get(scene_key, SCENE_POSE_MAP["床"])
    # 只保留真实存在的体位
    valid = [p for p in scene_poses if p in poses]
    return valid, f"场景承托面匹配({scene_key})"


def select_poses_with_staging(script_text, scene_text=""):
    """
    完整链路：文戏开场原语 + 场景自动识别体位 + 收尾
    """
    from tunjing_dialogue import resolve_intent

    sex_ids, source = select_poses_from_script(script_text, scene_text)

    # 文戏开场：自动识别戏剧意图
    intent = resolve_intent(script_text)
    staging = {
        "confront": ["env_establish", "srs_male", "srs_female"],
        "reveal": ["env_establish", "blocking_2s", "srs_female"],
        "breakdown": ["env_establish", "srs_female"],
        "tease": ["env_establish", "blocking_2s"],
    }.get(intent, ["env_establish", "srs_male", "srs_female"])

    full = staging + sex_ids + (["outro_solo"] if sex_ids else [])
    # 去相邻重复
    dedup = []
    for p in full:
        if not dedup or dedup[-1] != p:
            dedup.append(p)
    return dedup, source, intent


def list_pose_prompts(pose_ids):
    """按体位 ID 列出对应的体位提示词摘要（beats 第一拍 + 景别 + 音效）"""
    poses = load_poses()
    result = []
    for pid in pose_ids:
        p = poses.get(pid)
        if not p:
            continue
        result.append({
            "id": pid,
            "name": p.get("nameZh", pid),
            "framing": p.get("framingZh", ""),
            "beats_first": (p.get("beatsZh") or [""])[0][:60],
            "sfx": p.get("sfxZh", []),
        })
    return result


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="吞鲸场景自动识别体位引擎")
    ap.add_argument("--script", default="", help="剧本文件路径（或直接给一段场景文本）")
    ap.add_argument("--scene", default="", help="场景名（如 酒店客房/沙发/厨房）")
    ap.add_argument("--poses", action="store_true", help="列出识别出的体位提示词摘要")
    args = ap.parse_args()

    text = args.script
    if os.path.isfile(args.script):
        with open(args.script, encoding="utf-8") as f:
            text = f.read()

    ids, source, intent = select_poses_with_staging(text, args.scene)
    print(f"识别来源: {source} | 文戏意图: {intent}")
    print(f"体位序列: {','.join(ids)}")
    if args.poses:
        print("\n各体位提示词摘要:")
        for r in list_pose_prompts(ids):
            print(f"  [{r['id']}] {r['name']} | {r['framing']} | 音效:{r['sfx']}")
