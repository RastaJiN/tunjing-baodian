# 吞鲸宝典 v4.0 · 六段式全肯定提示词装配权威规格 (Official H3 Prompt Assembly Spec)

> 本文档定义吞鲸宝典内置的 **v4.0 六段式纯英文全肯定提示词装配结构**（代码唯一权威实现位于 `scripts/tunjing_core.py`）。
> **核心铁律**：任何大模型或 Agent 在为吞鲸剧集编写送模提示词时，必须优先直接调用 `tunjing_scene.py` / `tunjing_core.py` 自动生成；若人工审校，必须 100% 遵循本规格的 **纯英文正文（`<d>` 内中文台词除外）+ R1~R12 全肯定无否定语法**。
> 所有动作内容（Framing / Beats / 转换）的来源只能有三个内置文件：
> 1. `references/tunjing_poses_matrix.json`（87 套全剧集调度、挑逗、对峙与核心体位真源矩阵）
> 2. `references/transition_recipes.json`（40 条物理换位配方的原文）
> 3. `references/oneshot_transitions.json`（9 套转换模板的 beats 原文）

---

## 一、吞鲸 v4.0 送模提示词 = 六段式纯英文全肯定结构（零汉字残留、零负面尾块）

送入 ComfyUI `Node 263` 的正向提示词必须由以下六大英文模块顺序组成（**严禁在 `<d>...</d>` 标签外出现任何中文字符，严禁在末尾拼接 `=== NEGATIVE ===` 块**）：

```text
[1] Goal & Audio Contract（时长、画幅、发声纪律）
[2] Anchoring & Consistency -> subject_definitions + Audio timbre anchors（<Picture 1~3> 与 <Audio 1~2> 槽位绑定 + 家具人体高度锚点）
[3] summary + retention_analysis（任务类型前缀 + fully_preserved / weak_reference 保留强度）
[4] Consistency + Skin & Lighting (DE_OIL) + Motion quality + MOTION FLOOR（全肯定压油词 + 底噪生命力锁）
[5] Integrated Multimodal Description -> Camera: + [Shot N] (分号分割先静后动运镜与动作) + SPEECH:（同行台词与闭口锁）
[6] Overall Soundscape -> overall_soundscape + non_diegetic_music: N/A
```

---

## 二、逐段装配标准模板（与 `tunjing_core.py` 1:1 严格对齐）

### [1] Goal & Audio Contract（全肯定描述，零否定词）

```text
Goal & Audio Contract: Generate a {dur:.2f}-second {aspect} live-action cinema video with readable physical biomechanics, locked identity consistency, and synchronized native audio.
Audio rule: characters vocalize exclusively the exact words enclosed inside <d>...</d> tags; all other moments contain pure physical foley and natural breathing. Never speak stage directions, pose names, camera moves, or any instruction aloud; only the dialogue inside <d> tags is spoken, everything else stays as unvoiced visual action.
Voice discipline: <d> content is the sole spoken text; pose labels, intensity tags, and framing terms are never narrated, only enacted silently on screen.
```

> 注：`{aspect}` 为画幅参数（`9:16` 竖屏默认 / `16:9` 横屏 / `1:1` 方屏），由 `--aspect` 贯穿全链路，横屏时整套景别/机位/运镜语言同步切换（见铁律 10b）。反念稿两行（`Never speak stage directions` + `Voice discipline`）是对齐外部 H3 生态后的硬性新增，用于压掉「模型把 Goal/姿势名/机位/负向等工程文本当台词念出来」的隐患。

### [2] Anchoring & Consistency (`subject_definitions`)

- **双人同框镜 (`A_two_shot`)**：
  ```text
  Anchoring & Consistency:
  subject_definitions:
  <Subject 1> is the young woman anchored in <Picture 1>, preserving her exact facial structure, hairstyle, skin tone, and anatomical proportions.
  <Subject 2> is the mature man anchored in <Picture 2>, preserving his exact masculine facial identity, hairstyle, skin tone, and muscular build.
  <Subject 3> is the {scene_en} environment anchored in <Picture 3>, featuring {surf_noun} ({height_anchor}) and ambient lighting.
  Audio timbre anchors: <Audio 1> locks the vocal timbre of <Subject 1> (S1); <Audio 2> locks the vocal timbre of <Subject 2> (S2).
  ```
- **单人正反打镜 (`B_solo_female` / `B_solo_male`)**：只定义在场的单个角色与 `<Subject 3>`，从文本与参考图槽位两端物理隔离不在场的异性角色，彻底根除背景鬼脸裂殖。
- **特写/微距镜头头部自动瘦身 (`macro` / `face`)**：当景别为 `macro` 或 `face` 时，`<Subject 3>` 自动裁剪掉全景房间与大件家具描述，仅写 `showing close-range {surf_pad} texture in 20% shallow depth-of-field`，防止模型因看到全景房间描述而强行把特写拉宽为中景。

### [3] `summary` 与 `retention_analysis`

```text
summary:
[reference generation + audio reference] High-tension dramatic interaction between <Subject 1> and <Subject 2> within <Subject 3>.

retention_analysis:
<Subject 1>: fully_preserved - facial identity, exact hairstyle, body anatomy, and skin texture are strictly locked to <Picture 1>.
<Subject 2>: fully_preserved - masculine facial identity, physique, and skin tone are strictly locked to <Picture 2>.
<Subject 3>: fully_preserved for surface texture and lighting direction from <Picture 3>; weak_reference for exact camera framing.
```

### [4] `Consistency` + 全肯定压油 (`DE_OIL`) + `MOTION FLOOR`

工作流底层 `Node 328 = ConditioningZeroOut` 将负向清零，`CFG = 1.0`。正向严禁出现 `without / non- / zero / no` 等否定词，必须 100% 使用全肯定物理描述：

```text
Consistency: Keep the same faces, body proportions, skin tone, hairstyle, and anatomical scale throughout. Two adults in frame. The camera stays on the same side of them throughout; <Subject 1> is on the left, <Subject 2> is on the right.
Skin & Lighting: authentic matte velvet skin finish, powdered dry complexion texture, natural human skin with visible fine pores and subtle dermal grain, soft subsurface scattering with gentle matte light absorption, heavily diffused soft ambient illumination, organic 35mm cinema film grain, photorealistic human anatomy, clean full-bleed raw 35mm cinema frame
Motion quality (Anti-Stiffness): Smooth continuous human kinematics with visible inertia, follow-through, and natural breathing. Breasts and buttocks exhibit authentic delayed wave jiggle and recoil upon impact.
MOTION FLOOR: Continuous organic human micro-kinematics throughout every second; visible ribcage and collarbone breathing expansion of 1 cm, subtle weight shifts across the support surface, natural hair strand micro-sway, and realistic soft-tissue recoil.
```

### [5] `Integrated Multimodal Description`（先静后动运镜 + 分号分割 + 同行 `SPEECH:`）

```text
Integrated Multimodal Description:
integrated_multimodal_description:
Camera: {size_desc}, 0.00s to 1.00s holds steady locking the initial posture, then from 1.00s to {t_move_end:.2f}s {cam_desc}, holding steady for the final 0.80s.
[Shot 1] Live-action cinematic, {size_desc}, 0.00s to 1.00s holds steady locking the initial posture, then from 1.00s to {t_move_end:.2f}s {cam_desc}, holding steady for the final 0.80s; {COMPOSITION_LOCK}From 0.00s, <Subject 1> and <Subject 2> in <Subject 3>: {action_en}.
SPEECH: From {t_mid_start:.2f}s to {t_mid_end:.2f}s, {golden_emotion_cue}, <Subject 2> (S2) says: <d>[Chinese]{台词}</d> while <Subject 1> (S1) keeps her lips completely closed and motionless.
```

### [6] `Overall Soundscape`

```text
Overall Soundscape:
overall_soundscape: Quiet room tone continues throughout. Rhythmic skin-on-skin collision slaps, viscous lubrication friction, heavy ragged breathing, and subtle {surf_sfx}.
non_diegetic_music: N/A

[Visual Constraints | Do Not Speak]
(visual/audio guidance only; never voiced, never narrated)
- only one mouth speaks in any given second; non-speaking characters keep lips softly closed and natural
- clean full-bleed raw 35mm cinema frame with no on-screen overlays or UI elements
- same faces, body proportions, and identity across every beat; no identity drift, no extra limbs, no ghosting
- stable composition; cuts change framing and beat only, never identity or scene
```

> 注：`[Visual Constraints | Do Not Speak]` 负向声明锚为对齐外部 H3 生态后的新增段，置于 footer 末尾。前置声明「这些是视觉约束、绝不出声不朗读」，既补视觉约束语义又压掉模型把它们念出来。**注意：此段只放反向注意力不敏感的约束语义，严禁放入 `NO SUBTITLES` / `no captions` 等字幕词根（会诱发字幕烫印）**。

---

## 三、四大字幕烫印死刑禁令（100% 必拦截红线）

实测铁证表明，以下 4 种错误写法会直接触发 `qwen3vl_32b` 在第 3 秒台词发声瞬间于人物腰腹部渲染出白底描边中文字幕，`tunjing_compiler.py` 与 `tunjing_gatekeeper.py` 见到即判 FAIL：

1. **严禁在正向提示词末尾保留 `=== NEGATIVE ===` 块**：在 `CFG=1.0` + `Node 328 ConditioningZeroOut` 架构下，任何留在 `Node 263` 文本里的 `=== NEGATIVE === No subtitles, captions...` 都会被当成正向指令编码！
2. **严禁在正向提示词任何位置写 `NO SUBTITLES` / `NO CAPTIONS` / `NO ON-SCREEN TEXT` / `NO BURN-IN TEXT` / `TEXT BAN`**：模型对 `NO` 否定词不敏感，但对 `SUBTITLES / CAPTIONS / ON-SCREEN TEXT` 词根极度敏感；写得越多，越会在画面中央排版出字幕！正向防字只需写 `clean full-bleed raw 35mm cinema frame`。
3. **严禁将 `says:` 与 `<d>[Chinese]...</d>` 回车断成两行**：写成 `<Subject 2> (S2) says:\n<d>[Chinese]...</d>` 会被多模态编码器识别为“影视剧 SRT 字幕轨块”，必须同行紧接写为 `<Subject 2> (S2) says: <d>[Chinese]...</d>`！
4. **严禁在 `At 0.00s,` 后机械复读 `mcu, static_side;` 等工程代号**：分号 `;` 之后只能写纯自然英文物理动作，严禁复读景别机位代码破坏构图切边。
