# 吞鲸 ComfyUI 双轨渲染工作流与节点规范 (Dual Pipeline Spec)
> 任何机器 1:1 复现必须遵循的底层节点与环境契约。

---

## 一、双轨硬件与环境基准 (Hardware & Env Baseline)
- **最低显卡配置**：NVIDIA RTX 3060 12GB / RTX 4070 Ti 12GB 或更高（支持单卡渲染）；
- **宿主环境**：ComfyUI (原生或 Docker 版均可，监听端口默认 8188)；
- **底层生图底模**：全线采用**越狱解禁版底模 (Uncensored Checkpoints / GGUF)**，彻底释放成人解剖与真实交合生成能力；
- **底层视频模型**：MiniMax H3 (33B / INT8 近似) 或 同级开源影视级视频模型 (如 Wan2.1 / Seedance)。

---

## 一之一、越狱版底模实战防翻车铁律 (Uncensored Pitfalls)
1. **越狱底模出场景的“防发春脑补”断言**：
   越狱模型对 `bed, hotel, sofa, bathroom` 等词极度敏感，容易自动脑补裸体假人或情趣内衣残留。
   - **出纯场景时负向必须强拍死**：`human, person, woman, man, body, limbs, skin, nude, naked, clothes, underwear, lingerie, condom, sex toys, face`，确保场景 100% 纯净无人，防止进 I2V 裂殖出第三人！
2. **越狱底模出姿态关键帧的“全解剖释放”**：
   跑 POS-01 到 POS-12 姿态首帧时，直接调用 `kinetic-positions.md` 中的全套受力与解剖英文动量，越狱底模能直接出精准咬合与身体受力，彻底告别打码和融化。

---

## 二、轨道 A：【文戏与简单动作轨 · 纯血 Ref2V】
适用于：00:00 ~ 01:30 的剧情对话、站立对峙、单人走位、面部神态。

### 1. 核心节点拓扑
```
[角色 2x3 母版 PNG] ➔ LoadImage (Node A) ➔ \
[纯净场景底图 PNG] ➔ LoadImage (Node B) ➔ ---> [MiniMax H3 Video DiT / Ref2V Sampler] ➔ VAE Decode ➔ SaveVideo
[全英文物理动词文本] ➔ Text/Primitive (Node C) ➔ /
```
### 2. 关键运行参数 (死锁)
- **CFG**：1.0（禁止使用高 CFG，防止过饱和彩噪）；
- **Sampling Steps**：10 ~ 12 步；
- **Scheduler**：beta / simple；
- **画幅规格**：9:16 (864x1536 或 928x1664)；
- **物理帧长**：`length = 5 + 17 * N` (如 107 帧 = 4.46s)。

---

## 三、轨道 B：【高危复杂体位轨 · 姿态首帧 + I2V 启动】(绝不融化秘诀)
适用于：02:45 ~ 04:30 的 POS-01 到 POS-11 复杂交合、悬空、折叠深顶、深喉等高难度动作。

### 1. 为什么不能纯靠文生视频？
文生视频的 Cross-Attention 在计算两人多肢体复杂缠绕时会发生拓扑崩溃（出现三条腿、融化成橡皮泥）。因此必须在第一步把身体接触用高精度生图底模锁定！

### 2. 两阶段作业拓扑
```
【阶段 1：姿态关键帧锁定 (T2I / Inpainting)】
[男女素身母版] + [POS 姿态 ControlNet/OpenPose] ➔ Qwen-Image-2.1 / FLUX ➔ [100% 完美的交合关键帧 PNG]
                                                                        ↓
【阶段 2：动力学脉冲启动 (I2V)】
[该交合关键帧 PNG] ➔ LoadImage (作为 Initial Frame) ➔ [H3 / 视频 I2V Sampler] ➔ 输出 2.5 ~ 4.0s 猛烈受力冲撞
```
### 3. 关键运行参数
- **Motion Scale / Denoise**：0.65 ~ 0.80（既保持身体结合部不散架，又赋予肌肉与臀肉足够的撞击回弹）；
- **英文提示词**：直接调用 `kinetic-positions.md` 中的对应 `Prompt Block`。
