#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 文戏镜头语言引擎 (Tunjing Dialogue Cinematography Engine)

解决「发散型大模型不会设计文戏镜头语言」的根本症结：
肉戏有据可查（体位代号 -> 自动出景别/机位/运镜），但文戏一直靠模型自由发挥，
而发散型大模型没有导演创造力，只能凭空瞎编景别机位，导致文戏拍成「站桩干聊、机位乱跳、镜头语言空洞」。

本引擎把文戏的「戏剧意图」翻译成「景别 + 机位 + 运镜 + 剪接节奏」的确定性配方，
让文戏也变成「查字典」就能对的机械装配，模型不需要自己有镜头语言天赋。

核心：戏剧意图(Intent) -> 镜头配方(Shot Recipe)，8 类文戏意图全查表覆盖。
"""

# 文戏镜头语言配方库：意图 -> (景别, 机位, 运镜, 剪接节奏说明, 英文送模描述)
# 所有常量 100% 复用 tunjing_core 的英文语义，零重复定义。
DIALOGUE_SHOT_RECIPES = {
    # 1. 建立/交代环境 —— 定位空间与人物位置关系
    "establish": {
        "size": "wide", "cam": "pull_reveal",
        "zh": "全景交代空间轴线与人物位置，镜头缓拉揭示环境",
        "en": "wide establishing shot revealing left-to-right spatial axis and character placement, slow dolly pull-back over three seconds",
        "cut": "慢切（3s 以上留白，让观众看清空间）",
    },
    # 2. 双人对峙/施压 —— 权力关系的正面交锋
    "confront": {
        "size": "cu", "cam": "ots_depth",
        "zh": "过肩近景，前景一方虚焦肩部占位，焦点落在被压一方脸上",
        "en": "over-the-shoulder close-up with soft-focus foreground shoulder occupying 15% frame edge, focus locked on the pressured face",
        "cut": "切正反打，一施压一承受，视线互补对撞",
    },
    # 3. 单人反应/内心 —— 一句话后的情绪反打
    "reaction": {
        "size": "face", "cam": "high_downward",
        "zh": "面部特写，俯拍脆弱承受，锁定眼神/咬唇/微表情",
        "en": "tight facial close-up, subtle high-angle downward, locked on eyes, jaw, and lip micro-expressions",
        "cut": "紧跟对白后 0.5s 反应延迟，留情绪余韵",
    },
    # 4. 递进压迫 —— 情绪/权力逐级升级
    "escalate": {
        "size": "mcu", "cam": "push_tension",
        "zh": "中近景慢推，镜头随情绪压迫向前逼近",
        "en": "medium close-up with slow dolly push-in sliding forward 15 cm over four seconds tightening on the tense subject",
        "cut": "连续两镜递进推入，景别逐级收紧（wide→mcu→cu）",
    },
    # 5. 揭示/摊牌 —— 关键信息或真相揭露
    "reveal": {
        "size": "mcu", "cam": "arc_subtle",
        "zh": "中近景微弧偏转，制造背景视差揭示关键信息",
        "en": "medium close-up with subtle 8-degree lateral dolly arc shifting sideways for parallax reveal",
        "cut": "先留白再揭示，镜头缓慢偏转带出信息",
    },
    # 6. 暧昧挑逗 —— 肢体与视线拉扯
    "tease": {
        "size": "cu", "cam": "handheld_breath",
        "zh": "近景手持呼吸微晃，跟随暧昧肢体与视线节奏",
        "en": "intimate close perspective, organic handheld camera with subtle 2 cm breathing micro-sway synchronized with body rhythm",
        "cut": "软切，呼吸感手持带出暧昧张力",
    },
    # 7. 冷场/对峙僵持 —— 两人静止互瞪
    "standoff": {
        "size": "wide", "cam": "static_side",
        "zh": "全景90度侧向定轴，两人左右僵持，靠微表情与呼吸推进",
        "en": "wide side profile angle, tripod locked, both subjects framed left-to-right in a tense standoff",
        "cut": "长镜头慢切，僵持感靠演员微动态而非机位变化",
    },
    # 8. 情绪崩溃/宣泄 —— 人物防线崩塌
    "breakdown": {
        "size": "face", "cam": "pull_reveal",
        "zh": "面部特写缓拉，随情绪宣泄逐渐拉远抽离",
        "en": "tight facial close-up with slow dolly pull-back retreating 18 cm revealing the emotional collapse",
        "cut": "从特写缓拉到中景，情绪放大人退场",
    },
}

# 意图中文别名 -> 标准意图键（供模型/用户自然语言输入解析）
INTENT_ALIAS = {
    "建立": "establish", "交代": "establish", "环境": "establish", "开场": "establish",
    "对峙": "confront", "施压": "confront", "争吵": "confront", "逼迫": "confront", "质问": "confront",
    "反应": "reaction", "反打": "reaction", "内心": "reaction", "表情": "reaction", "沉默": "reaction",
    "递进": "escalate", "升级": "escalate", "压迫": "escalate", "逼近": "escalate",
    "揭示": "reveal", "摊牌": "reveal", "揭露": "reveal", "真相": "reveal", "坦白": "reveal",
    "挑逗": "tease", "暧昧": "tease", "拉扯": "tease", "勾引": "tease",
    "僵持": "standoff", "冷场": "standoff", "冷对峙": "standoff", "互瞪": "standoff",
    "崩溃": "breakdown", "宣泄": "breakdown", "破防": "breakdown", "哭": "breakdown",
}


def resolve_intent(intent_text):
    """把任意中文意图描述解析为标准意图键，默认 confront（对峙是最常见的文戏）"""
    t = (intent_text or "").strip()
    # 精确匹配
    if t in DIALOGUE_SHOT_RECIPES:
        return t
    # 别名匹配
    for alias, key in INTENT_ALIAS.items():
        if alias in t:
            return key
    return "confront"


def recipe_for(intent):
    """按意图取镜头配方，未识别意图回退对峙配方"""
    key = resolve_intent(intent)
    r = DIALOGUE_SHOT_RECIPES.get(key, DIALOGUE_SHOT_RECIPES["confront"])
    return key, r


def list_intents():
    """列出全部文戏意图配方，供模型/用户查阅"""
    return DIALOGUE_SHOT_RECIPES


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="吞鲸文戏镜头语言引擎")
    ap.add_argument("--intent", default="", help="文戏戏剧意图（如 对峙/揭示/挑逗/崩溃/建立/反应/递进/僵持）")
    ap.add_argument("--list", action="store_true", help="列出全部 8 类文戏镜头配方")
    args = ap.parse_args()

    if args.list:
        for key, r in DIALOGUE_SHOT_RECIPES.items():
            print(f"{key:12s} | {r['size']:6s} | {r['cam']:14s} | {r['zh']} | 剪接：{r['cut']}")
    elif args.intent:
        key, r = recipe_for(args.intent)
        print(f"意图 [{args.intent}] -> 标准键 [{key}]")
        print(f"  景别: {r['size']}  机位: {r['cam']}")
        print(f"  中文: {r['zh']}")
        print(f"  英文送模: {r['en']}")
        print(f"  剪接: {r['cut']}")
    else:
        ap.print_help()
