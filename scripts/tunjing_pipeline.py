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


def entry_selfcheck():
    """
    入口自检：判断当前处在「创作/擦屁股/继续」哪个入口，给出选择题回应。
    返回 (入口类型, 判断结果说明)
    """
    # 自检：当前工作目录 / 常见位置有没有剧本
    checks = []
    cwd = os.getcwd()
    for d in (cwd,):
        for fn in ("剧本.md", "EP001/剧本.md", "剧集/EP001/剧本.md"):
            p = os.path.join(d, fn)
            if os.path.exists(p):
                checks.append(p)
    if checks:
        script = checks[0]
        # 快速判断剧本是否"合格"（有没有幕次结构 + 是否是散装/废稿）
        with open(script, encoding="utf-8") as f:
            txt = f.read()
        has_act = ("第一幕" in txt or "第二幕" in txt or "## " in txt)
        has_d = "<d>" in txt or "：" in txt
        if has_act and has_d:
            return "continue", f"已有合格剧本 {script}，可继续走 分镜→提示词→门禁→渲染"
        else:
            return "fix", f"有剧本但残缺（{script} 缺幕次结构或台词标签），是擦屁股材料，先诊断再改编"
    return "create", "没有找到剧本，是从零创作，先定题材+冲突原型+画幅再写剧本"


def main():
    ap = argparse.ArgumentParser(description="吞鲸宝典端到端自动流水线（One-Shot Auto-Pipeline）")
    ap.add_argument("script", nargs="?", default="", help="剧本.md 文件路径（或项目目录）；不填则自检入口并提示")
    ap.add_argument("--aspect", default="9:16", help="画幅 9:16/16:9/1:1，默认竖屏")
    ap.add_argument("--total", type=float, default=240.0, help="全集目标时长秒")
    ap.add_argument("--scene", default="酒店客房", help="主场景名")
    ap.add_argument("--lines", default="", help="台词（可选，格式 '镜号:女子A:台词' 竖线分隔）")
    ap.add_argument("--idea", default="", help="剧情核心张力描述")
    ap.add_argument("--dry", action="store_true", help="只跑到分镜+提示词落地，不渲染")
    args = ap.parse_args()

    # ── 0. 入口自检（不填 script 时，自动判断入口并给选择题，不直接报错）──
    if not args.script:
        kind, msg = entry_selfcheck()
        print("🐳 吞鲸宝典 · 入口自检")
        print(f"   [判断] {msg}")
        print()
        if kind == "continue":
            print("   [选择题] 剧本已就绪，下一步怎么走？")
            print("     A. 继续跑完整流水线（分镜→提示词→门禁→渲染）")
            print("     B. 先只出分镜和提示词给我审，先不渲染")
            print("     C. 先诊断升维，看能不能更精彩再跑")
        elif kind == "fix":
            print("   [选择题] 这是要擦屁股的材料，怎么处理？")
            print("     A. 先诊断哪里烂（tunjing_advisor.py），列出问题再决定改法")
            print("     B. 直接按冲突发动机改编（tunjing_drama.py 先定冲突原型）")
            print("     C. 我先说明要什么样的剧，你帮我重写剧本")
        else:
            print("   [选择题] 从零创作，请先回答三个方向：")
            print("     A. 题材是什么？（人妻/交换/绿帽/偷窥/不伦/正经情感/悬疑...）")
            print("     B. 冲突原型选哪个？（夺物/揭密/逼选/摊牌/破防）")
            print("     C. 画幅横屏还是竖屏？")
        print()
        print("   （监制拍板后，鲸鲸按所选方向继续。带剧本重跑：python tunjing_pipeline.py '<剧本路径>'）")
        return

    # ── 确定项目目录 ──
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
    from tunjing_pose_select import select_poses_with_staging, select_poses_from_script
    poses = load_poses()

    # 场景自动识别体位（场景 → 姿势 → 体位提示词），绝不写死默认链
    pose_ids, pose_source, intent = select_poses_with_staging(script_txt, args.scene)

    print(f"  识别到体位序列: {pose_ids}")
    print(f"  识别来源: {pose_source} | 文戏意图: {intent} -> {DIALOGUE_SHOT_RECIPES[intent]['zh']}")
    sex_pose_ids = [p for p in pose_ids if p not in STAGING_IDS]
    if not sex_pose_ids:
        # 纯文戏剧集（无肉戏信号），合法，继续跑文戏链，不塞肉戏、不退出
        print("  [纯文戏] 剧本无肉戏信号，仅编排文戏镜头，不强行塞肉戏体位。")

    # 把识别出的调度链写回剧本（场景 → 文戏原语/体位 → 写进剧本 → 门禁可识别吞鲸 ID）
    # 纯文戏写文戏原语，含肉戏写体位 + 文戏原语；保留剧本原文不动
    if "吞鲸体位推进" not in script_txt:
        # 写回时按顺序写全部调度链（文戏原语 + 肉戏体位），确保 Gate 2 能认到
        pose_lines = ["## 吞鲸体位推进", "",
                      "以下为本集按场景自动识别的吞鲸标准调度序列（供门禁与分镜引擎识别）：", ""]
        for pid in pose_ids:
            p = poses.get(pid, {})
            pose_lines.append(f"- `{pid}` {p.get('nameZh', pid)}")
        pose_lines.append("")
        with open(script_file, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(pose_lines))
        # 重新读剧本（已含写入的调度链），供后续使用
        with open(script_file, "r", encoding="utf-8") as f:
            script_txt = f.read()
        print(f"  已将 {len(pose_ids)} 个调度项写回剧本（吞鲸调度链段落）：{','.join(pose_ids)}")

    # ── 2. 组装调度链：场景自动识别的体位序列 ──
    step_banner(2, "自动组装调度链（场景识别体位）")
    chain_str = ",".join(pose_ids)
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
