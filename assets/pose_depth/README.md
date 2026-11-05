# 吞鲸体位深度图资产索引 (Pose Depth Asset Index)

> 本目录存放 12 套核心体位的**纯灰度深度图**（Depth Map），供 ComfyUI ControlNet Depth 分支锁定三维骨骼与肢体接触几何。
> 全部为侧视（Side Angle）3:4 竖版，白色越亮表示越近。

## 使用规范

1. **轨道归属**：仅用于 `[Track: I2V_Pose]` 高危复杂体位镜头的**第一阶 T2I 静态关键帧生成**；
2. **接入方式**：`LoadImage` 载入 → `ControlNet Depth` 控制网 → 绑定 Qwen 2.1 生成器；
3. **禁止事项**：深度图**不得**直接送进视频模型槽位，只走生图阶段的几何控制；
4. **身份来源**：深度图只提供姿态几何，脸与身体仍由 2×3 母版决定。

## 体位对照表

| 文件 | 体位名称（中） | 体位名称（英） | 几何特征 |
|---|---|---|---|
| `POS-01_depth.png` | 站立前屈后入（可贴桌/贴墙） | Standing Bent-Over Rear Entry | 女方前屈撑扶，男方站立于身后，一手按腰胯 |
| `POS-02_depth.png` | 双脚架肩·折叠深压 | Folded Missionary (Ankles on Shoulders) | 女方仰躺，双腿架于男方双肩，男方跪压覆盖 |
| `POS-03_depth.png` | 反向跨坐·背对骑乘 | Reverse Cowgirl | 女方背对男方坐于其腿上，背贴男方胸口 |
| `POS-04_depth.png` | 站立相拥·单腿抬抱 | Standing Embrace with One Leg Lifted | 面对面站立，女方单腿抬扣男方腰际 |
| `POS-05_depth.png` | 双膝抱胸·极限折叠 | Full Fold (Knees to Chest) | 女方仰躺，双膝折压至胸口，男方跪姿施压 |
| `POS-06_depth.png` | 四足跪姿·后方跪入 | All-Fours Rear Entry | 女方四肢撑地，男方跪姿自后方进入 |
| `POS-07_depth.png` | 侧卧侧位·单腿抬肩 | Side Position (Leg to Shoulder) | 女方侧躺，一腿抬向男方肩部 |
| `POS-08_depth.png` | 站立前伸·腰被支撑 | Standing Supported from Behind | 站立，女方手臂前伸上举，男方自后托腰 |
| `POS-09_depth.png` | 正面跨坐·面对面骑乘 | Front Cowgirl (Face-to-Face) | 女方正面跨坐于仰躺的男方身上 |
| `POS-10_depth.png` | 膝抵肩·足踝被抓 | Knees to Shoulders (Ankles Held) | 女方仰躺，双膝压至肩部，脚踝被男方握住 |
| `POS-11_depth.png` | 站立手腕被压过头 | Standing Wrist Pinned Overhead | 站立，女方双手腕被举过头顶压制 |
| `POS-12_depth.png` | 站立相拥·腿缠绕 | Standing Embrace with Leg Wrapped | 站立相拥，女方一腿盘扣于男方腰侧 |

## 与分镜的对应关系

写分镜时，凡是标注 `[Track: I2V_Pose]` 且指定了 POS 编号的镜头，必须同编号引用本目录下的深度图：

```markdown
### SHOT-04 [Track: I2V_Pose]
- 时长: 6.5s (158 帧)
- 关联体位: POS-01 / Depth: assets/pose_depth/POS-01_depth.png
- T2I 关键帧生图词: 见 dual-prompt-protocol.md 七支柱结构
- I2V 动力学生成词: 见 kinetic-positions.md 的 POS-01 Prompt Block
```
