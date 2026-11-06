# 🐳 吞鲸宝典 (Tunjing Baodian)

> 吞鲸工作室 · 精品漫剧极速生产引擎
> 绑定桌面《大人的工作台》真源，1:1 复刻其姿势矩阵与提示词装配逻辑。

---

## 安装

```bash
git clone https://github.com/RastaJiN/tunjing-baodian.git ~/.hermes/skills/tunjing-baodian
```

---

## 一键唤醒

会话中发送：
> **`吞鲸开始`**

系统挂载本宝典并初始化六大门禁状态机。

---

## 核心能力

### 1. 整段床戏自动拆镜（主轴）

```bash
python scripts/tunjing_scene.py --chain "kiss_fondle,bj,fingering,cunnilingus,missionary,cowgirl,doggy,cum_butt" --total 120 --scene "办公室"
```

输出 **29 镜分镜表 + 每镜完整送模提示词**：
- 每镜 2~6 秒（贴合硬件上限，不把多体位压进一镜）
- 逐镜标明**景别**（wide/mcu/cu/macro/hip/face）与**机位**（static_side/static_rear/low_hip/ots/high_angle 等）
- 每镜输出完整六段式 H3 提示词，可直接贴进 ComfyUI

加 `--table-only` 只看拆镜表，不出提示词。
加 `--lines "台词"` / `--idea "剧情"` 注入台词与用户介绍。

### 2. 单镜精修

```bash
python scripts/tunjing_storyboard.py --shot "bj,cowgirl,doggy,cum_butt" --dur 12 --scene "办公室"
```

### 3. 六大步进门禁

```bash
python scripts/tunjing_gatekeeper.py <项目目录> [1-6]
```

Gate 3 强制检查：逐镜景别、逐镜机位、平均单镜时长 ≤8s、换体位、3 次交合微距、口交特写。

---

## 真源数据（全部 1:1 提取自工作台 `h3-app.js`）

| 文件 | 内容 | 条数 |
|---|---|---|
| `references/workbench_poses_matrix.json` | 单体姿势（framing + beats 中英原文） | 50 套 |
| `references/oneshot_transitions.json` | 一键组合模板（仅作转场桥参考） | 9 套 |
| `references/transition_recipes.json` | 物理换位配方 | 40 条 |
| `references/kinetic-positions.md` | 上表的人类可读视图（由 JSON 生成） | — |
| `references/official-prompt-assembly-spec.md` | 六段式装配规格 | — |

---

## 核心纪律

1. **2 分钟床戏必须拆成 20~30 镜**，严禁把多个体位压进一个镜头；
2. **逐镜必给景别与机位**，缺一即不合格；
3. **全片纯血 Ref2V**，严禁 I2V 首帧垫图；
4. **正向肯定句压油**（工作流负向被清零，负向排油词无效）；
5. **动作文本禁止脑补**，必须从真源 JSON 取原文。

---

## 目标机自检

```bash
python scripts/dryrun_test.py
```

---

## 脚本一览

| 脚本 | 作用 |
|---|---|
| `tunjing_scene.py` | 整段拆镜 + 逐镜出完整提示词（主轴） |
| `tunjing_storyboard.py` | 单镜精修 / 一键组合复现 |
| `tunjing_core.py` | 提示词装配共享核心（唯一实现） |
| `tunjing_gatekeeper.py` | 六大步进门禁状态机 |
| `tunjing_compiler.py` | 提示词体检工具 |
| `tunjing_resolver.py` | 单个动作快速查询 |
| `dryrun_test.py` | 目标机最小闭环自检 |
