# 吞鲸视听弹跳分镜规范 (Tunjing Bounce Shot Design)
> 吞鲸工作室专属导演指南 · 彻底粉碎平铺直叙与死板平摊时长，把短剧视听呼吸感做到院线级拉扯。

---

## 一、核心视听语法：弹跳剪辑 (The Bounce Cut)

### 1. 为什么你的分镜会平？
平铺直叙的分镜永远是：`中景(4s) ➔ 中景(4s) ➔ 中景(4s)`，观众看 15 秒就想快进！

### 2. 弹跳三镜序列公式 (中 ➔ 1.5s 极近微距 ➔ 弹回中景)
在任何身体冲撞或权力交锋的高潮点，镜头必须像弹簧一样瞬间扎进微观受力，然后立刻回弹：
```
[Shot A · 中景/全身] 动作发生：男主一把将女主按在办公桌上，猛力贯入 (3.5s)
         ↓ (切点瞬间：注意力交棒)
[Shot B · 1.5s 生理阻断微距] 受力爆发：女主指节在桌沿瞬间抓到泛白 / 脚趾死抠床单 / 咬破下唇的血珠 (1.5s)
         ↓ (切点瞬间：反应回弹)
[Shot C · 中景/反打] 心理余波：男主居高临下的冷酷眼神，女方面颊潮红大汗淋漓 (3.0s)
```
**凡是核心动作，必须插入至少一个 1.2s ~ 2.0s 的生理阻断微距！这是带电感的根源！**

---

## 二、镜头组 (Shot Groups) 结构规范

一集 300 秒（约 20~28 个镜头）按四大镜头组组织，严禁单镜孤立平铺：

### 组 1: 【证据刺探组 (Inquiry Group)】(约 00:00 ~ 01:30)
- **职责**：实物道具流转、秘密剥皮、建立密闭空间压迫。
- **镜数**：5 ~ 7 镜。
- **节奏**：对峙推进，景别由全景关系逐步收紧到过肩与下颌特写。

### 组 2: 【阻断与撕扯组 (Denial & Tear Group)】(约 01:30 ~ 02:45)
- **职责**：突发阻断（门外脚步/电话）、强制剥离衣物、心理最后防线崩塌。
- **镜数**：4 ~ 6 镜。
- **节奏**：快慢错落，大动作突进（2.0s）配以心跳骤停的凝固特写（1.8s）。

### 组 3: 【体位清算组 (Kinetic Climax Group)】(约 02:45 ~ 04:30)
- **职责**：调用 2 套 POS 姿态，暴力冲撞与深度贯入，生理绝顶。
- **镜数**：8 ~ 12 镜。
- **节奏**：长短交替。交合长发力镜头（6.0 ~ 7.5s）+ 弹跳生理微距（1.5s）。

### 组 4: 【余温与终局钩子组 (Aftermath & Hook Group)】(约 04:30 ~ 05:00)
- **职责**：汗水滑落、四肢脱力、扔下一句不可违抗的下一集命令。
- **镜数**：3 ~ 4 镜。
- **节奏**：慢速平息，定格在关键道具或未挂断的电话上。

---

## 三、双轨管线标注 (Pipeline Routing)

分镜表中每一镜必须显式标注执行轨道，提示下游生成管线：
- `[Track: Ref2V]`：常规文戏对话、单人走位、纯面部特写（走纯血 Ref2V 提示词直接生成，省时高效）；
- `[Track: I2V_Pose]`：高难度多人肢体缠绕、复杂交合体位（POS-01 ~ POS-11）、特殊角度（必须先出姿态首帧关键帧，再送 I2V 启动动态，防肢体融化）。

---

## 四、高能戏四套“防穿模防换脸”电影级运镜法则 (Bulletproof Camera Grammar)

在高能戏份中，严禁大范围环绕 (Orbit)、剧烈手持晃动或大推拉，这会导致模型换脸、算力分散和肢体融化。必须严格执行以下四种受控运镜：

### 1. 核心交合冲撞：【低机位死锁 (Static Side Lock)】
- **场景**：大开大合的深顶、后入、律动。
- **法则**：**机位完全静止，让肉体动，不让相机动！** 所有 Cross-Attention 算力独占分配给受力形变与肌肉震颤。
- **控机词**：`The camera is locked at a stationary side-angle at hip height, strictly NO camera movement, capturing continuous physical kinetic impacts.`

### 2. 心理拉扯与逼近：【五秒超慢匀速推轨 (Slow Linear Push In)】
- **场景**：由交合部向女方面部、泪痕、咬唇表情交棒。
- **法则**：极其平滑匀速推进，耗时 4~6 秒，严禁中途变速。
- **控机词**：`A slow, steady Push In moving continuously across 5.0 seconds from the waistline toward her flushed cheek, without acceleration or tilt.`

### 3. 1.5s 生理阻断特写：【纯微距极近死锁 (Macro Static)】
- **场景**：指节抓白床单、脚趾神经性反弓、喉结吞吐拉丝。
- **法则**：纯定焦点微距，绝对静止，毫秒级交接。
- **控机词**：`Stationary extreme close-up macro, razor-sharp focus on white-knuckled fingers twisting into the silk sheet, zero panning.`

### 4. 禁忌窥视与支配感：【紧凑过肩/门框遮挡 (Tight OTS / Framing)】
- **场景**：下位者被压制、办公桌沿、门后偷听。
- **法则**：借男主宽厚肩膀或门框前景压迫，形成逼仄景深，杜绝大平光穿帮。
- **控机词**：`Tight Over-The-Shoulder framing from behind his shoulder, foreground shoulder soft and dark, holding static on her pinned expression.`
