#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 · 端到端自动流水线主控编排器 (Tunjing One-Shot Auto-Pipeline)

解决「宝典是工具箱、不是流水线，模型加载后不知道从哪跑起」的根本症结。

本编排器是宝典的「大脑」：给定一个剧本文件，它按固定顺序自动执行
诊断 → 文戏镜头查表 → 肉戏体位查表 → 拆镜 → 装提示词 → 六步门禁 → 签字单，
全程不询问用户，只有无法自动推断的关键参数（题材/人选/资产）才停下。

模型加载宝典后，唯一需要做的是：
    python scripts/tunjing_pipeline.py <剧本.md路径> [--aspect 9:16|16:9] [--total 240] [--scene 酒店客房]

其余全部由本编排器自动完成，用户只验收最终产物。
"""

import os
import sys
import json
import argparse
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def run(cmd, cwd=None):
    """执行子命令，返回 (stdout, returncode)"""
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd or BASE_DIR)
    return r.stdout + r.stderr, r.returncode


def step_banner(n, title):
    print("\n" + "=" * 70)
    print(f"  [流水线第 {n} 步] {title}")
    print("=" * 70)


def main():
    ap = argparse.ArgumentParser(description="吞鲸宝典端到端自动流水线（One-Shot Auto-Pipeline）")
    ap.add_argument("script", help="剧本.md 文件路径（或项目目录）")
    ap.add_argument("--aspect", default="9:16", help="画幅 9:16/16:9/1:1，默认竖屏")
    ap.add_argument("--total", type=float, default=240.0, help="全集目标时长秒")
    ap.add_argument("--scene", default="酒店客房", help="主场景名")
    ap.add_argument("--lines", default="", help="台词（可选，格式 '镜号:女子A:台词' 竖线分隔）")
    ap.add_argument("--idea", default="", help="剧情核心张力描述")
    ap.add_argument("--dry", action="store_true", help="只跑到分镜+提示词落地，不渲染")
    args = ap.parse_args()

    # ── 0. 确定项目目录 ──
    if os.path.isdir(args.script):
        project_dir = os.path.abspath(args.script)
        script_file = os.path.join(project_dir, "剧本.md")
    elif os.path.isfile(args.script):
        script_file = os.path.abspath(args.script)
        project_dir = os.path.dirname(script_file)
    else:
        print(f"[X] 剧本路径不存在: {args.script}")
        sys.exit(1)

    if not os.path.exists(script_file):
        print(f"[X] 找不到剧本.md: {script_file}")
        sys.exit(1)

    print("🐳 吞鲸宝典端到端自动流水线启动")
    print(f"   剧本: {script_file}")
    print(f"   画幅: {args.aspect} | 目标时长: {args.total}s | 场景: {args.scene}")
    os.makedirs(project_dir, exist_ok=True)

    # ── 1. 读取剧本，自动提取文戏/肉戏意图与体位 ──
    step_banner(1, "剧本读取 + 自动意图识别")
    with open(script_file, "r", encoding="utf-8") as f:
        script_txt = f.read()

    from tunjing_core import load_poses, STAGING_IDS
    from tunjing_dialogue import DIALOGUE_SHOT_RECIPES, resolve_intent
    poses = load_poses()

    # 提取剧本里提到的吞鲸体位 ID
    found_ids = []
    import re
    for m in re.findall(r"\b([a-z][a-z_0-9]{1,28})\b", script_txt):
        if m in poses:
            found_ids.append(m)

    # 自动识别文戏意图（按剧本里的情绪词）
    intent_hits = []
    for alias in ("对峙", "吵架", "争执", "质问", "施压", "争吵"):
        if alias in script_txt:
            intent_hits.append("confront"); break
    for alias in ("摊牌", "揭露", "真相", "坦白", "揭穿"):
        if alias in script_txt:
            intent_hits.append("reveal"); break
    for alias in ("崩溃", "大哭", "破防", "宣泄"):
        if alias in script_txt:
            intent_hits.append("breakdown"); break
    for alias in ("挑逗", "暧昧", "勾引", "撩"):
        if alias in script_txt:
            intent_hits.append("tease"); break
    if not intent_hits:
        intent_hits.append("confront")

    print(f"  识别到剧本体位 ID: {found_ids if found_ids else '(剧本未显式写体位，用默认肉戏链)'}")
    print(f"  识别到文戏意图: {intent_hits[0]} -> {DIALOGUE_SHOT_RECIPES[intent_hits[0]]['zh']}")

    # ── 2. 组装调度链：文戏原语 + 肉戏体位 ──
    step_banner(2, "自动组装调度链（文戏镜头 + 肉戏体位）")
    # 文戏开场原语（按意图映射）
    intent_to_staging = {
        "confront": ["env_establish", "srs_male", "srs_female"],
        "reveal": ["env_establish", "blocking_2s", "srs_female"],
        "breakdown": ["env_establish", "srs_female"],
        "tease": ["env_establish", "blocking_2s"],
    }
    staging = intent_to_staging.get(intent_hits[0], ["env_establish", "srs_male", "srs_female"])

    # 肉戏链：优先用剧本识别到的体位，否则默认完整肉戏
    default_sex = ["undress", "kiss_fondle", "missionary", "srs_female", "doggy", "srs_male", "creampie"]
    sex_chain = [p for p in found_ids if p not in STAGING_IDS] or default_sex

    full_chain = staging + sex_chain
    # 去相邻重复
    dedup = []
    for p in full_chain:
        if not dedup or dedup[-1] != p:
            dedup.append(p)
    chain_str = ",".join(dedup)
    print(f"  完整调度链: {chain_str}")

    # ── 3. 拆镜 + 装提示词（调用 tunjing_scene.py） ──
    step_banner(3, "拆镜 + 六段式提示词装配（tunjing_scene.py）")
    cmd = (f'python "{BASE_DIR}/tunjing_scene.py" --chain "{chain_str}" '
           f'--total {args.total} --scene "{args.scene}" '
           f'--aspect "{args.aspect}" --out-dir "{project_dir}"')
    if args.lines:
        cmd += f' --lines "{args.lines}"'
    if args.idea:
        cmd += f' --idea "{args.idea}"'
    out, rc = run(cmd)
    print(out[-2000:])
    if rc != 0:
        print("[X] 拆镜失败，终止流水线")
        sys.exit(1)

    # ── 4. 六步门禁 ──
    step_banner(4, "六步门禁逐关核验（tunjing_gatekeeper.py）")
    gate_failed = False
    for g in range(1, 7):
        out, rc = run(f'python "{BASE_DIR}/tunjing_gatekeeper.py" "{project_dir}" {g}')
        tail = out.strip().splitlines()
        # Gate 6 是渲染放行（无 "门禁通过" 文案，直接看 returncode）
        is_pass = (rc == 0) and ("门禁通过" in out or "PASS" in out or g == 6)
        if rc != 0 or not is_pass:
            gate_failed = True
            print(f"  [X] Gate {g}: {tail[-2] if len(tail)>=2 else out[-200:]}")
        else:
            print(f"  [✓] Gate {g} PASS")
    if gate_failed:
        print("\n[X] 有门禁未通过，请查看上方具体拦截项修复后重跑。流水线已停在失败关。")
        sys.exit(1)

    # ── 5. 生成签字单（复用 diff_audit 终审） ──
    step_banner(5, "生成终审签字单（SHA-256 授权码）")
    out, rc = run(f'python "{BASE_DIR}/tunjing_diff_audit.py" "{project_dir}"')
    print(out[-1500:])

    print("\n" + "=" * 70)
    print("✅ 吞鲸端到端流水线全部跑通！产物已落盘：")
    print(f"   分镜.md       -> {project_dir}/分镜.md")
    print(f"   视频提示词.md -> {project_dir}/视频提示词.md")
    print(f"   批量任务.json -> {project_dir}/批量任务.json")
    print(f"   终审签字单    -> {project_dir}/审查/生成前终审报告.md")
    print("=" * 70)

    if not args.dry:
        step_banner(6, "渲染提示")
        print("【提醒】若需正式渲染，请监制审阅签字单后运行：")
        print(f'  python "{BASE_DIR}/tunjing_runner.py" "{project_dir}" --confirm-token <签字单上的8位授权码>')
    else:
        print("[--dry] 已省略渲染步骤，只查分镜+提示词落盘。")


if __name__ == "__main__":
    main()
