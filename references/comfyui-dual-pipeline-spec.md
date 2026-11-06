# 吞鲸纯血 Ref2V 生产管线规范 (Tunjing Pure Ref2V Standard)
> 继承自桌面《大人的工作台》与《大人的准则_SOP.md》
> 唯一铁律：坚决彻底摒弃首帧依赖（I2V 禁令）！全片 100% 采用全局母版 Ref2V 一采直出！

---

## 一、为什么彻底封杀 I2V 首帧垫图？(大人的准则第一条)
1. **注意力竞争导致人脸与骨骼融化**：
   在扩散模型（MiniMax H3 / DiT）的 Cross-Attention 机制中，每镜单独截取的首帧关键帧，会与全局角色母版产生剧烈的特征冲突与注意力拉扯，导致角色骨骼剧烈漂移、换脸、甚至产生多肢连体畸变；
2. **流程割裂彻底摧毁自动化**：
   单镜抽首帧迫使流水线不断中断，需要人工切软件选图、切图、改参数，成功率串联暴跌；
3. **纯血真理**：
   **全片 100% 采用【1套角色2x3母版 + 1张纯净环境底图】双锚定直通 H3 视频生成**，步骤最少、断点最少、全自动跑批量的稳定性最高！

---

## 二、纯血 Ref2V 解决复杂体位不融化的核心法则：【景别收缩与局部聚焦】

在不依赖外部垫图的前提下，跑高难度双人体位（后入、折叠深压、跨坐），必须在分镜与提示词中严格执行**三大视听法则**：

1. **核心交合冲撞强制收紧景别**：
   - 严禁在大全景或全身中景里画两人交合（全裸全身会让模型同时计算两张正脸+四只手+四条腿+骨盆结合，算力必过载融化）；
   - **取景范围强制死锁在腰胯中近景或局部微距**（`framing strictly from mid-thigh to lower ribcage, hip-height crop`）；
   - 将全部潜空间注意力 100% 独占分配给骨盆前后冲撞、臀肉受力凹陷回弹、脊柱波浪反弓！
2. **面部微表情注意力交棒**：
   - 女主角的失神翻白眼、咬唇泪痕，**不在交合大动作中强行同框计算**；
   - 顺势切给相邻的 **1.5s 生理阻断微距特写**，音画毫秒级对位，既保住了暴烈受力，又保住了神级微表情！
3. **单镜一主动作，下镜必须物理换部位与机位**：
   - 遵循工作台状态机推进（脱衣剥落 ➔ 指尖试探 ➔ 足部受力 ➔ 抓桌沿发力 ➔ 侧平视低机位主律动 ➔ 面部微距喘息 ➔ 顶点痉挛 ➔ 相拥平息），严禁单一动作机械复读。

---

## 三、工作流负向清零与【正向肯定句绝对压油法则】(吸取工作台核心教训)

在《大人的工作台》实战中已彻底查明：
> **工作流负向通道是零化的（Node 328 = ConditioningZeroOut），负向提示词完全不生效！在负向里写一万句 strictly NO oily skin 全是废话，必须靠正向肯定句压油！**

### 必须内嵌进每个镜头提示词的正向压油肯定句段落：
```text
[skin & texture]
authentic matte velvet skin finish, powdered dry texture, natural human skin with visible fine pores and subtle imperfections, soft subsurface scattering without surface reflection, non-greasy complexion.

[lighting]
heavily diffused soft ambient light through large soft diffusion source, zero hard directional light, no harsh specular rim light on cheek, perfectly soft gradient shadow falloff.

[cinematography]
35mm film still, shallow depth of field, fine authentic 35mm film grain, neutral color science, candid caught-in-the-moment intensity, photorealistic anatomy, strictly zero extra limbs.
```

---

## 四、标准 Ref2V 节点拓扑与参数死锁 (RTX 4070 Ti 12GB 基准)

```
[角色 2x3 母版 PNG] (槽位 ref_image_1) ➔ \
[纯净场景底图 PNG] (槽位 ref_image_0) ➔ ---> [MiniMax H3 ReferenceToVideo] ➔ VAE Decode ➔ 完美成片 MP4
[全英文物理动量四段式文本] ➔ /
```
- **CFG**：1.0（杜绝 Turbo 蒸馏底模与 H3 潜空间过饱和彩噪）；
- **Sampling Steps**：10 ~ 12 步；
- **Scheduler**：beta / simple；
- **画幅规格**：9:16 (864x1536 或 928x1664)；
- **物理帧长**：`length = 5 + 17 * N` (由脚本自动按秒数换算整数帧)。
