#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 剧本生成器 (Tunjing Script Writer — 写剧本/改剧本的最后一公里)

把「冲突发动机（tunjing_drama.py）」的四段骨架，展开成符合门禁的、
带台词、带体位推进的完整可拍剧本。同时支持"擦屁股"——把散装梗概/小说改写合格。

半自动：给 题材 + 冲突原型 + 画幅，按「目标-反对-转向-退出」生成三幕剧本；
关键转向处留监制拍板的缝，不搞无人驾驶。

剧本符合 Gate 2 硬要求：三幕结构 + <d>[Chinese]</d> 台词 + 体位推进 + 禁 AI 腔。
"""

import os
import re
import json
import argparse

BASE = os.path.dirname(os.path.abspath(__file__))
sys_path_added = False
try:
    from tunjing_drama import CONFLICT_ARCHETYPES, build_conflict_beats
    from tunjing_core import load_poses, STAGING_IDS
    from tunjing_pose_select import select_poses_from_script
except ImportError:
    import sys
    sys.path.insert(0, BASE)
    from tunjing_drama import CONFLICT_ARCHETYPES, build_conflict_beats
    from tunjing_core import load_poses, STAGING_IDS
    from tunjing_pose_select import select_poses_from_script


# ── 题材 → 默认冲突原型 + 默认落点（正经剧落情绪，成人剧落肉戏）──
SUBJECT_PRESETS = {
    "人妻":   {"archetype": "逼选", "ending": "肉戏", "note": "居家妻子在家庭责任与内心欲望间两难，最终沉沦"},
    "交换":   {"archetype": "夺物", "ending": "肉戏", "note": "交换伴侣/交换把柄，争夺与妥协中欲望失控"},
    "绿帽":   {"archetype": "揭密", "ending": "肉戏", "note": "发现另一半偷情的秘密，隐忍、摊牌、报复"},
    "偷窥":   {"archetype": "揭密", "ending": "肉戏", "note": "偷窥撞见不该看的，在窥视与愧疚中越陷越深"},
    "不伦":   {"archetype": "破防", "ending": "肉戏", "note": "禁忌关系，层层设防被攻破，防线崩塌沉沦"},
    "情感":   {"archetype": "摊牌", "ending": "情绪", "note": "隐忍已久的情感当面摊开，和解或决裂"},
    "悬疑":   {"archetype": "揭密", "ending": "反转", "note": "一个不能公开的秘密被逼近，真相层层揭开"},
    "复仇":   {"archetype": "夺物", "ending": "反转", "note": "夺回被夺走的东西，代价层层落地"},
    "职场":   {"archetype": "逼选", "ending": "反转", "note": "利益与底线两难，选择带来不可逆代价"},
}


def subject_preset(subject):
    """按题材取默认冲突原型 + 落点，未识别题材回退通用"""
    for key, preset in SUBJECT_PRESETS.items():
        if key in subject:
            return preset
    return {"archetype": "夺物", "ending": "情绪", "note": "一个想得到、一个不让，冲突中见人心"}


def build_three_act_script(subject, archetype, obj="", secret="", ending="", title=""):
    """
    按冲突四段生成三幕剧本（符合 Gate 2）。
    返回 markdown 剧本文本。
    """
    a = CONFLICT_ARCHETYPES.get(archetype, CONFLICT_ARCHETYPES["夺物"])
    title = title or subject

    # 冲突四段骨架
    beats = build_conflict_beats(archetype, obj=obj, secret=secret)

    # 落点（正经剧=情绪/反转，成人剧=肉戏）
    ending = ending or "情绪"
    is_adult = ending == "肉戏"

    lines = []
    lines.append(f"# {title or subject}")
    lines.append("")
    lines.append("<!-- 吞鲸剧本 · 冲突原型：{} · 落点：{} -->".format(a["name"], ending))
    lines.append("")

    # ── 第一幕：目标建立（晚进，从冲突正烧处切入）──
    lines.append("## 第一幕 · 交锋")
    lines.append("")
    lines.append("（晚进：不写背景铺垫，直接切入两人正在争什么。）")
    goal_zh = _goal_zh(archetype, obj, secret)
    lines.append(f"场景：{obj or '关键物件'} 的归属与争夺一触即发。")
    lines.append("")
    lines.append(f"<d>[Chinese]{_line_goal(archetype, obj, secret)}</d>")
    lines.append("")
    lines.append("（反对：对方不说'不'，而是有筹码地出招。）")
    lines.append(f"<d>[Chinese]{_line_opposition(archetype)}</d>")
    lines.append("")
    lines.append("（第一幕收在压力顶到最高处，不给结果，逼出第二幕。）")
    lines.append("")

    # ── 第二幕：转向（局面实质变化，亮证据/筹码易主/身份反转）──
    lines.append("## 第二幕 · 转向")
    lines.append("")
    lines.append("（转向：亮出一张此前藏住的底牌，局面当场反转。）")
    lines.append(f"<d>[Chinese]{_line_turn(archetype, obj, secret)}</d>")
    lines.append("")
    if is_adult:
        # 成人剧：转向后防线破，落肉戏——直接写具体体位推进（不是占位说明），供体位引擎识别
        lines.append("（转向后原本的对峙解体，紧绷的敌对关系在破防瞬间滑向身体的本能。）")
        lines.append("")
        lines.append("## 第三幕 · 沉沦")
        lines.append("")
        lines.append("两人脱衣，吻到一处；女上位骑乘，再换后入，最后内射。")
        lines.append("")
    else:
        # 正经剧：转向后落情绪/反转
        lines.append("## 第三幕 · 落定")
        lines.append("")
        lines.append("（转向后代价落地，关系被当面宣判，情绪或反转收束。）")
        lines.append(f"<d>[Chinese]{_line_ending(archetype)}</d>")
        lines.append("")

    return "\n".join(lines)


def _goal_zh(archetype, obj, secret):
    return {
        "夺物": f"你手上那东西，今天必须留下。",
        "揭密": f"你到底还有多少事瞒着我？",
        "逼选": f"要么你选，要么我替你选。",
        "摊牌": f"有些话，我一直等你先开口。",
        "破防": f"装够了吗？把真心话掏出来。",
    }.get(archetype, f"这事，今天得有个了断。")


def _line_goal(archetype, obj, secret):
    return _goal_zh(archetype, obj, secret)


def _line_opposition(archetype):
    return {
        "夺物": "东西可以给，但你得拿别的来换。",
        "揭密": "你查我之前，先问问自己够不够干净。",
        "逼选": "两个我都不选，你能拿我怎么样。",
        "摊牌": "我先开口？是你先把话说绝的。",
        "破防": "真心话？你听得起吗。",
    }.get(archetype, "我不答应，你又能如何。")


def _line_turn(archetype, obj, secret):
    return {
        "夺物": f"你以为拿稳了？看清楚，那上面根本没有你的名字。",
        "揭密": f"这张照片的时间，可比你说的早多了。",
        "逼选": f"既然你两个都不选，那我替你要第三个——两样都归我。",
        "摊牌": f"当年那封信，是我让人转交的。",
        "破防": f"你眼角的那滴泪，早把你卖了。",
    }.get(archetype, f"你以为我不知道？")


def _line_ending(archetype):
    return {
        "夺物": f"东西还你，从今往后，我们两清。",
        "揭密": f"你走吧，这件事，我会记一辈子。",
        "逼选": f"我选的，是这个家。",
        "摊牌": f"我等你这句话，等了十年。",
        "破防": f"你终于，说了真话。",
    }.get(archetype, f"就这样吧。")


def diagnose_and_fix(script_text):
    """
    擦屁股入口：诊断散装/废稿剧本缺什么，返回诊断 + 修法建议。
    """
    issues = []
    if "第一幕" not in script_text and "第二幕" not in script_text:
        issues.append("缺幕次结构（只有散装段落，没有【第一幕/第二幕】）")
    if "<d>" not in script_text:
        issues.append("缺台词标签（台词没包 <d>[Chinese]...</d>，会被画成字幕）")
    if "：说" not in script_text and "：" not in script_text:
        issues.append("可能没有完整对白或没有冲突（角色没在争什么）")
    # 检测有没有冲突发动机四段
    if not any(k in script_text for k in ("争", "抢", "逼", "摊牌", "瞒", "揭", "问", "翻脸", "两难")):
        issues.append("缺冲突（角色没在争一件具体的东西，只是干聊）")
    return issues


def main():
    ap = argparse.ArgumentParser(description="吞鲸剧本生成器（写剧本/擦屁股）")
    ap.add_argument("--subject", default="", help="题材（人妻/交换/绿帽/偷窥/不伦/情感/悬疑/复仇/职场）")
    ap.add_argument("--archetype", default="", help="冲突原型（夺物/揭密/逼选/摊牌/破防），不填按题材自动")
    ap.add_argument("--obj", default="", help="关键物件（如 房产证/房卡/手机）")
    ap.add_argument("--secret", default="", help="被藏的秘密")
    ap.add_argument("--ending", default="", help="落点：肉戏（成人剧）/情绪/反转（正经剧）")
    ap.add_argument("--title", default="", help="剧名")
    ap.add_argument("--out", default="", help="输出剧本文件路径（默认打印）")
    ap.add_argument("--diagnose", default="", help="擦屁股：诊断一个已有剧本文件，列出哪里烂")
    args = ap.parse_args()

    # 擦屁股模式
    if args.diagnose:
        if not os.path.isfile(args.diagnose):
            print(f"[X] 文件不存在: {args.diagnose}")
            return
        with open(args.diagnose, encoding="utf-8") as f:
            txt = f.read()
        issues = diagnose_and_fix(txt)
        print("🐳 吞鲸 · 剧本诊断（擦屁股）")
        print(f"   待诊断: {args.diagnose}")
        if issues:
            print(f"   发现 {len(issues)} 处问题：")
            for i, iss in enumerate(issues, 1):
                print(f"     {i}. {iss}")
            print("")
            print("   修法：用 --subject/--archetype 重建剧本，或用冲突发动机补齐缺的环节。")
        else:
            print("   ✓ 剧本结构完整，可直接走分镜流程。")
        return

    # 创作模式
    subject = args.subject
    if not subject:
        print("[X] 请用 --subject 指定题材（人妻/交换/绿帽/偷窥/不伦/情感/悬疑/复仇/职场）")
        return

    preset = subject_preset(subject)
    archetype = args.archetype or preset["archetype"]
    ending = args.ending or preset["ending"]
    title = args.title or subject

    script = build_three_act_script(subject, archetype, obj=args.obj, secret=args.secret,
                                    ending=ending, title=title)

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(script)
        print(f"[✓] 剧本已写入: {args.out}")
    else:
        print(script)


if __name__ == "__main__":
    main()
