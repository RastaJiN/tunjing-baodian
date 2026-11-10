"""
吞鲸标准生产引擎 · 一键最小闭环全门禁通关测试 (Tunjing Full-Pipeline Dry-Run)
作用：
在任何机器上无需人工干预，一键实测验证整个吞鲸宝典从 Gate 1 到 Gate 6 的 100% 闭环能力：
1. 自动创建测试项目目录与定版资产占位 (Gate 1)
2. 自动生成包含吞鲸内置 pose id 的三幕式刀锋剧本 (Gate 2)
3. 自动调用 tunjing_scene.py 将 120s 床戏拆解为 29 个 2~6s 独立短镜，落盘 分镜.md + 视频提示词.md + 批量任务.json (Gate 3 & Gate 4)
4. 自动调用 tunjing_compiler.py 校验吞鲸标准六段式结构与正向压油词
5. 自动生成合格的生成前六维度终审报告 (Gate 5)
6. 逐步运行 tunjing_gatekeeper.py 跑通 Step 1 ➔ Step 6 全绿通关，并由 export_comfy_payload.py 核验批量任务包！
"""

import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import tunjing_scene as scene_mod
import tunjing_gatekeeper as gate_mod
import tunjing_compiler as comp_mod


def run_dryrun(target_dir):
    print("=" * 70)
    print("🐳 吞鲸宝典 · 纯血 Ref2V 全链路门禁 (Gate 1~6) 端到端闭环实测")
    print("=" * 70)

    # 清理旧状态确保从 Step 1 全新开始
    os.makedirs(target_dir, exist_ok=True)
    status_file = os.path.join(target_dir, ".tunjing_status.json")
    if os.path.exists(status_file):
        os.remove(status_file)

    # ── 1. 准备 Gate 1 资产目录 ──
    asset_dir = os.path.join(target_dir, "00_资产")
    os.makedirs(asset_dir, exist_ok=True)
    for fname in ("男主_穿衣与素身母版_2x3.png", "女主_穿衣与素身母版_2x3.png", "场景_顶奢办公室_scene.png"):
        fpath = os.path.join(asset_dir, fname)
        if not os.path.exists(fpath):
            with open(fpath, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"0" * 1024)

    assert gate_mod.check_gate(target_dir, 1), "Gate 1 资产门禁未通过！"

    # ── 2. 准备 Gate 2 刀锋剧本（显式使用吞鲸内置 pose id）──
    script_content = """# 吞鲸标准测试剧集 · EP01 刀锋剧本

## 第一幕：秘密撕扯与极限阻断
男主将文件拍在办公桌上，步步紧逼。
男主：<d>[Chinese] 你以为你能全身而退？这上面签着你的名字。</d>
女主：<d>[Chinese] 把东西还我！</d>
男主单手将她按在墙边（kiss_pin），门外突发脚步声停驻，两人瞬间屏息凝固。

## 第二幕：防线失守与羞耻前戏
危机暂退，男主展开凌厉前戏：调用吞鲸引擎 kiss_fondle（揉胸舌吻）➔ bj（跪姿口交）➔ fingering（手指扣插女穴）➔ cunnilingus（舔阴）。
男主：<d>[Chinese] 别出声，门外还没走远。</d>

## 第三幕：多体位清战与绝顶收网
进入主力冲撞：先以 missionary（传教士）破壁贯入，中途强制换体位至 cowgirl（女上位骑乘）与 doggy（后入趴跪），最后以 cum_butt（射在臀部）完成绝顶清算。
女主：<d>[Chinese] 别……求你……关灯……</d>
"""
    with open(os.path.join(target_dir, "剧本.md"), "w", encoding="utf-8") as f:
        f.write(script_content)

    assert gate_mod.check_gate(target_dir, 2), "Gate 2 剧本门禁未通过！"

    # ── 3. 调用 tunjing_scene.py 自动拆镜并落盘（驱动 Gate 3 & Gate 4）──
    poses = scene_mod.load_poses()
    chain = ["kiss_fondle", "bj", "fingering", "cunnilingus", "missionary", "cowgirl", "doggy", "cum_butt"]
    shots, actual = scene_mod.build_scene(chain, 120.0, poses)
    pose_names = "→".join(poses.get(p, {}).get("nameZh", p) for p in chain)
    _, pr_path, bj_path = scene_mod.save_project_artifacts(
        target_dir, shots, actual, 120.0,
        lines="嗯…啊…不要…", idea="executive office confrontation",
        scene="executive office", pose_names=pose_names
    )

    assert gate_mod.check_gate(target_dir, 3), "Gate 3 拆镜门禁未通过！"
    assert gate_mod.check_gate(target_dir, 4), "Gate 4 提示词门禁未通过！"

    # 额外用 tunjing_compiler.py 体检提示词文件
    with open(pr_path, "r", encoding="utf-8") as f:
        errs, warns = comp_mod.lint_tunjing_prompt(f.read())
    assert not errs, f"tunjing_compiler 体检报错: {errs}"
    print("[✓] tunjing_compiler.py 六段式体检 0 错误 PASS！")

    # ── 4. 准备 Gate 5 生成前自我终审报告 ──
    audit_dir = os.path.join(target_dir, "审查")
    os.makedirs(audit_dir, exist_ok=True)
    report_content = """# 吞鲸工作室 · 渲染放行终审报告 (Clearance Report)
- 剧集：吞鲸标准测试剧集 · EP01
- 自审执行人：鲸鲸 (执行导演)
- 审查结论：[PASS 放行]

### 核查清单对账：
1. 资产实名与槽位：[PASS] (男女母版与场景底图齐全，无第三人裂殖隐患)
2. 音画台词咬合：[PASS] (台词均满足 3.0字/s+1.0s 余量)
3. 换体位与特写契约：[PASS] (missionary ➔ cowgirl ➔ doggy，交合特写3次，口交特写齐全)
4. 受控运镜规范：[PASS] (逐镜标明景别与机位，无环绕/无快变焦)
5. 提示词纯净度：[PASS] (吞鲸标准六段式结构，内嵌正向肯定句压油词)
6. 纯血Ref2V单轨规范：[PASS] (全片 100% 纯血 Ref2V 单轨，零首帧垫图，29 镜每镜 2~5s)
"""
    with open(os.path.join(audit_dir, "生成前终审报告.md"), "w", encoding="utf-8") as f:
        f.write(report_content)

    assert gate_mod.check_gate(target_dir, 5), "Gate 5 终审门禁未通过！"
    assert gate_mod.check_gate(target_dir, 6), "Gate 6 渲染放行门禁未通过！"

    # ── 5. 调用 export_comfy_payload.py 核验最终批量任务包 ──
    rc = subprocess.call([sys.executable, os.path.join(SCRIPT_DIR, "export_comfy_payload.py"), target_dir])
    assert rc == 0, "export_comfy_payload.py 校验失败！"

    print("\n" + "=" * 70)
    print("🎉 恭喜！吞鲸宝典 Gate 1 ~ Gate 6 全链路自检 100% 绿灯通关！")
    print(f"产出目录: {target_dir}")
    print("=" * 70)


if __name__ == "__main__":
    out = os.path.join(os.path.expanduser("~"), "AppData", "Local", "hermes", "cache", "scratch", "tunjing_test_run")
    run_dryrun(out)
