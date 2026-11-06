#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 床戏动作实时响应引擎 (Tunjing Pose Real-time Resolver)

用法：在创作到床戏环节时，直接喊动作需求，本引擎 1:1 从吞鲸宝典内置引擎矩阵
返回该动作的完整送模提示词（Framing + 压油 + Beats + Line）。

命令行：
    python tunjing_resolver.py "女口交"          # 单个动作
    python tunjing_resolver.py "扣女穴"          # 指插
    python tunjing_resolver.py "女上位"          # 骑乘
    python tunjing_resolver.py --list            # 列出全部 50 套可用动作
    python tunjing_resolver.py --scene "..."     # 整段床戏剧本自动拆解生成全部提示词
"""

import json
import sys
import os
import re

MATRIX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "references", "tunjing_poses_matrix.json")

# 恒定正向压油模板（吞鲸引擎 Node 328 零化负向的物理真相：靠正向肯定句压油）
DE_OIL = ("authentic matte velvet skin finish, powdered dry texture, natural human skin "
          "with visible fine pores and subtle imperfections, soft subsurface scattering "
          "without surface reflection, non-greasy complexion, heavily diffused soft ambient light, "
          "zero hard directional light, 35mm film grain, photorealistic anatomy, "
          "strictly zero extra limbs and zero fused body parts")

# 中文/口语动作别名 -> 矩阵 pose id（关键：把用户口语映射到吞鲸引擎原版 ID）
ALIAS = {
    # 口爱
    "女口交": "bj", "口交": "bj", "含": "bj", "吹": "bj", "跪口": "bj", "跪姿口交": "bj",
    "深喉": "deepthroat", "喉咙": "deepthroat", "吞吐": "deepthroat",
    "口爆": "facefuck", "打桩口": "facefuck", "按头": "head_thrust",
    "69": "sixty_nine", "舔蛋": "ball_lick", "舔龟头": "tip_lick",
    # 指插/前戏
    "扣女穴": "fingering", "指插": "fingering", "扣穴": "fingering", "手指": "fingering",
    "揉阴蒂": "clit_tease", "揉豆": "clit_tease",
    "舔女穴": "cunnilingus", "舔逼": "cunnilingus", "口女": "cunnilingus", "舔阴": "cunnilingus",
    "揉胸": "breast_rub", "摸胸": "breast_rub", "揉奶": "breast_rub", "摸奶": "breast_rub",
    "舔乳头": "nipple_lick", "舔奶头": "nipple_lick",
    "撸管": "handjob", "打飞机": "handjob", "乳交": "titjob",
    "抚摸": "breast_rub", "爱抚": "breast_rub",
    # 主力交合
    "传教士": "missionary", "正常位": "missionary", "第一体位": "missionary",
    "后入": "doggy", "趴跪后入": "doggy", "狗爬": "doggy", "后人": "doggy", "后入位": "doggy",
    "桌上后入": "table_doggy", "站后入": "stand_doggy_wall", "撑墙后入": "stand_doggy_wall",
    "女上位": "cowgirl", "骑乘": "cowgirl", "女上": "cowgirl", "上坐": "cowgirl",
    "反向骑乘": "reverse_cowgirl", "背骑": "reverse_cowgirl",
    "抱起插入": "carry_insert", "抱插": "carry_insert",
    "肛交": "anal", "后庭": "anal", "菊花": "anal",
    "侧卧": "side_face", "侧位": "side_face",
    # 绝顶清算
    "射屁股": "cum_butt", "射在屁股上": "cum_butt", "射臀": "cum_butt", "颜射": "cum_face",
    "射脸": "cum_face", "射胸": "cum_chest", "内射": "creampie",
    # 亲吻
    "强吻": "kiss_force", "按墙强吻": "kiss_pin", "湿吻": "kiss_fondle", "舌吻": "kiss_fondle",
    # 导演结构性动作词（默认落到约定动作，避免漏识别）
    "前戏": "kiss_fondle", "破防": "kiss_pin", "脱衣": "undress",
    "第一个位": "missionary", "第一体位": "missionary", "换体位": "cowgirl", "体位": "missionary",
}


def load_matrix():
    with open(MATRIX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve(query):
    """把一句中文动作描述解析成 (pose_id, matrix_entry)"""
    m = load_matrix()
    q = query.strip()
    # 1) 精确别名
    if q in ALIAS:
        pid = ALIAS[q]
        return pid, m.get(pid)
    # 2) 模糊包含
    for alias, pid in ALIAS.items():
        if alias in q:
            return pid, m.get(pid)
    # 3) 直接 id / 中英文名
    for pid, it in m.items():
        if pid == q:
            return pid, it
        if it.get("nameZh") == q or it.get("nameEn", "").lower() == q.lower():
            return pid, it
    return None, None


def render_prompt(pid, entry):
    """把矩阵条目渲染成完整可直接送模的 Ref2V 提示词"""
    lines = []
    lines.append(f"### [{pid}] {entry.get('nameZh','')} ({entry.get('nameEn','')})")
    framing = entry.get("framingEn") or entry.get("framingZh", "")
    lines.append(f"\n[Framing] {framing}")
    lines.append(f"[Skin & Lighting] {DE_OIL}")
    beats = entry.get("beatsEn") or []
    if beats:
        lines.append("[Momentum]")
        lines.append(" - ".join(beats))
    sfx = entry.get("sfxEn") or []
    if sfx:
        lines.append(f"[SFX] {', '.join(sfx) if isinstance(sfx, list) else sfx}")
    line = entry.get("lineZh") or ""
    if line:
        lines.append(f"[Line] <d>[Chinese]{line}</d>")
    return "\n".join(lines)


def resolve_scene(text):
    """整段床戏剧本 -> 按顺序自动拆解出每个动作的提示词"""
    m = load_matrix()
    # 按常见标点/换行切分动作片段
    segs = re.split(r'[，。；;、\n]+', text)
    results = []
    for seg in segs:
        seg = seg.strip()
        if not seg:
            continue
        pid, entry = resolve(seg)
        if pid and entry:
            results.append((seg, pid, render_prompt(pid, entry)))
        else:
            results.append((seg, None, f"[!] 无法识别动作：{seg}（请查 --list 确认）"))
    return results


def main():
    m = load_matrix()
    if "--list" in sys.argv:
        print(f"吞鲸宝典 · 可实时响应的 {len(m)} 套动作清单：")
        for pid, it in m.items():
            print(f"  {pid:20s} | {it.get('nameZh',''):12s} | {it.get('nameEn','')}")
        return

    if "--scene" in sys.argv:
        idx = sys.argv.index("--scene")
        scene = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else ""
        print("=" * 60)
        print("🐳 吞鲸宝典 · 整段床戏自动拆解")
        print(f"剧本片段：{scene}")
        print("=" * 60)
        for seg, pid, prompt in resolve_scene(scene):
            if pid:
                print(f"\n▶ 动作「{seg}」")
                print(prompt)
            else:
                print(prompt)
        return

    if len(sys.argv) < 2:
        print("用法：python tunjing_resolver.py 「动作名」 或 --scene 「整段剧本」 或 --list")
        return

    query = sys.argv[1]
    pid, entry = resolve(query)
    if not entry:
        print(f"[!] 未命中动作「{query}」，请用 --list 查看可用动作或换个说法。")
        return
    print("=" * 60)
    print("🐳 吞鲸宝典 · 实时响应")
    print(f"需求「{query}」→ 命中吞鲸标准动作 [{pid}]")
    print("=" * 60)
    print(render_prompt(pid, entry))


if __name__ == "__main__":
    main()
