# 场景实体三维坐标提示词规范 (Scene Spatial Entity & Material Architecture)

本规范作为吞鲸宝典针对电影级场景参考图与环境提示词的权威生产标准，彻底摒弃空洞形容词堆砌，采用三维物理实体坐标法与单向主光学系统，确保环境在镜头切换中零漂移、家具零吃掉、光影零闪烁。

---

## 一、场景提示词核心五段式骨架 (The 5-Layer Spatial Template)

严禁撰写“温馨房间、奢华大气”等抽象形容词。场景描述必须按建筑置景图规范分层编译：

```text
[Layer 1: 空间母体定性]
<Subject X> is the [真实场景定义，如：lived-in master bedroom / minimalist tea room]:
[Layer 2: 空间主轴与核心承托面]
a [尺寸与形态，如：low solid dark-walnut platform bed] positioned [绝对坐标，如：centrally against the rear wall], with [物理材质与痕迹，如：wrinkled charcoal-silk sheets and two compressed velvet pillows];
[Layer 3: 屏幕左中右道具地标坐标系]
at room-left, [地标道具，如：floor-to-ceiling balcony glass doors with sheer linen drapes]; 
at room-right, [地标道具，如：a low freestanding two-drawer nightstand supporting an amber glass decanter and a muted stone bowl]; 
at center, [视线汇聚道具，如：a low woven floor mat];
[Layer 4: 建筑材质与微观质感]
[墙面材质，如：matte dark-teal plaster walls absorbing surface glare], [地面材质，如：unpolished dark timber floorboards with visible grain];
[Layer 5: 单一主光源光学系统与显式排除项]
the sole primary illumination is [光源定义与来向，如：warm directional low-angle window light from screen-right casting deep elongated side shadows]; strictly no modern plastic fixtures, no ceiling chandeliers, perfectly preserved spatial geometry across cuts.
```

---

## 二、场景三维坐标三大铁律 (Three Spatial Iron Laws)

### 1. 绝对地标死锁律 (Landmark Coordinate Locking)
- 房间内必须定义 3~4 个独立道具地标（如：左侧落地窗、右侧三抽屉矮柜、中央矮几）；
- 必须明确声明独立性（例如：`This nightstand is completely separate from the wardrobe console`），防止 AI 视频模型在运镜时把两个家具融合成一个巨型长柜。

### 2. 物理材质与反光属性直描律 (Material & Texture Specification)
- 严禁写 `beautiful walls`，必须写出光学反应：
  - `teal-gray plaster`（吸收高光的哑光蓝灰抹灰墙面）；
  - `luminous white stone with continuous gray mineral veins`（带连续矿物纹理的微光白石）；
  - `wrinkled silk with radial tension folds`（受力拉扯出放射状褶皱的真丝）。

### 3. 单向主光学系统律 (Directional Light System)
- 全场景只允许确立 **唯一主光源入口**（如：`screen-right directional warm window light`）；
- 严禁全景无影灯或随镜头漂移的环形光源。所有特写、正反打镜头的阴影走向必须严格服从该主窗口方向。
