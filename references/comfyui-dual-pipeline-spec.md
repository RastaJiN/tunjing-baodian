# 吞鲸纯血 Ref2V 生产管线规范 (Tunjing Pure Ref2V Pipeline Specification)
> 继承自吞鲸工作室《纯血 Ref2V 核心生产宪章》
> 唯一铁律：彻底摒弃单镜首帧依赖（I2V 禁令），全片 100% 采用全局母版 Ref2V 一采直出！

---

## 一、为什么彻底封杀单镜首帧垫图 (I2V)？
1. **Cross-Attention 注意力竞争导致骨骼漂移与换脸**：
   在视频扩散模型（MiniMax H3）中，若每镜单独抽一张首帧图喂入，首帧图的局部光影/姿态会与全局角色 2x3 母版发生剧烈的特征争夺，导致人物五官变形、身材比例坍塌甚至多肢畸变；
2. **流程割裂摧毁批量自动化**：
   单镜抽首帧迫使生产管线中断，需要人工切图、选图，无法跑通全自动队列；
3. **纯血双锚定真理**：
   全片每一镜均由 **【1 张纯净场景底图 (`<Picture 1>`) + 男女角色 2x3 定版母版 (`<Picture 2>`, `<Picture 3>`)】** 共同驱动，配合吞鲸标准六段式提示词直接生成视频，一致性最高、批量稳定性最强。

---

## 二、纯血 Ref2V 攻克高难度体位不融化的三大物理法则

1. **核心交合强制收缩景别（算力独占）**：
   - 严禁在大全景 (`wide`) 中让模型同时计算全身四肢 + 两张正脸 + 复杂交合（算力必然过载融化）；
   - 核心冲撞镜头强制收紧为 **中近景 (`mcu`)、腰胯特写 (`hip`) 或结合部微距 (`macro`)**，将扩散算力 100% 集中于腰臀冲撞、软组织受力回弹与局部接触点。
2. **面部微表情注意力交棒**：
   - 激烈动作中的失神、咬唇、泪痕，交棒给相邻的 **1.5s~3.0s 独立面部/微距特写 (`face` / `macro`)**，通过弹跳剪辑组合出完整的视听高潮。
3. **0.00s 空间接触死锁与防僵硬二次动作**：
   - 每个动作镜头从 `0.00s` 起即处于接触/结合就位状态（1:1 调用吞鲸引擎 `tunjing_poses_matrix.json` 的 `beats` 原文），杜绝前戏漫游穿模；
   - 全局挂载吞鲸引擎 `Motion quality（防僵硬）` 锁：包含预备—发力—跟随三阶段惯性、二次动作波浪晃动与呼吸起伏。

---

## 三、工作流负向清零真相与【正向肯定句绝对压油】

吞鲸宝典内置引擎底层工作流（`H3 标准工作流`）中，**Node 328 = `ConditioningZeroOut` 将负向条件通道直接清零**。
因此，任何写在负向里的排油词在物理上均不参与采样计算，**压除 LoRA 高光油腻感必须且只能靠正向肯定句**（已固化于 `tunjing_core.py` 的 `DE_OIL` 常量中）：

```text
Skin & Lighting: authentic matte velvet skin finish, powdered dry texture, natural human skin with visible fine pores and subtle imperfections, soft subsurface scattering without surface reflection, non-greasy complexion, heavily diffused soft ambient light, zero hard directional light, 35mm film grain, photorealistic anatomy
```

---

## 四、标准 Ref2V 节点拓扑与硬件参数基准

```text
[<Picture 1> 纯净场景底图 PNG] ➔ \
[<Picture 2> 女主 2x3 母版 PNG] ➔ ---> [MiniMax H3 ReferenceToVideo] ➔ VAE Decode ➔ 成片 MP4
[<Picture 3> 男主 2x3 母版 PNG] ➔ /
[吞鲸标准六段式送模提示词文本]    ➔ /
```

- **CFG**：`1.0`
- **Sampling Steps**：`10 ~ 12`
- **Scheduler**：`beta` / `simple`
- **画幅规格**：`9:16` (`864x1536` 或 `928x1664`)
- **严格物理帧长公式**：`length = 5 + 17 * N`（由 `tunjing_scene.py` 按单镜秒数自动换算写入 `批量任务.json`）

---

## 五、渲染出片入库与防踩坑物理铁律（2026一线实测定稿）

1. **`VHS_VideoCombine` 取件真理（优先取 `-audio.mp4`）**：
   - `VHS_VideoCombine` 在挂了音频渲染时，虽然本地磁盘会产出主视频（无声版）与 `-audio.mp4`（带音轨版）两个文件，但 ComfyUI `/history/<prompt_id>` 接口的 `outputs` **只返回 `-audio.mp4` 一个文件名**！
   - 下游入库脚本必须**优先提取 `-audio.mp4`** 作为带声音的正式成片，严禁使用“跳过 audio”的筛选逻辑，否则会导致筛空丢片、白跑整轮任务！
2. **严禁开场大全景脱衣（防遛鸟）**：
   - 若第一镜为 `undress`（脱衣诱惑），景别强制收紧为 `mcu`（中近景）或 `cu`（特写），把画面锁定在肩颈与衣领扣子滑落，男方衣着完整，物理上严禁第 1 帧生殖器露出！
3. **前戏严禁插入要点**：
   - `undress`、`kiss_fondle`、`breast_rub`、`nipple_lick` 等前戏体位及转场桥镜，严禁带入任何“阴茎与阴道紧密贴合插入”语句，防止模型动作精神分裂与动作打架。
4. **核心动作全英文物理力学驱动**：
   - 严格遵循 MiniMax H3 官方模型特性，动作描述 100% 采用吞鲸矩阵内置的 `POSE_EN` 纯英文物理力学（`beatsEn` 与 `framingEn`），台词保留 `<d>[Chinese]...</d>`，彻底杜绝中文散文导致的动作漂移与纯灰影棚跑偏！
5. **接吻防蛇信子形态锁**：
   - 接吻类镜头统一注入物理边界：`lips gently parted, subtle tongue contact, natural human lips anatomy, no exaggerated tongue protrusion`，防止舌头拉伸变形。
