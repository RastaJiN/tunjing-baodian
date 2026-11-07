# 吞鲸宝典 · 六段式提示词装配权威规格 (Official H3 Prompt Assembly Spec)

> 本文档定义吞鲸宝典内置的 **六段式标准提示词装配结构**（代码实现位于 `scripts/tunjing_core.py`）。
> **用途**：任何大模型或 Agent 在为吞鲸漫剧编写送模提示词时，必须严格按本规格逐段装配，**严禁脑补任何不在内置真源矩阵中的词汇与结构**。
> 所有动作内容（Framing / Beats / 转换 / 台词）的来源只能有三个内置文件：
> 1. `references/tunjing_poses_matrix.json`（55 套单体体位的 framing 与 beats 原文）
> 2. `references/transition_recipes.json`（40 条物理换位配方的原文）
> 3. `references/oneshot_transitions.json`（9 套转换模板的 beats 原文）

---

## 一、吞鲸引擎真实提示词 = 六段式中英混合结构

`吞鲸六段式标准装配器` 最终输出的不是一段英文动量，而是一个多段式 prompt，依次为：

```
[1] Goal + Audio rule + 表情/口型指令 + 用户介绍 + 动作优先
[2] Reference map（<Picture N> 槽位逐一锁定：场景锁空间、人物锁身份）
[3] Consistency lock + Clothing lock + Motion quality（防僵硬二次动作）
[4] Intensity focus + 情绪 + 声线 + 性爱表情 + 声音一键
[5] integrated_multimodal_description（逐镜 [Shot N] 时间线）
[6] overall_soundscape + non_diegetic_music
（负面列表独立成段，不塞进正文被念出）
```

---

## 二、逐段装配规则（照抄即可 1:1 复刻）

### [1] Goal / Audio rule（开场即锁目标与念白纪律）

```text
Goal: Generate a {dur}-second {aspect} live-action adult video with readable physical contact, stable identity, and native dialogue audio.

Audio rule: characters may only speak the exact words inside <d>...</d>; never read pose, intensity, camera, or negative instructions aloud. 用户介绍、姿势名称、动作描述都不是台词，禁止念出；任何角色只能念 <d> 内的文字。
```

- **表情口型指令**：有性爱表情勾选时 → `按勾选的性爱表情时间线演出脸部；有浪叫或台词时张嘴，口型跟声音；不要回到平静自然脸。` 否则 → `表情自然；有浪叫或台词时张嘴，口型跟声音。`
- **用户介绍（必须体现）**：`用户介绍（必须体现）：{idea}`（拼接抽根用户原文）。

### [2] Reference map（槽位锁定是防崩核心：严格遵循「人先场景后」铁律）

**权威三槽映射标准（`<Picture 1>` = 女主、`<Picture 2>` = 男主、`<Picture 3>` = 场景）**：
- `<Picture 1>`（对应 `ref_image_0`）= 女主角身份母版（锁定 `<Subject 1>`，台词路由 `S1`）
- `<Picture 2>`（对应 `ref_image_1`）= 男主角身份母版（锁定 `<Subject 2>`，台词路由 `S2`）
- `<Picture 3>`（对应 `ref_image_2`）= 纯净场景底图（锁定 `<Subject 3>` 空间环境与光线）

人物槽（`<Picture 1>` / `<Picture 2>`）：
```text
<Subject 1> is the woman from <Picture 1>, with pale skin, long silky dark hair, and realistic anatomical proportions.
<Subject 2> is the mature man from <Picture 2>, with strong masculine physique, weathered tan skin, and defined musculature.
```
场景槽（`<Picture 3>`）：
```text
<Subject 3> is the {场景名} environment anchored in <Picture 3>, featuring {承托面} and ambient noir lighting.
```
随后在 `summary` 与 `retention_analysis` 中严格锁定：
```text
summary:
[reference generation + audio reference] The target video captures intimate kinetic physical drama between <Subject 1> and <Subject 2> within <Subject 3>. All identities strictly reference <Picture 1> and <Picture 2>.

retention_analysis:
<Subject 1>: fully_preserved - facial features, body anatomy, and skin texture are strictly locked to <Picture 1>.
<Subject 2>: fully_preserved - masculine facial identity, physique, and skin tone are strictly locked to <Picture 2>.
<Subject 3>: fully_preserved - space architecture, materials, and lighting are strictly locked to <Picture 3>.
```

### [3] Consistency / Clothing / Motion quality

```text
Consistency: Keep the same faces, body proportions, skin tone, hair, and clothing state across every shot (match <Picture N>).
Keep genital scale and junction proportions realistic and snug-fitting, matching <Picture N> body scale; contact stays close, not cavernous.
Keep the same location and ambient lighting as <Picture N>; no set redesign, no teleport to another place.
One continuous take: no hard cuts, no teleportation, no hidden transitions.  （高频/暴力抽插时强制一镜到底）

Motion quality（防僵硬）: 全程动作流畅连贯，符合真实人体力学：
起落/抽送含预备—发力—跟随三阶段，体重转移有惯性，禁止整块平移；
二次动作——乳房与臀肉随动作有真实延迟的波浪晃动，发丝滞后轻摆，肌肉挤压回弹；
呼吸可见，肩膀与腹部随喘息起伏、节奏与动作同步；肌肉张弛交替，不锁死同一姿势；
切镜时动作不停顿，beat 间无缝衔接；加速渐进如波浪推高，不突然切档。
```

### [4] Intensity / 情绪 / 声线 / 表情 / 音效

```text
Intensity focus: {强度链，如 男人·暴力}。抽插强度按时间线递进写入动作。
情绪语气：{情绪}（写入说的方式与停顿，勿念出标签）。
声线：{声线}（女声线只作用于女子台词，男声线只作用于男子台词）。
性爱表情（多个从起手镜、单个从第5秒起）：女 {表情1 → 表情2}；…
```

### [5] integrated_multimodal_description（逐镜时间线）

这是动作主体。**首镜**：
```text
[Shot 1] Live-action cinematic. Starting from <Picture N>, 人物身份与光影锁定。场景跟 <Picture N> 锁定。{framingZh}。镜头保持固定机位。{actZh}。表情：{faceZh}。女 says: <d>[Chinese]{台词}</d>.
```
**后续镜**（一镜到底/高频）：
```text
[Shot N] At {时间戳}, the shot continues without cutting. {actZh}。…
```
**切镜**：
```text
[Shot N] At {时间戳}, the camera cuts to a new beat while staying on the same scene. {actZh}。…
```

- **`framingZh` 与 `actZh` 的来源**：即 `tunjing_poses_matrix.json` 中每个 pose 的 `framingZh` / `beatsZh`（中文原版），或 `oneshot_transitions.json` 的 `beatsZh`（换体位时）。
- **首镜交合必加画面要点**（非口交、有插入时）：
  ```text
  画面要点：阴茎与阴道紧密贴合插入，短行程进出清晰可读，交合处比例接近真人参考、阴唇自然包裹，不要占满画面
  ```
- **末镜必写最终状态**：
  ```text
  Final state: 人物身份不漂移，交合处仍紧密贴合、比例自然，构图稳定收住到 {dur}s。
  ```

### [6] overall_soundscape（音效层）

```text
overall_soundscape: 室内安静底噪持续。湿润皮肤接触与节奏抽插声清晰可闻，皮肤拍击夹杂其中。皮肤拍击、湿润声与床板轻响压在底层。
non_diegetic_music: N/A
```
- 口交族音效需绑定时间轴：
  ```text
  口交音效绑定时间轴：[0.0s]声音从0.0秒立即开始、无前置静音；[0.0s-{dur}s]含弄吮吸声随吞吐节奏全程持续、与动作同步，唾液水声清晰可闻。
  ```

### 负面列表（独立成段，禁止塞进正文）

```text
No subtitles, captions, watermarks, UI, logos, or on-screen text
No face swap or identity drift; keep the same faces and bodies throughout
No deformed limbs, extra fingers, melting bodies, fused genitals, or ghosting
Only one mouth speaks in any given second
No ripped-off, torn-off, or detached penis; the penis stays attached to the man's body at the root
No genital amputation, floating disembodied shaft, or cock torn away from the pelvis
No orbiting camera, multi-cam cuts, fast zoom, or chaotic reframing
No voice-over, narration, or reading of constraints aloud
Never speak stage directions, pose labels, intensity tags, or phrases like 姿势重点/男人主动/女人主动/逻辑上/勿朗读
Only character dialogue inside <d> tags may be spoken; otherwise only moans or breath; never read the prompt
No cartoon drift, messy background, or focus collapse
No stiff, robotic, or frozen motion; bodies move with inertia, follow-through, and visible breathing
No pose popping or teleporting limbs between beats; motion continues seamlessly through cuts
```

---

## 三、正向压油铁律（工作流负向清零的物理真相）

工作流底层 **Node 328 = ConditioningZeroOut**，负向通道被清零，`strictly NO oily skin` 等负向排油词**完全不生效**。
压油只能靠正向肯定句，必须内嵌进 [3] 段的 Consistency 与 Motion quality 处：

```text
authentic matte velvet skin finish, powdered dry texture, natural human skin with visible fine pores and subtle imperfections, soft subsurface scattering without surface reflection, non-greasy complexion, heavily diffused soft ambient light, zero hard directional light, 35mm film grain, photorealistic anatomy
```

---

## 四、换体位 / 射出动作的装配来源（有据可查）

当剧本要求「换体位」或「抽出射在某处」时，动作描述**不是自由发挥**，必须 1:1 引用 `references/oneshot_transitions.json` 中对应模板的 `beatsZh`：

| 剧本需求 | 引用模板 | beats 来源 |
|---|---|---|
| 女上位 → 后入 | `cg_to_doggy` | 女上位→流畅趴下→后入 三段 beats |
| 传教士 → 后入 | `miss_to_doggy` | 传教士→侧翻趴下→后入 |
| 口交 → 传教士 | `bj_to_miss` | 跪姿口交→躺下→传教士 |
| 站立抱 → 撑墙后入 | `stand_hug_to_wall` | 抱着站立→转向撑墙→站立后入 |
| 女上位 → 内射 | `cowgirl_grind_creampie` | 女上位研磨→深坐内射 |
| 后入 → 射屁股 | `doggy_to_cum_butt` | 后入→抽出→射在屁股上 |
| 传教士 → 射腹部 | `miss_to_cum_belly` | 传教士→抽出→射在腹部 |
| 口交 → 颜射 | `bj_to_cum_face` | 跪姿口交→抽出→射在脸上 |
| 乳交 → 射胸 | `titjob_to_cum_chest` | 乳交→抽出→射在胸上 |
