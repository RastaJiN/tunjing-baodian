#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 冲突发动机 (Tunjing Drama Engine — 剧作核心心脏)

解决宝典「只会拍、不会写戏」的根本缺环，实现「能文能武」统一：
正经剧靠它生出独立成立的戏（情绪/反转/和解）；成人剧靠它把人牢牢留住再推向肉戏。

核心公式（每场戏的发动机）：
    目标 × 反对 × 转向 × 退出 = 一场有筋骨有肌肉的戏

三条筋骨（缺一即"没戏"）：
    1. 晚进早出 —— 从冲突正烧的地方切入，局面实质变化处切出
    2. 可表演行动 —— 内在心理必须落成"改变空间/物件/姿态"的动作，不停在"眼神复杂"
    3. 空间/物件/反应组织冲突 —— 谁挡住出口、物件在谁可触达范围、谁能看见谁只听见

这是从 drama-skills script-craft.md「目标/反对/转向 + 可表演动词 + 晚进早出 + 物证戏」
内化的吞鲸原生，编号、出处全部归零，只留可复用的工业剧作法。
"""


# ── 冲突发动机的核心四段：目标、反对、转向、退出 ──
# 每场戏必须走完这四段才有戏；缺"转向"或"退出"就是站桩闲聊。

GOAL_VERBS = {
    # 目标必须是「能作用于现场的可见动作」，不是抽象心理
    "拿回": "让对方当众把{obj}交出来",
    "保住": "在{deadline}前守住{obj}不被{opponent}拿走",
    "逼问": "迫使对方当众承认{secret}",
    "阻止": "赶在对方{action}之前拦下",
    "索取": "拿到{obj}而不暴露{motive}",
    "掌控": "让对方主动服从{command}",
    "勾引": "让对方先踏出第一步，事后还能全身而退",
    "羞辱": "当众让对方下不来台",
    "隐瞒": "让对方直到最后都不知道{secret}",
    "反击": "用对方手上的把柄反将一军",
}

OPPOSITION_MOVES = {
    # 反对不是简单说"不"，而是这些有筹码的招
    "重新定义题目": "把话题引到对自己有利的定义上，不接对方原话",
    "交换条件": "提出一个对方付不起或不愿付的代价",
    "拿走资源": "抽走对方达成目标所依赖的时间/物件/身份",
    "质疑来源": "直指对方证据或说辞的来源不可信",
    "拉第三人": "借在场的第三方施压，或把公开代价抬高",
    "表面答应改条件": "口头应下，但在执行条件上做手脚",
    "反客为主": "把对方的词反过来用，逼对方自证",
    "沉默施压": "不说话，用停顿和目光迫使对方继续暴露",
}

TURN_POINTS = {
    # 转向 = 局面发生实质变化后，人物不能按原计划行事，必须有新的事实/筹码/关系/决定
    "亮出证据": "一方亮出此前藏住的物证/字据，当场推翻对方说辞",
    "筹码易主": "原本在甲手里的筹码，转到了乙手上",
    "身份反转": "一方暴露真实身份或立场，关系瞬间改变",
    "代价落地": "一个不可逆的代价当场坐实（签了字、砸了东西、说了狠话）",
    "联盟破裂": "原本的盟友当场倒戈或划清界限",
    "把柄公开": "私下被藏的丑事被当众揭开",
}

EXIT_STATES = {
    # 退出 = 局面实质变化后的落点，六项事实要可读
    "关系宣判": "一句台词宣判两人关系的新状态",
    "物件易主": "关键物件从一人转到另一人手里",
    "离场": "一人带着决定转身离开",
    "门锁落定": "门/锁的声响封死一条路，逼出下一场",
    "独自面对": "一人被留在原地面对刚炸开的后果",
    "沉默对望": "两人停在对峙的沉默里，谁都没赢",
}


# ── 五类经典冲突原型（正经剧 + 成人剧通用的"戏"的骨架）──
CONFLICT_ARCHETYPES = {
    "夺物": {
        "name": "争夺一件有归属的关键物件",
        "goal": "把{obj}拿到手 / 或保住{obj}",
        "scene_hint": "物件在谁可触达范围、谁能接近它、谁能看见它",
        "turn": "物件易主 / 露出真伪 / 被第三方截胡",
    },
    "揭密": {
        "name": "一个不能公开的秘密正在被逼近",
        "goal": "把{secret}藏到最后一刻 / 或逼对方吐露{secret}",
        "scene_hint": "谁在场谁不能听、哪句话会露馅",
        "turn": "把柄公开 / 身份反转",
    },
    "逼选": {
        "name": "两难选择，两个方向都活着",
        "goal": "逼对方在两个代价间二选一",
        "scene_hint": "为什么不能两个都要（时间/资源/身份/公开代价封死）",
        "turn": "选 A 的代价落地 / 选 B 的代价落地",
    },
    "摊牌": {
        "name": "隐忍已久的关系/立场当面摊开",
        "goal": "让对方承认 / 或让对方先低头",
        "scene_hint": "谁先忍不住、哪句话是底线",
        "turn": "关系宣判 / 联盟破裂",
    },
    "破防": {
        "name": "攻破对方层层设防的心理防线",
        "goal": "逼出对方最不愿露出的情绪/真实想法",
        "scene_hint": "对方的破绽在哪、哪句试探会让他露馅",
        "turn": "代价落地 / 情绪崩溃",
    },
}


def build_conflict_beats(archetype, obj="", secret="", deadline="", opponent="对方", action="", motive="", command=""):
    """
    冲突发动机主入口：给定冲突原型和要素，生成「目标-反对-转向-退出」四段戏的骨架。
    返回 dict，供剧本 / 分镜 / 提示词下游使用。
    """
    a = CONFLICT_ARCHETYPES.get(archetype, CONFLICT_ARCHETYPES["夺物"])
    goal_tmpl = a["goal"]
    try:
        goal = goal_tmpl.format(obj=obj, secret=secret, deadline=deadline,
                                opponent=opponent, action=action, motive=motive, command=command)
    except KeyError:
        goal = goal_tmpl

    return {
        "archetype": archetype,
        "name": a["name"],
        "goal": goal,
        "scene_hint": a["scene_hint"],
        "turn": a["turn"],
        "opposition_moves": list(OPPOSITION_MOVES.keys()),
        "turn_points": list(TURN_POINTS.keys()),
        "exit_states": list(EXIT_STATES.keys()),
    }


def list_archetypes():
    """列出全部冲突原型"""
    return CONFLICT_ARCHETYPES


def explain_engine():
    """输出冲突发动机的完整方法论（供模型加载时理解"戏从哪来"）"""
    return {
        "engine": "目标 × 反对 × 转向 × 退出",
        "goal_rule": "目标必须是能作用于现场的可见动作，不是抽象心理（'想被尊重'→'让对方当众承认记录被改过'）",
        "opposition_rule": "反对不是简单说'不'，是有筹码的招（换条件、拿资源、质疑来源、拉第三人、反客为主）",
        "turn_rule": "转向后人物不能按原计划行事，必须有新事实/筹码/关系/决定",
        "exit_rule": "退出=局面实质变化，六项事实可读：谁在哪、谁知道什么、物件归属、关系变化、动作是否不可撤回",
        "bone1": "晚进早出：从冲突正烧处切入，实质变化处切出（不要从进门换鞋写起）",
        "bone2": "可表演行动：'眼神复杂'→'把免责页往下一折只推签名栏，食指压住折痕'",
        "bone3": "空间物件反应：谁挡出口、物件在谁可触达、谁能看谁能听、公开私密边界",
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="吞鲸冲突发动机（剧作核心）")
    ap.add_argument("--archetype", default="", help="冲突原型：夺物/揭密/逼选/摊牌/破防")
    ap.add_argument("--obj", default="", help="关键物件")
    ap.add_argument("--secret", default="", help="秘密")
    ap.add_argument("--list", action="store_true", help="列出全部冲突原型")
    ap.add_argument("--explain", action="store_true", help="输出冲突发动机完整方法论")
    args = ap.parse_args()

    if args.list:
        for k, v in CONFLICT_ARCHETYPES.items():
            print(f"{k:8s} | {v['name']}")
    elif args.explain:
        for k, v in explain_engine().items():
            print(f"{k}: {v}")
    elif args.archetype:
        b = build_conflict_beats(args.archetype, obj=args.obj, secret=args.secret)
        print(f"冲突原型 [{b['archetype']}] {b['name']}")
        print(f"  目标: {b['goal']}")
        print(f"  场景要点: {b['scene_hint']}")
        print(f"  转向落点: {b['turn']}")
        print(f"  反对招法: {', '.join(b['opposition_moves'])}")
        print(f"  退出状态: {', '.join(b['exit_states'])}")
    else:
        ap.print_help()
