# 龚浩 Snail 工业级分镜与提示词架构剖析报告

本规范由吞鲸工作室整理，100% 提取自龚浩 Snail 工作室 9 部开源短片（《一代宗师》、《少帅》、《当古代圣贤遇上现代牛马》、《像当初见面那样》等）的核心工程母版，旨在为吞鲸宝典提供顶层电影级叙事、空间调度与声学一致性范式。

---

## 一、Snail 标准提示词四段式架构 (The 4-Block Standard)

在 MiniMax H3 跑多参考图视频生成时，Snail 确立了一套无可挑剔的工业级 Prompt 装配结构：

```text
1. subject_definitions:
   - 严密定义 <Subject 1> 至 <Subject N>
   - 明确每张参考图 <Picture 1> ~ <Picture 5> 的机器职能

2. summary:
   - 单镜/单轮目标概述：时长、镜头数、核心冲突与对位逻辑

3. retention_analysis:
   - 资产留存刚性契约：哪些人脸、衣服、发型、空间位置是 fully_preserved，哪些是显式动作演绎

4. detailed_description:
   - 核心分镜调度，精细到 [Shot 1] [Shot 2] [Shot 3] 的毫秒级时间轴、声学 DNA、动作起止与抽帧气口

5. overall_soundscape:
   - 环境底噪、肢体摩擦声、台词清晰度与禁令（禁止罐头笑声、禁止多余旁白）
```

---

## 二、五图空间拓扑规范 (The 5-Picture Spatial Topology)

彻底消灭角色瞬移、换脸和空间错乱的终极配方：

| 图片标签 | 机器语义角色 | 严格约束与行为定义 |
| :--- | :--- | :--- |
| `<Picture 1>` | **Female/Male Identity 1** | **纯身份卡**。仅用于锁死主角五官、发型、肤色，严禁作为开场第一帧！ |
| `<Picture 2>` | **Male/Female Identity 2** | **纯身份卡**。锁死对戏角色五官、体型、服装，严禁直接作为开场帧！ |
| `<Picture 3>` | **Master Spatial Anchor** | **母体空间大景**。固定房间透视、采光窗口、地面材质、家具朝向，提供全景坐标系。 |
| `<Picture 4>` | **Shot 1 Departure Anchor** | **起势位移源**。镜头 1 的开场构图，规定角色从何种姿势结束并开始移动（显式动作起点）。 |
| `<Picture 5>` | **Shot 2/3 Interaction Anchor** | **交锋落位点**。双人贴合、对峙、交合的终点机位，锁死特写双人构图。 |

---

## 三、显式动量与反瞬移工程 (Anti-Teleportation Engineering)

### 1. 物理换位显式化
所有体位转换、走位与推拉必须写出肉眼可见的力学支点转移：
- ❌ 错误（AI 瞎猜瞬移）：`The man moves to the bed and enters her.`
- ✅ 正确（Snail/吞鲸母版）：
  `The man lowers his right palm, shifts his center of gravity forward onto the soft mattress, bringing his left knee between her thighs. The camera tracks gently downward with his descending spine, capturing radial fabric tension on the silk sheet. Nobody changes posture or place instantaneously; physical movement develops visibly across cuts.`

### 2. 剪辑师定格抽帧气口 (Editor's Freeze Beat)
在每个镜头或问答段落的最后 1.2s ~ 1.8s，强制让角色执行：
`close lips, chin lifts slightly, chest heaves with heavy natural breathing, preserve a nearly still reaction for the editor's freeze beat.`
- 为剪辑师打字幕、做音效重音、转场切镜预留绝对干净的物理停顿。

---

## 四、角色固定声学 DNA (Fixed Acoustic DNA)

严禁跨镜头声线漂移，对白与喘息必须具备生物声学约束：

```text
Fixed voice specification template:
Use exactly this fixed voice: An adult [male/female] [register: low-mid baritone / upper-mid soprano], [resonance: grounded chest / soft rounded airy], with [texture: lightly dry grain / faint soft edge], clear consonants, unhurried pacing and [accent: natural Mandarin].
Rule: Keep the same vocal age, pitch center, resonance and grain across every cut; only emotional and physical intensity changes. No elderly rasp, cartoon growl, or announcer delivery.
```

---

## 五、吞鲸宝典融合实战映射表

| 场景需求 | Snail 范式对应 | 吞鲸宝典落地节点 |
| :--- | :--- | :--- |
| **开场对峙与脱衣** | 《一代宗师》雪地对白 / 《少帅》逼近对视 | 导火索 + 5图拓扑空间建立 |
| **激烈交合与换体位** | 《当古代圣贤》显式走位 + 姿势链连续位移 | 50 套体位矩阵 + 40 条连续换位配方 |
| **高潮与情绪失神** | 抽帧定格气口 (Freeze Beat) + 微距呼吸 | 生理阻断微距 + 1.5s 反应留白 |
| **台词与喘息对位** | `<d>[Chinese]...</d>` + 声学 DNA 锁死 | 三段式气口 (1.5s 动作 -> 3s 念白 -> 1.5s 收尾) |
