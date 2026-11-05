# Tunjing Adult Drama Engine (吞鲸·成人漫剧极速生产引擎)

> 吞鲸工作室专属资产 · 文戏带刀有张力，做爱带电有花样，步步门禁不跳步，工业流程一次过。

---

## 快速安装与使用 (Installation)

### 方式 1：标准 Skills 安装
```bash
npx skills add <你的GitHub用户名>/tunjing-adult-drama-engine
```

### 方式 2：Git Clone 本地挂载
直接克隆到你的 Agent skills 目录：
```bash
git clone https://github.com/<你的GitHub用户名>/tunjing-adult-drama-engine.git ~/.hermes/skills/tunjing-adult-drama-engine
```

---

## 一键唤醒与启动

在与任何支持 Skills 的智能体（Hermes / Claude Code / Codex / 千问 / 豆包）会话中发送：
> **`吞鲸开始`**

系统将自动挂载本引擎并初始化 5 大步进门禁状态机。

---

## 核心资产架构

- **`SKILL.md`**：引擎总控中枢与唤醒契约；
- **`references/kinetic-positions.md`**：12 套实战生物力学体位字典（POS-01 到 POS-12，全套由支点、受力凹陷、脊柱反弓与神经痉挛写成）；
- **`references/shot-design-and-bounce.md`**：视听弹跳分镜规范（镜头组 + 1.5s 生理阻断微距）；
- **`references/comfyui-dual-pipeline-spec.md`**：ComfyUI 双轨渲染工作流与节点规范（文戏 Ref2V / 肉戏 I2V 垫图）；
- **`scripts/tunjing_gatekeeper.py`**：五大刚性步进门禁状态机；
- **`scripts/dryrun_test.py`**：一键最小闭环跑通测试脚本；
- **`scripts/tunjing_compiler.py`**：全英文物理动量提示词编译器与体检工具。

---

## 目标机 1:1 出片自检

在任何新机器上下载后，运行：
```bash
python scripts/dryrun_test.py
```
验证帧长换算与 ComfyUI Payload 输出，全绿即可无缝接入生产。
