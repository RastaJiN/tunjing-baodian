#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 v4.0 · 全剧集导演主动诊断与升维顾问引擎 (Tunjing v4.0 Proactive Director Advisor)

核心职责（专治“读了旧剧本就照本宣科、不主动提修改完善建议”的痛点）：
当接手任何既有项目（如《交换游戏》EP01）或初稿剧本/分镜时，主动从五大维度进行导演级视听诊断，
并直接给出可一键执行的 `--chain` 升级方案与资产补齐清单：

1. 【维度一：文戏肢体与暧昧挑逗饱和度诊断】
   - 检查是否从“干站对话”直接跳入“脱衣/插入”，缺失 24 套文戏推拉与挑逗前奏（如捏下巴 chin_lift、贴耳热气 ear_whisper_tease、拽领带 tie_pull_seduce、拇指擦唇 lip_thumb_wipe、十指扣死 finger_interlock_pin）。
2. 【维度二：正反打与视线交锋密度诊断】
   - 检查是否全片皆为双人同框（A_two_shot 连体婴），缺失单人正反打（srs_male ⇄ srs_female）与深景深过肩（ots_depth）。
3. 【维度三：12 大主动表演情绪光谱覆盖诊断】
   - 检查对白与反应镜头是否标注了具体情绪底色（生气/冷怒/忧伤/委屈/冷笑/恐惧等），主动为每句台词配齐四维解剖级微表情。
4. 【维度四：空间图池单槽轮换诊断（专治 1 张图拍到底）】
   - 检查 `00_资产/` 是否仅有 1 张主场景图，若剧本含墙边/镜前立面戏或大量特写微距，主动提示补齐 `scene_wall.png`（立面）与 `scene_close.png`（承托面近景）。
5. 【维度五：Auto-DP 运镜活性与体位防站桩诊断】
   - 检查是否存在单一姿势连续堆叠 >3 镜（如 15 镜原地后入）或 static 死机位占比过高，主动输出心电图运镜替换方案。
"""

import os
import sys
import json
import re
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from tunjing_core import (
    load_poses, STAGING_IDS, TEASE_IDS, DRAMATIC_BODY_IDS,
    EMOTION_MUSCLE_CUES, resolve_emotion_key, check_dialogue_human_quality, parse_audio_fx_mode
)


def diagnose_project(project_dir):
    poses_db = load_poses()
    asset_dir = os.path.join(project_dir, "00_资产")
    script_file = os.path.join(project_dir, "剧本.md")
    sb_file = os.path.join(project_dir, "分镜.md")
    bj_file = os.path.join(project_dir, "批量任务.json")

    script_txt = open(script_file, "r", encoding="utf-8").read() if os.path.exists(script_file) else ""
    sb_txt = open(sb_file, "r", encoding="utf-8").read() if os.path.exists(sb_file) else ""
    batch_data = json.load(open(bj_file, "r", encoding="utf-8")) if os.path.exists(bj_file) else {}
    shots = batch_data.get("batch_shots") or batch_data.get("shots") or []

    all_text = script_txt + "\n" + sb_txt
    found_ids = [m for m in re.findall(r"\b([a-z][a-z_0-9]{1,28})\b", all_text) if m in poses_db]
    if shots:
        shot_poses = [s.get("pose", "").split("->")[0] for s in shots if s.get("pose")]
    else:
        shot_poses = found_ids

    used_set = set(shot_poses)
    used_tease = used_set & TEASE_IDS
    used_dramatic = used_set & DRAMATIC_BODY_IDS
    used_srs = used_set & {"srs_male", "srs_female"}

    suggestions = []
    upgrade_chain_prefix = []
    upgrade_chain_mid = []

    # ── 1. 文戏肢体与暧昧挑逗饱和度诊断 ──
    if not used_tease and not used_dramatic:
        suggestions.append({
            "dimension": "【维度 1 · 文戏肢体与挑逗前奏缺失】",
            "issue": "当前剧本/分镜从对话直接跳入前戏/肉戏，缺少上半身肢体推拉与暧昧挑逗过渡，容易显得生硬直球、缺乏拉扯张力。",
            "action": "建议在破局前插入 3~4 个单接触点高张力肢体动作：如 `wall_caging`(单臂壁咚封堵) ➔ `chin_lift`(捏下巴抬脸逼视) ➔ `chest_push`(双手抵胸推拒) ➔ `ear_whisper_tease`(贴耳热气低语) ➔ `lip_thumb_wipe`(拇指摩挲唇瓣) ➔ `finger_interlock_pin`(十指扣死按压)。"
        })
        upgrade_chain_prefix.extend(["env_establish", "wall_caging", "chin_lift", "chest_push", "ear_whisper_tease", "lip_thumb_wipe"])
    elif not used_tease:
        suggestions.append({
            "dimension": "【维度 1 · 暧昧挑逗层次可深化】",
            "issue": f"已包含对抗肢体 {sorted(used_dramatic)}，但缺少欲拒还迎的挑逗试探动作。",
            "action": "建议在进入实质前戏前穿插 `trace_collar`(指尖划喉结领口)、`tie_pull_seduce`(拽领带拉低逼视) 或 `shoulder_strap_slide`(肩带衣领半滑落诱惑)。"
        })

    # ── 2. 正反打与视线交锋密度诊断 ──
    if not used_srs:
        suggestions.append({
            "dimension": "【维度 2 · 缺少单人正反打 (Shot / Reverse-Shot)】",
            "issue": "全片未显式排布 `srs_male`(男正打) 与 `srs_female`(女反打)，全双人同框会导致分不清谁在说话、眼神戏缺失。",
            "action": "建议在对白交锋处与主力冲撞中段插入 `srs_male ➔ srs_female` 正反打序列（自动物理隔离异性槽位防鬼脸，并用 `ots_depth` 过肩景深撑开 9:16 纵深）。"
        })
        upgrade_chain_prefix.extend(["srs_male", "srs_female"])
        upgrade_chain_mid.extend(["srs_male", "srs_female"])

    # ── 3. 12大主动表演情绪光谱诊断 ──
    dialogues = re.findall(r"<d>(?:\[Chinese\])?(.*?)</d>", all_text)
    emo_recommendations = []
    for idx_d, d_line in enumerate(dialogues[:8], 1):
        d_clean = d_line.strip()
        if not d_clean:
            continue
        auto_ek = resolve_emotion_key("", d_clean, fallback="forbearance")
        emo_recommendations.append(f"台词 {idx_d}「{d_clean[:18]}」➔ 匹配情绪 `{auto_ek}` ({EMOTION_MUSCLE_CUES[auto_ek][:48]}...)")
    if emo_recommendations:
        suggestions.append({
            "dimension": "【维度 3 · 演员四维解剖情绪底色配对】",
            "issue": f"检测到 {len(dialogues)} 句台词，若不指定主动表演情绪底色，角色易呈木头面瘫。",
            "action": "已为您自动匹配吞鲸 4.0 四维面部肌肉指令（支持在 `--lines` 中用 `男子A(生气):台词` 显式锁定）：" + " | ".join(emo_recommendations[:5])
        })

    # ── 4. 空间图池单槽轮换诊断（专治 1 张场景图拍到底）──
    scene_files = []
    if os.path.isdir(asset_dir):
        scene_files = [f for f in os.listdir(asset_dir) if any(k in f.lower() for k in ("scene", "room", "wall", "close", "场景"))]
    if len(scene_files) <= 1:
        suggestions.append({
            "dimension": "【维度 4 · 空间参考图单一预警（防切特写穿帮/丢背景）】",
            "issue": f"当前 `00_资产/` 仅检测到 {len(scene_files)} 张场景底图 ({scene_files})。一图拍到底会导致站立镜前戏躺回床上、特写背景模糊穿帮。",
            "action": "建议采用吞鲸 4.0【空间图池单槽轮换法】，在 `00_资产/` 补齐 3 张同风格空间图（每镜 `<Picture 3>` 只挂 1 张不混喂）：① scene_main.png(主全景) ② scene_wall.png(立面墙镜) ③ scene_close.png(承托面近景俯拍，根治切特写丢背景)"
        })

    # ── 4b. 去AI味活人台词与声学特效诊断 ──
    cliche_warnings = []
    fx_notes = []
    for idx_d, d_line in enumerate(dialogues, 1):
        issues = check_dialogue_human_quality(d_line, shot_dur=4.5)
        if issues:
            cliche_warnings.extend(issues)
        fx_m = parse_audio_fx_mode("", d_line)
        if fx_m != "normal":
            fx_notes.append(f"台词 {idx_d} 自动识别为 `{fx_m}` 声学模式")
    if cliche_warnings:
        suggestions.append({
            "dimension": "【维度 4b · 台词去AI味与语速窗口预警】",
            "issue": " | ".join(cliche_warnings[:3]),
            "action": "建议精简为 12 字以内的口语化短句（常速 4.1字/秒，预留开口前 1.1s 延迟与句尾 0.7s 反应）。"
        })

    # ── 5. 运镜活性与防站桩诊断 ──
    if shots:
        static_cnt = sum(1 for s in shots if "static" in str(s.get("camera_motion", "")))
        if static_cnt > len(shots) * 0.35:
            suggestions.append({
                "dimension": "【维度 5 · 固定三脚架机位占比过高（画面死气沉沉）】",
                "issue": f"当前 {len(shots)} 镜中有 {static_cnt} 镜为 static 死机位（占比 {static_cnt/len(shots)*100:.0f}%）。",
                "action": "建议重新通过吞鲸 4.0 `tunjing_scene.py` Auto-DP 引擎编译，自动将死机位替换为 `push_tension`(慢推)、`tilt_up_desire`(垂直上摇)、`ots_depth`(深景深过肩)、`handheld_breath`(呼吸感手持)。"
            })

    # 生成推荐的 4.0 升维完整调度链
    core_action_chain = [p for p in shot_poses if p not in STAGING_IDS]
    if not core_action_chain:
        core_action_chain = ["undress", "kiss_fondle", "bj", "missionary", "cowgirl", "doggy", "cum_face"]
    # 去重连续相同体位
    dedup_actions = []
    for p in core_action_chain:
        if not dedup_actions or dedup_actions[-1] != p:
            dedup_actions.append(p)
    if len(dedup_actions) >= 3 and upgrade_chain_mid:
        mid_idx = len(dedup_actions) // 2
        dedup_actions = dedup_actions[:mid_idx] + upgrade_chain_mid + ["cut_insert"] + dedup_actions[mid_idx:]

    recommended_chain = upgrade_chain_prefix + dedup_actions + ["outro_solo"]
    # 消除相邻重复
    final_chain = []
    for x in recommended_chain:
        if not final_chain or final_chain[-1] != x:
            final_chain.append(x)

    return {
        "project": os.path.abspath(project_dir),
        "existing_poses_count": len(shot_poses),
        "used_tease": sorted(used_tease),
        "used_dramatic": sorted(used_dramatic),
        "used_srs": sorted(used_srs),
        "scene_files": scene_files,
        "suggestions": suggestions,
        "recommended_v4_chain": ",".join(final_chain)
    }


def print_diagnosis(rep):
    print("=" * 80)
    print("🐳 吞鲸宝典 v4.0 · 导演主动诊断与全剧集升维建议报告 (Proactive Director Advisor)")
    print(f"诊断目标项目: {rep['project']}")
    print("=" * 80)
    if not rep["suggestions"]:
        print("🎉 本项目已 100% 满配【文戏肢体推拉 + 暧昧挑逗 + 单人正反打 + 四维情绪 + 多视角空间图池】！")
    else:
        print(f"🔍 鲸鲸主动扫描发现 {len(rep['suggestions'])} 项可大幅提升成片质感的导演升维点：")
        for idx, s in enumerate(rep["suggestions"], 1):
            print(f"  {idx}. {s['dimension']}")
            print(f"     • 现状痛点: {s['issue']}")
            print(f"     • 升维方案: {s['action']}")

    print("-" * 80)
    print("🚀 【鲸鲸一键升维重排推荐命令】（可直接复制执行，补齐文戏肢体、挑逗、正反打与 Auto-DP 运镜）：")
    print(f"python scripts/tunjing_scene.py --chain '{rep['recommended_v4_chain']}' --total 180 --out-dir '{rep['project']}'")
    print("=" * 80)


def main():
    ap = argparse.ArgumentParser(description="吞鲸 v4.0 导演主动诊断与升维顾问引擎")
    ap.add_argument("project_dir", help="待诊断的项目目录")
    ap.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = ap.parse_args()

    rep = diagnose_project(args.project_dir)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print_diagnosis(rep)


if __name__ == "__main__":
    main()
