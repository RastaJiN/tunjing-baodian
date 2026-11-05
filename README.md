# 吞鲸宝典 (Tunjing Baodian)

> 吞鲸工作室至高资产 · 文戏带刀有张力，动作带电有花样，步步门禁不跳步，工业流程一次过。

---

## 快速安装与使用 (Installation)

### 方式 1：标准 Skills 安装
```bash
npx skills add <你的GitHub用户名>/tunjing-baodian
```

### 方式 2：Git Clone 本地挂载
直接克隆到你的 Agent skills 目录：
```bash
git clone https://github.com/<你的GitHub用户名>/tunjing-baodian.git ~/.hermes/skills/tunjing-baodian
```

---

## 一键唤醒与启动

在与任何支持 Skills 的智能体（Hermes / Claude Code / Codex / 千问 / 豆包）会话中发送：
> **`吞鲸开始`**

系统将自动挂载本宝典并初始化 6 大步进门禁状态机。

---

## 核心资产架构

- **`SKILL.md`**：引擎总控中枢与唤醒契约；
- **`references/kinetic-positions.md`**：12 套实战生物力学体位字典（POS-01 到 POS-12，全套由支点、受力凹陷、脊柱反弓与神经痉挛写成）；
- **`references/shot-design-and-bounce.md`**：视听弹跳分镜规范（镜头组 + 1.5s 生理阻断微距）；
- **`references/pre-render-audit-standard.md`**：生成前终审六大冷血维度；
- **`references/comfyui-dual-pipeline-spec.md`**：ComfyUI 双轨渲染工作流与节点规范；
- **`scripts/tunjing_gatekeeper.py`**：六大刚性步进门禁状态机；
- **`scripts/dryrun_test.py`**：一键最小闭环跑通测试脚本；
- **`scripts/tunjing_compiler.py`**：全英文物理动量提示词编译器与体检工具。

---

## 目标机 1:1 出片自检

在任何新机器上下载后，运行：
```bash
python scripts/dryrun_test.py
```
验证帧长换算与 ComfyUI Payload 输出，全绿即可无缝接入生产。
