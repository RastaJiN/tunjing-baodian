# 吞鲸高能戏双阶梯提示词编写规范 (Dual-Prompt Protocol for High-Tension Scenes)
> 吞鲸工作室专属标准 · 复杂高能交合戏必须严格解耦为：【T2I 静态姿态提示词】+【I2V 动力学动量提示词】。
> 严禁拿生图提示词直接喂视频模型，也严禁拿视频动量词去生图！两套提示词各司其职。

---

## 核心设计哲学：【先定姿态，后给动力】

| 阶段 | 任务目标 | 核心抓手 | 提示词重点 |
|---|---|---|---|
| **第一阶：T2I 静态关键帧** | 锁死男女骨相、姿态几何、解剖接触点、皮肤水光 | ControlNet Depth + Qwen 2.1 + NSFW LoRA | **七支柱静态结构**：机位、人物体态、四肢着力点、解剖结合部、光影水汽、胶片质感 |
| **第二阶：I2V 动力学视频** | 启动抽送受力、臀肉凹陷、脊柱波浪、音画台词咬合 | MiniMax H3 / 视频模型 (Denoise 0.65~0.75) | **纯英文物理动量**：从首帧继承姿态、前后冲撞矢量、受力反弹、呼吸拟音、`<d>` 台词 |

---

## 实战案例：以 POS-01 (办公桌沿·悬空后入) 为例

### 【第一套：T2I 静态姿态提示词 (生图用 · Qwen 2.1)】
- **作用**：配合深度图，15 秒生成一张 1152×1728、没有多余肢体、男女身份锁死的高精交合首帧。
- **模板示例**：
```text
A hyper-realistic photograph, tight medium side-angle shot, cinematic dim lighting with cold rim light. The female character has her upper body pressed flat against a dark polished mahogany desk, loose damp dark hair falling forward over her cheek, both palms stretched out flat against the wood with knuckles white under tension. The male character stands flush behind her, his large muscular hands locked firmly onto her pelvic bones, pulling her hips back into tight interlocking contact. Her spine is hyperextended in a sharp concave curve, lower back hollowed, gluteal muscles compressed against his thighs. Natural skin texture with visible fine pores, glistening sweat sheen along collarbones, sharp anatomical junction. 8k resolution, authentic matte velvet skin, candid caught-in-the-moment intensity, photorealistic anatomy, strictly zero extra limbs.
```

---

### 【第二套：I2V 动力学动量提示词 (视频用 · MiniMax H3)】
- **作用**：以此关键帧为首帧，启动 4~6 秒的猛烈抽送动力学与受力回弹，绝不让模型重新猜姿势。
- **模板示例**：
```text
Goal & Audio Contract:
9:16 vertical, length = 158 frames (6.58s). At 0.00s, actively in motion, inheriting the exact physical posture from the initial keyframe. Strictly NO camera movement, camera locked at stationary side angle at hip height. Characters may only speak the exact words inside <d>...</d>.

Anchoring & Consistency:
The initial keyframe is the definitive reference for body contact, desk position, and limb placement. Every element present in the initial frame keeps its exact shape and relative coordinates; generate only continuous forward kinetic thrusts and tissue compression after 0.00s.

Integrated Multimodal Description:
[Shot 1] 00:00.000
The male character maintains his tight grip on her pelvic crest, driving forward in dense, continuous rhythmic penetrative thrusts into her body. With each heavy kinetic impact, her torso presses deeper against the dark mahogany desk, her palms sliding forward by inches against the wood as her spine hyperextends into a trembling arch. Her gluteal tissue and upper thigh flesh visibly compress and recoil upon each collision, loose hair swaying in rhythm.
SPEECH: (S1) (low guttural whisper against her neck) says: <d>[Chinese] 抓紧了……别让门外加班的人听见你的动静。</d> while her lips remain parted in breathless gasps.

Overall Soundscape:
Realistic acoustic foley: heavy rhythmic skin-on-skin pelvic impact slapping, sharp wood resonance vibration, rustle of crumpled skirt fabric, heavy masculine breathing and sharp feminine gasps, non_diegetic_music: N/A.
```

---

## 分镜与自动化文件落地规范

在 `分镜.md` 中，凡是标记为 `[Track: I2V_Pose]` 的镜头，必须成对输出两套字段：
```markdown
### SHOT-04 [Track: I2V_Pose]
- 时长: 6.5s (158 帧)
- 关联姿态: POS-01 (办公桌后入) + Depth_P007_side.png
- **T2I 关键帧生图词**: (写入 00_资产/关键帧提示词/SHOT-04_t2i.txt)
- **I2V 动力学生成词**: (写入 视频提示词.md 中的 SHOT-04 代码块)
```
门禁脚本 `tunjing_gatekeeper.py` 会在 Gate 4 自动校验：
`[Track: I2V_Pose]` 镜头是否**同时具备 T2I 生图词与 I2V 动量词**，缺一不可！
