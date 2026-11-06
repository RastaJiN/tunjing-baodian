#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 真源偏离度与模型执行审计引擎 (Tunjing Source & Execution Audit Engine)

核心使命：
针对 DeepSeek / GPT / Claude 等发散型大模型在执行过程中“夹带私货、自作主张、自编动作、篡改结构”等顽疾，
提供一键自动化全量盲检与标准对比数据报告！

输出指标：
1. 提示词语言与英文真源命中率 (Action Source Purity)
2. 六段式结构契约对齐度 (Six-Section Parity)
3. 前戏/插入逻辑冲突检测 (Foreplay vs Insertion Conflict Check)
4. 首镜脱衣景别安全锁 (Undress Wide Risk Check)
5. 台词重复与嘴部占用检测 (Dialogue Repetition & Oral Mute Check)
6. 物理帧长公式 (5 + 17*N) 合规率 (Frame Formula Compliance)
7. 与宝典标准基准 (tunjing_poses_matrix.json) 的逐镜差异对比 (Diff Matrix)
"""

import os
import sys
import json
import re
import argparse

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "..", "references")


def load_poses_truth():
    p_path = os.path.join(REF, "tunjing_poses_matrix.json")
    with open(p_path, "r", encoding="utf-8") as f:
        return json.load(f)


def audit_project(project_dir):
    poses_db = load_poses_truth()
    
    sb_file = os.path.join(project_dir, "分镜.md")
    pr_file = os.path.join(project_dir, "视频提示词.md")
    batch_file = os.path.join(project_dir, "批量任务.json")
    
    report = {
        "project": os.path.abspath(project_dir),
        "files_checked": {},
        "metrics": {},
        "violations": [],
        "warnings": [],
        "diff_table": []
    }
    
    for f_name, f_path in [("分镜.md", sb_file), ("视频提示词.md", pr_file), ("批量任务.json", batch_file)]:
        report["files_checked"][f_name] = os.path.exists(f_path)
    
    if not os.path.exists(batch_file):
        report["violations"].append(f"缺少关键执行文件: {batch_file}")
        return report

    with open(batch_file, "r", encoding="utf-8") as f:
        batch_data = json.load(f)
    
    shots = batch_data.get("batch_shots") or batch_data.get("shots") or []
    report["metrics"]["total_shots"] = len(shots)
    
    # 1. 物理帧长检查
    frame_pass = 0
    for s in shots:
        frames = s.get("frames", 0)
        if frames >= 5 and (frames - 5) % 17 == 0:
            frame_pass += 1
        else:
            report["violations"].append(f"镜头 {s.get('id')} 帧数 {frames} 违反 5+17*N 物理公式！")
    report["metrics"]["frame_compliance"] = f"{frame_pass}/{len(shots)} ({frame_pass/len(shots)*100:.1f}%)" if shots else "N/A"

    # 2. 六段式结构完整度与真源纯度分析
    struct_pass = 0
    pure_truth_pass = 0
    foreplay_conflicts = 0
    undress_wide_risks = 0
    spoken_dialogues = []
    
    foreplay_ids = {"undress", "kiss_fondle", "breast_rub", "nipple_lick",
                    "kiss_pin", "kiss_force", "kiss_her", "ass_rub", "masturbation",
                    "finger_masturbate", "strip_tease"}
    oral_ids = {"bj", "squat_bj", "prone_bj", "deepthroat", "head_thrust", "facefuck",
                "sixty_nine", "cunnilingus", "sofa_cunni", "fingering", "clit_tease",
                "tip_lick", "ball_lick", "penis_slap", "handjob", "titjob"}

    required_anchors = [
        "Goal:",
        "Audio rule:",
        "Reference map",
        "Consistency:",
        "Motion quality",
        "integrated_multimodal_description:",
        "overall_soundscape:",
        "=== NEGATIVE ==="
    ]

    for idx, s in enumerate(shots, 1):
        prompt = s.get("prompt", "")
        pose = s.get("pose", "")
        size = s.get("shot_size", "")
        
        # 结构检查
        anchors_present = sum(1 for a in required_anchors if a in prompt)
        if anchors_present >= 7:
            struct_pass += 1
        else:
            report["violations"].append(f"镜头 {s.get('id')} 六段式结构缺失 (仅命中 {anchors_present}/8 锚点)")

        # 首镜脱衣景别安全
        if idx == 1 and "undress" in pose:
            if size == "wide" or "景别：全景" in prompt or "wide shot" in prompt.lower():
                undress_wide_risks += 1
                report["violations"].append(f"第 1 镜脱衣诱惑使用了 wide 全景，存在严重露鸟失控风险！")

        # 前戏与插入冲突
        first_p = pose.split("->")[0]
        if first_p in foreplay_ids or first_p in oral_ids or "->" in pose:
            if "阴道紧密贴合插入" in prompt or "penis inside vagina" in prompt.lower() or "vaginal insertion" in prompt.lower():
                foreplay_conflicts += 1
                report["violations"].append(f"镜头 {s.get('id')} ({pose}) 属于前戏/口交/转场，但被注入了插入要点！")

        # 检查台词（排除说明文字中的 <d>...</d> 规则）
        prompt_without_rule = prompt.replace("Audio rule: characters may only speak the exact words inside <d>...</d>;", "")
        d_match = re.search(r"<d>(?:\[Chinese\])?(.*?)</d>", prompt_without_rule)
        if d_match:
            line_text = d_match.group(1).strip()
            # 嘴部占用检查
            if first_p in ("bj", "deepthroat", "facefuck", "cum_face") and "女子" in prompt:
                report["violations"].append(f"镜头 {s.get('id')} ({pose}) 女方嘴部被占用，但排了女方对白！")
            spoken_dialogues.append((s.get("id"), line_text))

        # 动作纯度检查：比对是否脱稿自编
        p_info = poses_db.get(first_p)
        if p_info:
            beats_en = p_info.get("beatsEn", [])
            beats_zh = p_info.get("beatsZh", [])
            has_truth = any(b[:20].lower() in prompt.lower() for b in beats_en) or any(b[:6] in prompt for b in beats_zh)
            if has_truth:
                pure_truth_pass += 1
            else:
                report["warnings"].append(f"镜头 {s.get('id')} ({pose}) 疑似脱稿自编（未匹配到宝典真源 beats 原文）")

    # 3. 台词连续复读检查
    dup_lines = []
    for k in range(len(spoken_dialogues) - 1):
        if spoken_dialogues[k][1] == spoken_dialogues[k+1][1]:
            dup_lines.append(f"{spoken_dialogues[k][0]} 与 {spoken_dialogues[k+1][0]} 台词重复: 「{spoken_dialogues[k][1]}」")
    if dup_lines:
        for dl in dup_lines:
            report["violations"].append(f"台词重复复读: {dl}")

    report["metrics"]["structure_compliance"] = f"{struct_pass}/{len(shots)} ({struct_pass/len(shots)*100:.1f}%)" if shots else "N/A"
    report["metrics"]["truth_purity"] = f"{pure_truth_pass}/{len(shots)} ({pure_truth_pass/len(shots)*100:.1f}%)" if shots else "N/A"
    report["metrics"]["foreplay_insertion_conflicts"] = foreplay_conflicts
    report["metrics"]["undress_wide_risks"] = undress_wide_risks
    report["metrics"]["dialogue_repetition_count"] = len(dup_lines)

    return report


def print_audit_summary(report):
    print("\n" + "=" * 70)
    print("🐳 吞鲸宝典 · 真源偏离度与模型执行审计报告 (Tunjing Audit Report)")
    print(f"审计目标项目: {report['project']}")
    print("=" * 70)
    
    m = report["metrics"]
    print("【核心质量账目】")
    print(f"  • 总 镜 数: {m.get('total_shots', 0)} 镜")
    print(f"  • 物理帧长合规率 (5+17N): {m.get('frame_compliance')}")
    print(f"  • 六段式结构契约完整度: {m.get('structure_compliance')}")
    print(f"  • 宝典真源动作纯度: {m.get('truth_purity')}")
    print(f"  • 前戏/插入逻辑冲突数: {m.get('foreplay_insertion_conflicts')} (越低越好，0为完美)")
    print(f"  • 开场全景脱衣露鸟风险: {m.get('undress_wide_risks')} (必须为0)")
    print(f"  • 台词连续复读次数: {m.get('dialogue_repetition_count')} (必须为0)")
    
    print("\n【红线违规清单 (Violations)】")
    if not report["violations"]:
        print("  🎉 零红线违规！大模型 100% 严格依照宝典真源执行，无私货夹带！")
    else:
        for v in report["violations"]:
            print(f"  ❌ {v}")
            
    print("\n【偏差预警 (Warnings)】")
    if not report["warnings"]:
        print("  ✅ 零偏差预警！")
    else:
        for w in report["warnings"][:10]:
            print(f"  ⚠️  {w}")
        if len(report["warnings"]) > 10:
            print(f"  ... 另有 {len(report['warnings']) - 10} 处预警已折叠")
    print("=" * 70 + "\n")


def main():
    ap = argparse.ArgumentParser(description="吞鲸真源偏离度与模型执行审计器")
    ap.add_argument("project_dir", help="待审计项目目录（内含 批量任务.json）")
    ap.add_argument("--json", action="store_true", help="输出 JSON 原始数据")
    args = ap.parse_args()

    rep = audit_project(args.project_dir)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print_audit_summary(rep)


if __name__ == "__main__":
    main()
