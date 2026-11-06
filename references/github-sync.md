# 吞鲸宝典 · 跨机同步与仓库维护指南 (Repository Sync Guide)

## 一、仓库信息
- **GitHub 仓库**：`https://github.com/RastaJiN/tunjing-baodian` (`main` 分支)
- **标准挂载路径**：`~/.hermes/skills/tunjing-baodian` 或本地 Agent Skills 目录

## 二、任意新机器 1:1 部署与验证三步法

1. **拉取或更新宝典**：
   ```bash
   git clone https://github.com/RastaJiN/tunjing-baodian.git
   # 或在已有目录执行 git pull
   ```
2. **运行组件完整性自检**：
   ```bash
   python scripts/selftest.py
   ```
3. **运行 Gate 1 ~ Gate 6 端到端闭环实测**：
   ```bash
   python scripts/dryrun_test.py
   ```
   当终端输出 `🎉 恭喜！吞鲸宝典 Gate 1 ~ Gate 6 全链路自检 100% 绿灯通关！` 时，说明当前机器环境、吞鲸内置真源矩阵、13 类场地适配与门禁系统 100% 就绪。

## 三、开发维护纪律
- **真源唯一性**：`references/tunjing_poses_matrix.json`、`references/transition_recipes.json`、`references/oneshot_transitions.json` 为唯一数据真源；`references/kinetic-positions.md` 由脚本从 JSON 自动生成，严禁手改导致脱节。
- **装配唯一性**：`scripts/tunjing_core.py` 为六段式提示词装配与 `with_scene_surface` 场地适配的唯一内核，`tunjing_scene.py` 与 `tunjing_storyboard.py` 统一调用该内核，严禁各写一份。
- **仓库卫生**：推送远端时严格排除 `__pycache__/` 与临时测试目录，确保远端仓库永远处于干净整洁的 Master 状态。
