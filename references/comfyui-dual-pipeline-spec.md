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
   全片每一镜均由 **【女主 2x3 定版母版 (`<Picture 1>`) + 男主 2x3 定版母版 (`<Picture 2>`) + 1 张纯净场景底图 (`<Picture 3>`)】** 共同驱动，配合吞鲸标准六段式提示词直接生成视频，一致性最高、批量稳定性最强。

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
Skin & Lighting: authentic matte velvet skin finish, powdered dry complexion texture, natural human skin with visible fine pores and subtle dermal grain, soft subsurface scattering with gentle matte light absorption, heavily diffused soft ambient illumination, organic 35mm cinema film grain, photorealistic human anatomy
```

---

## 四、标准 Ref2V 节点拓扑与硬件参数基准

```text
[<Picture 1> 女主 2x3 母版 PNG (ref_image_0)] ➔ \
[<Picture 2> 男主 2x3 母版 PNG (ref_image_1)] ➔ ---> [MiniMax H3 ReferenceToVideo] ➔ VAE Decode ➔ 成片 MP4
[<Picture 3> 纯净场景底图 PNG (ref_image_2)] ➔ /
[<Picture 4~9> 近景承托面/道具母版 (ref_image_3~8, 按需通电)] ➔ /
[<Audio 1~3> 男女主定版干声 WAV (ref_audio_0~2, 锁死音色)]   ➔ /
[吞鲸标准六段式送模提示词文本]                               ➔ /
```

- **核心底模与 LoRA 黄金挂载**：
  - **Node 192 (`UNETLoader`)**：`minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors`
  - **Node 38 (`CLIPLoader`)**：优先挂载满血 8-bit 旋转量化版 `qwen3vl_32b_minimax_h3_ultra_uncensored_heretic_int8_convrot.safetensors`（大内存机器下替代 4-bit `nvfp4`，根治多参考图注意力丢失与复杂空间调度听不懂的问题；仅编码瞬间过显存，不影响采样耗时）
  - **Node 53 (`LoraLoaderModelOnly`)**：`minimax_h3_dmad_full_dareties_v4_step600_comfy_fro.safetensors` @ `0.80`
  - **Node 400 (`LoraLoaderModelOnly`)**：`MysticXXX_MMH3-V5-ref2va.safetensors`（Ref2VA 专用版；文戏/穿衣/空镜强制置 `0.0`，肉戏置 `0.45 ~ 0.50`）
  - **Node 404 (`LoraLoaderModelOnly`)**：`H3_RuMengSiHuan_1536-e8.safetensors` @ `0.80`
- **12GB 显卡低显存削峰四护法链（严禁断开或穿插 Node 333 SigmaShift）**：
  - `Node 331 (ModelAttentionBackend = comfy kitchen attention)` ➔ `Node 332 (BlockSparseAttention = sol-attn, tau=1.3, min_tokens=12288)` ➔ `Node 403 (MiniMaxLowVRAMAttention, head_chunks=2)` ➔ `Node 401 (MiniMaxChunkFeedForward, chunks=2, seq_threshold=4096)` ➔ `Node 397 (SelfLiftH3Sampler, lowres_scale=0.6, highres_tiling=True, upscaler_unload=True)`
  - **排雷铁律**：彻底从文/肉主工作流中物理移除悬空的 `Node 333 (MiniMaxH3SigmaShift, shift_video=12.0)` 以及 `Node 342~345/366` 武打加速 LoRA 组（武戏单独存为独立工作流备用），防止脚本误连导致人物橡皮泥拉扯或 3 倍速抽搐。
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
6. **双轨物理分流构图死锁（Composition Lock）与肢体减法**：
   - **交合特写轨 (`hip` / `macro`)**：强制注入 `COMPOSITION LOCK: Camera locked low-angle at pelvic level. Framed strictly from waist to mid-thigh. HEADS, FACES, AND UPPER TORSO ARE STRICTLY OUT OF FRAME.`，杜绝结合部上方出现浮空人脸。
   - **面部情绪轨 (`face` / `cu` / `mcu`)**：强制注入 `COMPOSITION LOCK: LOWER BODY AND GENITALIA STRICTLY OUT OF FRAME. Intercourse is depicted ONLY through rhythmic shoulder trembling and hair shaking caused by unseen off-screen thrusts.`，杜绝因景别裁切导致正戏无交合感。
   - **肢体减法**：特写框内最多允许 1 只手入画（`His left hand is the ONLY hand in frame`），其余肢体明文规定置于画框外，彻底消灭 4~5 只手的多肢鬼影。
5. **肢体减法与正向空间不变式（Positive Invariant）**：
   - **肢体减法**：特写框内最多允许 1 只手入画（`His left hand is the ONLY hand in frame`），其余肢体明文规定置于画框外，彻底消灭 4~5 只手的多肢鬼影。
   - **正向空间不变式（防画红线）**：严禁在画面段出现 `axis / line / lines / 越轴 / 轴线` 等具象构图线词，统一采用 `The camera stays on the same side of them throughout; <Subject 1> is on the left, <Subject 2> is on the right.`。
   - **硬质承托面排他强化与特写景深标桩**：在铁桌/办公台/墙边等非床场地做俯身或低姿动作时，正向必须强化硬质承托面材质，并保留 15%~20% 的浅景深硬质环境标桩（如 `Maintain 20% shallow depth-of-field background showing dark mahogany headboard`）。
6. **A/B/C 三档槽位物理隔离、单调服装状态机与空镜三不铁律**：
   - **单人镜/空镜槽位物理隔离**：单人特写镜必须将未出场角色的槽位替换为纯净场景底图占位（防背景裂殖第二张人脸鬼影）；纯环境空镜三槽全挂场景底图；`retention_analysis` 中 `<Subject 3>` 声明 `weak_reference for exact camera framing` 防广角透视拉扯。
   - **空镜三不铁律**：零胶片特效词（禁 `flashback / overexposed / halation / light flare` 防门框五金融化）、闭门底图禁写动态推门大位移、100% 锚定底图真实陈设白名单（单次动作禁跨时段写两遍）。
7. **黄金 LoRA 分级隔离、ComfyUI 启动参数与单实例防 OOM 锁**：
   - **ComfyUI 必加启动参数**：Windows 下运行 20GB+ H3 模型与 Qwen3-VL 32B 编码器，启动命令必须包含 `--lowvram --disable-smart-memory`（防大文件内存映射闪退与显存打满）。
   - **LoRA 文肉动态分级**：文戏/穿衣镜成人特征 LoRA 权重强制置 `0.0`（防正装长出器官），肉戏恢复 `0.45~0.50`；Node 53 (DMAD) 锁定 `0.60~0.80`；Node 250/252/265 保持动态帧长计算连线。
   - **真实目录动态寻址与单实例锁**：提交前通过 `/system_stats` 核验 `--input-directory` 真实挂载目录，使用全 ASCII 文件名；批跑启动前清理残留孤儿进程、清空 `/queue` 并调用 `POST /free` 冷却 10 秒，严禁双进程并发抢占显存引发 Node 397 (SelfLift) OOM。
   - **潜变量续写与母带合成**：超长连续镜头优先采用 `ComfyUI-H3-Continuum` 透传音视频潜变量上下文（4 chunks × 5s）；成片交付优先采用 FFmpeg `concat demuxer`（`-c copy`）无损缝合全长母带。
