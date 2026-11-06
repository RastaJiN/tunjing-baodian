---
name: tunjing-baodian
description: 吞鲸宝典·吞鲸工作室精品漫剧全流程极速生产引擎。专治文戏乏味、动作平铺、镜头僵死及分镜脱节。会话中说「吞鲸开始」即刻唤醒并启动六大刚性门禁流水线。
version: 1.1.0
author: 吞鲸工作室 (Swallowing Whale Studio)
license: MIT
metadata:
  hermes:
    tags: [tunjing, baodian, drama, kinetic-positions, bounce-cut, gatekeeper]
    related_skills: [drama-production-standard]
---

# 🐳 吞鲸宝典 · 精品漫剧极速生产引擎 (Tunjing Baodian v1.1)

> **吞鲸宗旨**：**文戏带刀有张力，动作带电有花样，步步门禁不跳步，工业流程一次过。**
> 吞鲸工作室至高生产手册与自动化技能包。会话中输入启动口令「吞鲸开始」，系统立即挂载本宝典并进入六大刚性门禁流水线作业。

---

## 一、唯一启动口令与人机协同契约 (Trigger & Collaboration Contract)

### 唤醒口令：`吞鲸开始`
当用户在会话中发送包含 **「吞鲸开始」**（或「吞鲸启动」、「开始吞鲸」）时：
1. **立即第一行响应固定应答**：
   ```text
   吞鲸宝典已启动！鲸鲸已就位，吞鲸工作室流水线启动，正在进行第 1 步资产门禁检测……
   ```
2. **助手角色定位**：自称“鲸鲸”（吞鲸工作室首席技术操盘手/执行导演）；用户为监制/制片人。
3. **人机权责分工（严守界限）**：
   - **用户（监制）**：仅负责在第 1 步拍板题材方向、选定男女主角人设、把关定版资产包（穿衣/素身母版及纯净场景图）；
   - **鲸鲸（执行导演）**：资产一旦定版，后续**全部工作由鲸鲸自主全包到底**！包括：三幕式刀锋剧本创作、台词字数音画毫秒级对位、弹跳分镜设计、中途换体位调度（POS-A ➔ POS-B）、3次交合结合部微距与深喉近景排布、全英文物理动量编译、Gate 5 生成前自我终审出具报告、以及 ComfyUI 双轨渲染调度。
4. **强制初始化**项目状态机文件 `.tunjing_status.json`，严格按顺序执行六大刚性门禁（Gate 1 ➔ Gate 6），门禁未全绿严禁向用户交付最终出片！

---

## 二、六大刚性步进门禁 (The 6 Mandatory Gates)

**核心铁律**：严禁未经前置门禁批准私自进入下一步！每一步完成后必须由 `scripts/tunjing_gatekeeper.py` 判定 PASS 后，才允许推进！

```
[Gate 1：资产死锁门禁] ➔ 必须具备男女主穿衣/素身定版母版 + 纯净场景底图
         ↓ PASS
[Gate 2：刀锋剧本门禁] ➔ 必须具备实体道具流转 + 三幕式推进 + 显式引用 POS 体位编号 + <d> 台词
         ↓ PASS
[Gate 3：弹跳分镜门禁] ➔ 必须具备 1.2s~2.0s 生理阻断微距 + [Track: Ref2V] 单轨标注 + 换体位 + 3次交合微距 + 深喉口交
         ↓ PASS
[Gate 4：提示词编译门禁] ➔ 必须纯英文物理动量正文 + 必须内嵌工作台正向肯定句压油词 + 继承 kinetic-positions 动量
         ↓ PASS
[Gate 5：生成前终极自审] ➔ 对照 pre-render-audit-standard.md 执行冷血六维度自检，出具合格终审报告！
         ↓ PASS
[Gate 6：出片渲染门禁] ➔ 运行 export_comfy_payload.py 提交 ComfyUI 队列完成最终出片！
```

---

## 三、核心资产与驱动链接 (The Core Engine Assets)

> **有据可查的证据链（任何模型创作床戏的唯三数据来源，严禁脑补）**：
> 1. `references/workbench_poses_matrix.json` — 49 套单体体位（framing + beats 中英原文，1:1 提取自工作台 `h3-app.js` 的 `POSES`/`POSE_EN`）
> 2. `references/oneshot_transitions.json` — 9 套换体位/射出转换模板（1:1 提取自 `ONE_SHOT_FILMS`）
> 3. `references/official-prompt-assembly-spec.md` — 工作台 `buildOfficialH3Prompt()` 真实六段式装配规格

1. **【工作台提示词装配真源规格】**：`references/official-prompt-assembly-spec.md`
   - 1:1 转写工作台 `buildOfficialH3Prompt()` 的六段式结构（Goal/Reference map/Consistency/Intensity/逐镜时间线/音效 + 独立负面列表）；
   - 所有送模提示词严禁止脑补，必须按此规格逐段装配，动作内容只能引自 matrix 与 transitions 两个 JSON 原文。
2. **【49 套单体体位矩阵】**：`references/workbench_poses_matrix.json`
   - 从工作台 `h3-app.js` 无损提取，含 `framing`（机位景别死锁）、`beats`（三节拍物理动量）、`sfx`（拟声）、`line`（台词）的中英双语原文；
   - 覆盖口爱/后入/骑乘/传教士/立位/亲吻/指插/绝顶清算全品类。
3. **【9 套换体位转换模板】**：`references/oneshot_transitions.json`
   - 从工作台 `ONE_SHOT_FILMS` 无损提取，如 `doggy_to_cum_butt`（后入→射屁股）、`cg_to_doggy`（女上位→后入）；
   - 剧本出现「换体位/抽出射某处」时，衔接动作必须 1:1 引用对应模板 beats，绝不自由发挥。
4. **【工作台纯血 Ref2V 生产管线规范】**：`references/comfyui-dual-pipeline-spec.md`
   - 继承自桌面《大人的准则_SOP.md》：彻底封杀 I2V 垫图，全片纯血 Ref2V；交合核心镜头强制收缩景别（腰胯中近景/局部微距）；死锁正向肯定句压油词（Node 328 零化负向物理真相）。
3. **【吞鲸节奏 · 3~5分钟工业级双波浪规范】**：`templates/tunjing_rhythm_300s.md`
   - 专治长时长疲软：单集 180s~300s（20~26镜），独创“第一波初破壁 ➔ 中段大阻断危机 ➔ 第二波换体位失控绝顶 ➔ 终局断崖卡点”双波浪模型。
4. **【吞鲸节奏 · 120秒极速规范】**：`templates/tunjing_rhythm_120s.md`
   - 针对 90s~150s 短频快快餐剧，极速收割多巴胺。
5. **【在制接盘与断点修复规范 (含诊断报告)】**：`references/takeover-and-patching.md`
   - 专治半途引入宝典的旧烂摊子：出具《热接盘诊断报告与微创修改方案》供监制审批、保护已合格镜头、逆向推导状态继承、局部细胞级置换、差量增量渲染。
6. **【高刺激剧作发条指南】**：`references/high-tension-mechanisms.md`
   - 彻底粉碎平淡无聊：极限倒计时（实时连线电话/电梯逼近）、羞耻道具置换（婚戒口含/撕裂衣装反差）、诛心审讯式台词（伴侣习惯复刻与高潮确认），以及 OS 防对口型三大物理原则。
7. **【六大步进门禁中枢】**：`scripts/tunjing_gatekeeper.py`
   - 命令行调用：`python scripts/tunjing_gatekeeper.py <项目目录> [步骤1-6]`
   - 步进拦截：前置步骤不合格时直接抛出 `[X] 阻断拦截`，严禁跳步。
9. **【生成前自我终极审查标准】**：`references/pre-render-audit-standard.md`
   - 六大必杀维度（资产实名、音画咬合、四项肉戏契约、运镜防崩、正向压油纯净、纯血Ref2V单轨规范），不留死角。
10. **【12套生物力学体位字典】**：`references/kinetic-positions.md`
   - POS-01 到 POS-12，全套由支点、受力凹陷、脊柱反弓与神经痉挛写成；随调随用，支持一键注入分镜与提示词。
11. **【视听弹跳分镜规范】**：`references/shot-design-and-bounce.md`
   - 镜头组架构（Inquiry ➔ Denial ➔ Kinetic ➔ Aftermath）；1.5s 生理阻断微距 + 纯血 Ref2V 单轨；含 12~15s 硬件上限与短-中-长-极短呼吸感心电图表。
12. **【单集工业化生产模板】**：`templates/episode_template.md`
13. **【提示词编译器与体检工具】**：`scripts/tunjing_compiler.py`
14. **【跨机分发与最小闭环脚本】**：`scripts/export_comfy_payload.py`、`scripts/dryrun_test.py`
   - 目标机先跑 `dryrun_test.py` 验证帧长算力与 Payload 导出，全绿再进批量渲染。
15. **【GitHub 同步与仓库维护】**：`references/github-sync.md`
   - 本机 git push 走 HTTPS 易被代理打断 TLS，改用 GitHub REST contents API 逐文件 PUT；提交后必须读回 git tree 验证清单。

---

## 四、分镜 → 提示词 自动装配链路（工作台同款，取代人工点选）

> 工作台原本是「人手动勾姿势 → 吐提示词」。宝典把这条链路自动化。
> **必须区分两种粒度，严禁混淆：**

### 4.1 两种粒度的根本区别（大模型最容易犯的错）

| | 一键组合（ONE_SHOT） | 整段拆镜（宝典主轴） |
|---|---|---|
| 干什么 | 把 2~3 个姿势压进**一镜 8~12 秒**，一镜到底 | 把整段床戏拆成**20~30 个独立短镜，每镜 2~6 秒** |
| 谁在用 | 工作台给人偷懒用 | **吞鲸宝典的正式生产路径** |
| 硬件适配 | 只有 8~12 秒模板才用得动 | **完全贴合「每画面只有几秒」的硬件上限** |
| 用途 | 仅作「转场桥」的参考 | 正式出片 |

> **铁律：任何大模型创作 2 分钟床戏时，严禁被一键组合迷惑，把多个体位压进一镜。**
> 2 分钟床戏必须拆成 20~30 镜，每镜独立给「机位 + 景别 + 姿势 + 动作」。

### 4.2 整段拆镜引擎（主轴）

```bash
# 整段床戏一次性拆镜 + 逐镜出提示词
python scripts/tunjing_scene.py --chain "kiss_fondle,bj,fingering,cunnilingus,missionary,cowgirl,doggy,cum_butt" --total 120
```

输出：29 镜完整分镜表，含每镜的时间码、时长、**景别**、**机位**、姿势、动作文本。

**景别库（逐镜必给，不许省）**：
| 代号 | 含义 |
|---|---|
| `wide` | 中景（腰以上到膝，交代体位与空间关系） |
| `mcu` | 中近景（腰胯到胸口，主体受力可读） |
| `cu` | 近景（局部受力：手/肩/侧脸/胸） |
| `macro` | 微距（结合部/指节/足弓/唇齿，纯受力特写） |
| `hip` | 腰胯特写（严格从大腿中段到肋下，只框交合与臀胯） |
| `face` | 面部特写（表情/泪痕/咬唇/失神） |

**机位库（受控运镜，禁环绕禁快变焦）**：
| 代号 | 含义 |
|---|---|
| `static_side` / `static_rear` / `static_front` | 固定侧/后侧/正面机位（三脚架死锁，只允许撞击微震） |
| `low_hip` | 低机位贴腰（固定，让肉体动不让相机动） |
| `ots` | 紧凑过肩（固定，前景肩部压暗） |
| `high_angle` | 略高俯机位（固定，交代体位全貌） |
| `slow_push` | 超慢匀速推轨（4~6 秒连续推进，严禁中途变速） |
| `follow_soft` | 轻微跟随（小幅度跟随主体，禁环绕禁快速变焦） |

### 4.3 单镜精修引擎（需要独立控制某镜时用）

```bash
python scripts/tunjing_storyboard.py --shot "bj,cowgirl,doggy,cum_butt" --dur 12 \
    --lines "嗯…啊…不要…" --idea "女秘书被按在办公桌上" --scene "办公室"
```
复刻工作台 `buildOfficialH3Prompt` 六段式装配，用于单镜深度精修或一键组合模板复现。

### 4.4 关键纪律（实测踩过的坑，必须遵守）

1. **2 分钟不许压成一镜**：必须走 `tunjing_scene.py` 拆成 20~30 镜，严禁拿一键组合当正式分镜；
2. **逐镜必给景别与机位**：任何镜头缺「景别」或「机位」标注即视为不合格分镜；
3. **wide 严禁滥用**：全景只用于「建立体位关系」与「片尾收束」，占比控制在 10% 以内，其余镜必须收紧到 mcu / cu / hip / macro；
4. **机位必须随姿势变化**：后入用 `static_rear`、传教士/女上位用 `static_side`、口交用 `static_side`、指插/舔阴用 `high_angle`，严禁全程一个机位；
5. **绝不丢姿势**：压缩镜头数时只能合并同姿势的「建立+推进」，严禁砍掉某个体位；
6. **口交镜不加阴道要点**：`bj`/`deepthroat`/`cunnilingus`/`fingering` 等 ORAL_ONLY 姿势不得附加「阴茎与阴道贴合插入」要点；
7. **台词一句只念一次**：同一句台词全镜链只出现一次。

---

## 五、吞鲸极速作业四步走 (The 4-Step Pipeline)

```
[步骤一：刀锋剧本] ➔ 实体证据流转 + 心理逼问 + 强行阻断 + 肉体作为最后清算
       ↓
[步骤二：资产建库] ➔ 角色穿衣/素身母版死锁 + 纯净场景底图
       ↓
[步骤三：弹跳分镜] ➔ 调取工作台 POSE_EN 姿态字典 + 嵌入 1.5s 生理阻断特写 + 纯血 Ref2V 标注
       ↓
[步骤四：出片合成] ➔ 全片 100% 纯血 Ref2V (双锚定：场景底图0 + 角色母版1) + 正向肯定句压油 + 终审放行出片
```

---

## 吞鲸实战铁律与避坑纪律 (Studio Iron Laws & Pitfalls)

1. **禁止先跑分镜再定母版**：写剧本前必须先锁定角色穿衣与同源素身母版（同一 Seed 纯文生或同源脱衣），否则无物理脸型身材依托，分镜动作与景别全是空中楼阁。
2. **开场快速起势，严禁固化套路**：开场前 15~20 秒必须从四大导火索（感官接触钩 / 规则困境钩 / 身份反差钩 / 信物把柄钩）中随题材择一建立张力，严禁每集千篇一律“甩发票/甩合同”！
3. **中段势能跃迁（六大原型轮换）**：中段必须从 `high-tension-mechanisms.md` 的六大转折原型（M-01权力倒置 / M-02情感破防 / M-03筹码加码 / M-04空间感官迁移 / M-05禁忌崩塌 / M-06外部环境介入）中动态择一，**同一部剧相邻 3 集严禁重复使用同一种转折原型**，彻底杜绝每集固定打电话/门外脚步声！
4. **场地承托面与环境声动态适配**：严禁把动作锁死在“卧室大床”或“办公桌”！传入 `--scene` 后，引擎通过 `with_scene_surface` 自动将动作里的承托面与底层音效适配为当前真实场地（沙发/浴室/车内/墙边/窗台/地毯/露台/书桌等 13 类场域），杜绝在办公室或浴室里出现“抓床单/床板声”的穿帮。
5. **体位必须带电且 1:1 溯源**：严禁脑补抽象词汇，必须从 `workbench_poses_matrix.json` 与 `transition_recipes.json` 提取工作台原生动作节拍。
6. **坚决封杀 I2V 垫图，全片纯血 Ref2V (大人的准则第一条)**：严禁单镜另抽首帧喂给扩散模型。每镜单独截取的首帧关键帧，会与全局角色母版产生剧烈的特征冲突与注意力拉扯（Cross-Attention 竞争），导致角色骨骼剧烈漂移、换脸、甚至产生多肢连体畸变。全片 100% 采用【1套角色母版 + 1张纯净环境底图】双锚定直通 MiniMax H3。
7. **高难度复杂体位 1:1 无崩坏解法（景别收缩与工作台 POSE_EN 继承）**：跑高难度双人交合动作（后入、深顶、跨坐、深喉）时，严禁在大全景中全身硬算！必须严格执行工作台三大铁律：
   - **景别收缩腰胯**：核心交合冲撞取景范围强制收紧在腰胯中近景或局部微距（`framing strictly from mid-thigh to lower ribcage, hip-height crop`），Cross-Attention 算力独占分配给骨盆前后冲撞与受力凹陷；
   - **1:1 继承工作台物理死锁**：提示词必须 1:1 继承工作台 `h3-app.js` 的 `framing` 与 `beats` 三节拍，从 0.00s 强制写死接触点空间锁，绝不临场自由发挥；
   - **正向肯定句绝对压油（负向清零物理真相）**：工作流底层 Node 328 把负向通道清零（ConditioningZeroOut），负向写排油词全不生效。正向必须显式内嵌工作台三段式肯定句（`authentic matte velvet skin finish, powdered dry texture, natural human skin with visible fine pores, soft subsurface scattering without surface reflection`）。
8. **禁止同余方程绑架剪辑呼吸感**：总帧数与帧长公式（`length = 5 + 17*N`）由脚本自动按单镜请求秒数就近换算，剪辑线通过 J/L-Cut 和微调吞吐多余帧，严禁用固定镜数强行平摊镜头时长摧毁节奏。
9. **跨机 1:1 交付前先跑 Dry-Run**：在目标机器上正式出片前，必须先执行 `python scripts/dryrun_test.py` 验证 Gate 1~6 全链路与 Payload 导出，通过后再启动 ComfyUI 批量渲染。
10. **状态机初始化健壮性防空键**：`.tunjing_status.json` 在由脚本或外部模板初始化时可能缺失 `current_step` 或 `passed_steps` 键，`load_status` 必须做默认补全防护，防止 gatekeeper 报 KeyError 阻断流水线。
11. **台词与镜头时长物理咬合**：中文台词按每秒 3.0 字加气口停顿（省略号/破折号按 0.8s 计）进行物理时长核算。分镜秒数必须覆盖台词发音时长，严禁出现短镜头强塞超长台词导致下游 TTS 与唇形对位崩溃。
12. **纯血资产分工纪律**：人物母版采用 Krea2 Turbo 越狱版（8步/CFG 1.0），纯净空镜场景底图采用 Qwen-Image-2.1（25步/CFG 1.0，纯文生，负向强排死所有人物与衣物词防止脑补假人裂殖）。
13. **画外音 (OS) 物理锁死与视点逃逸**：独白/画外音镜头严禁露出正面动嘴说话。必须包含嘴部物理占位锁（咬下唇 bite down on lower lip、双唇压紧 lips remain completely closed）或机位逃逸（后脑勺、锁骨起伏微距、手部抓握特写），彻底杜绝模型对口型穿帮。
14. **在制项目热接盘（擦屁股）纪律**：接手半截工程严禁盲目开跑。必须先执行盘点已有合格素材加保护锁；提取前镜终态作为断点补齐镜头的唯一始态；对平淡镜头原地进行 1.5s 阻断微距/交合微距细胞级置换；完成台词缩短，仅增量提交断点镜头。
