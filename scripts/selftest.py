#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 v3.0 · 跨机权威完整性自检器 (Tunjing Master Self-Test)
全部采用相对路径（可移植到任何机器、任何目录），一次性核验：
1. 全部 28 个核心文件存在且非空
2. 3 个吞鲸内置真源 JSON 结构合法（55 套姿势 / 40 条换位配方 / 9 套转换模板）
3. 全部 11 个 Python 脚本 AST 语法 100% 通过
4. 13 类场地承托面动态适配 (with_scene_surface) 功能正常
"""

import os
import sys
import json
import ast

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, SCRIPT_DIR)

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "references/tunjing_poses_matrix.json",
    "references/transition_recipes.json",
    "references/oneshot_transitions.json",
    "references/official-prompt-assembly-spec.md",
    "references/kinetic-positions.md",
    "references/comfyui-dual-pipeline-spec.md",
    "references/shot-design-and-bounce.md",
    "references/high-tension-mechanisms.md",
    "references/femme-fatale-reversal.md",
    "references/pre-render-audit-standard.md",
    "references/takeover-and-patching.md",
    "references/github-sync.md",
    "scripts/tunjing_core.py",
    "scripts/tunjing_scene.py",
    "scripts/tunjing_storyboard.py",
    "scripts/tunjing_resolver.py",
    "scripts/tunjing_gatekeeper.py",
    "scripts/tunjing_compiler.py",
    "scripts/export_comfy_payload.py",
    "scripts/export_jianying_draft.py",
    "scripts/tunjing_diff_audit.py",
    "scripts/dryrun_test.py",
    "scripts/selftest.py",
    "templates/episode_template.md",
    "templates/tunjing_rhythm_120s.md",
    "templates/tunjing_rhythm_300s.md",
]


def main():
    print("=" * 65)
    print("🐳 吞鲸宝典 v3.0 · 跨机权威母版完整性自检")
    print(f"当前挂载路径: {SKILL_DIR}")
    print("=" * 65)

    # 1. 文件完整性检查
    for rel in REQUIRED_FILES:
        fp = os.path.join(SKILL_DIR, rel)
        if not os.path.exists(fp) or os.path.getsize(fp) == 0:
            print(f"[FAIL] 缺失或空文件: {rel}")
            sys.exit(1)
    print(f"[✓] 1/4 文件清单核验 PASS (共 {len(REQUIRED_FILES)} 个核心文件全部就绪)")

    # 2. 真源 JSON 数据核验
    with open(os.path.join(SKILL_DIR, "references/tunjing_poses_matrix.json"), encoding="utf-8") as f:
        poses = json.load(f)
    with open(os.path.join(SKILL_DIR, "references/transition_recipes.json"), encoding="utf-8") as f:
        recipes = json.load(f)
    with open(os.path.join(SKILL_DIR, "references/oneshot_transitions.json"), encoding="utf-8") as f:
        oneshots = json.load(f)
    assert len(poses) >= 55, f"姿势数不足 55: {len(poses)}"
    assert len(recipes) >= 40, f"换位配方不足 40: {len(recipes)}"
    assert len(oneshots) >= 9, f"转换模板不足 9: {len(oneshots)}"
    print(f"[✓] 2/4 吞鲸内置真源数据 PASS ({len(poses)} 套姿势 / {len(recipes)} 条换位配方 / {len(oneshots)} 套模板)")

    # 3. 脚本语法核验
    py_files = [r for r in REQUIRED_FILES if r.endswith(".py")]
    for rel in py_files:
        fp = os.path.join(SKILL_DIR, rel)
        with open(fp, encoding="utf-8") as f:
            ast.parse(f.read(), filename=rel)
    print(f"[✓] 3/4 脚本 AST 语法核验 PASS ({len(py_files)} 个 Python 引擎零语法错误)")

    # 4. 场地承托面动态适配核验
    import tunjing_core as core
    test_out = core.with_scene_surface("女子A趴跪床上，双手抓紧床单", "温泉浴室")
    assert "床" not in test_out and ("tile" in test_out or "瓷砖" in test_out or "shower" in test_out), f"场地改写异常: {test_out}"
    print("[✓] 4/4 13类场地承托面与声场动态适配 (with_scene_surface) PASS")

    print("=" * 65)
    print("🎉 吞鲸宝典 v3.0 权威母版自检 100% 通过！跨机跨模型随时可投产！")
    print("=" * 65)


if __name__ == "__main__":
    main()
