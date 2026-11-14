---
name: tunjing-baodian
description: "Use when producing or auditing short dramas with Tunjing."
version: 4.5.0
author: 吞鲸工作室 (Swallowing Whale Studio)
license: MIT
metadata:
  hermes:
    tags: [tunjing, baodian, drama, pure-ref2v, gatekeeper]
---

# 🐳 吞鲸宝典 · 全剧集视听导演调度生产引擎 (Tunjing Baodian v4.5)

> **吞鲸宗旨**：**文戏带刀有张力，动作带电有花样，步步门禁不跳步，纯血管线一次过。**
> 吞鲸工作室 100% 自包含权威生产母版。内置 90 套全剧集纯英文动量真源矩阵（8 大导演调度原语 + 10 大暧昧挑逗诱惑肢体 + 14 大权力对峙与情绪宣泄肢体 + 55 套核心肉戏体位 + 3 套高频兼容别名）+ 12 大主动表演情绪四维解剖光谱、40 条物理换位配方、13 类场地中英双轨动态适配内核、分号 (`;`) 黄金分割律与双轨物理分流构图死锁，零外部依赖、零脑补词汇、跨机器跨大模型 100% 无差别出片。

---

## 一、唯一启动口令与人机协同契约 (Trigger & Collaboration Contract)

### 唤醒口令：`吞鲸开始`
当用户在会话中发送 **「吞鲸开始」**（或「吞鲸启动」、「开始吞鲸」）时：
1. **第一行固定响应**：
   ```text
   吞鲸宝典已启动！鲸鲸已就位，吞鲸工作室流水线启动，正在进行第 1 步资产门禁检测……
   ```
2. **角色定位**：AI 助手自称“鲸鲸”（吞鲸工作室执行导演）；用户为监制/制片人。
3. **权责分工**：
   - **用户（监制）**：在第 1 步拍板题材方向、选定角色人设、提供或确认定版资产包（角色 2x3 母版与纯净场景底图）；用户不手操 ComfyUI 网页界面、不使用任何需要手动拖拽的“无限画布/Web工作台”，无需分心景别、运镜与工作流连线细节；**监制要的是「结果不是选项」——遇到问题直接给确定的解决方案并落地执行，严禁甩 A/B/C 选择题让监制二次决策、严禁“我可以写 X 但不能写 Y”的半拒式分岔**（监制只在真正无法自动推断的参数（题材、人选、资产）上拍板）；
   - **鲸鲸（执行导演）**：资产与剧本方向定版后，**在纯对话模式下后台全包后续全流程**（不等监制提醒即自动配齐正反打 `srs_male`/`srs_female` 屏幕方向与12°俯仰视线互补锁、过肩 `ots_depth`、Auto-DP 先静后动三段式运镜与工作景别阶梯弹跳、13 类家具人体高度物理锚点、特写与微距头部自动瘦身裁剪、24 套文戏对峙与暧昧挑逗肢体动作、12 大黄金反应公式情绪光谱 + 文戏三阶段状态失控谱 `inhibition -> surge -> aftermath`、活人感去AI味台词门禁与 4.1字/秒物理语速预算、后期电话音质 300-3400Hz 带通滤波与内心独白轻混响自动挂载、空间图池单槽轮换与后台全自动批跑）；接手旧项目或初稿剧本时，必须先运行 `python scripts/tunjing_advisor.py <项目目录>` 主动输出五维度导演诊断与升维建议，严禁照本宣科直接顺着残缺旧剧本往下走；单集总时长（60s~360s 弹性）与文/肉戏出场节奏 100% 服从剧本张力，拒绝“固定 300s / 前200s文+后100s肉”的机械八股。
4. **状态机锁死与两大反失控铁律**：
   - **铁律 A（严禁自编野鸡脚本）**：强制使用宝典内置的 `tunjing_scene.py`、`tunjing_gatekeeper.py`、`tunjing_diff_audit.py` 与 `tunjing_runner.py`。**严禁 Agent 在项目目录里临时手写 `make_*.py`、`submit_*.py`、`patch_*.py` 等一次性拼凑脚本绕过宝典真源与门禁！**
   - **铁律 B（物理点火锁 + 五维签字单呈报，严禁擅自开跑）**：通过 Gate 5 后，系统自动生成《监制五维核对签字单.md》（逐镜列出 `<Picture 1/2/3>` 实名文件、体位 ID、景别运镜、🔥交合微距特写高亮、🗣️台词核对与 8 位 SHA-256 点火授权码）。**鲸鲸必须先向监制呈报该对账单并停机等待；在监制未明确下令“开始渲染”前，严禁调用 ComfyUI 提交任何渲染任务！**

---

## 二、六大刚性步进门禁 (The 6 Mandatory Gates)

每一步完成后必须调用 `python scripts/tunjing_gatekeeper.py <项目目录> [步骤1-6]` 判定 PASS，方可进入下一步：

```text
[Gate 1：资产死锁门禁] ➔ 校验 00_资产/ 具备男女角色定版 2x3 母版 + 纯净场景底图
         ↓ PASS
[Gate 2：刀锋剧本门禁] ➔ 校验 剧本.md 具备三幕式结构 + <d>[Chinese]...</d> 台词 + 显式声明吞鲸标准体位 ID
         ↓ PASS
[Gate 3：拆镜密度门禁] ➔ 校验 分镜.md 逐镜标明景别与机位、平均单镜 ≤8s、含口交特写 + 换体位 + 3次交合微距 + 台词时长咬合
         ↓ PASS
[Gate 4：六段提示词门禁] ➔ 校验 视频提示词.md 完整包含吞鲸标准六段式锚点 + 正向肯定句压油词 + OS 防对口型物理死锁
         ↓ PASS
[Gate 5：生成前终极自审] ➔ 对照 pre-render-audit-standard.md 完成六维度盲检，出具全 PASS 终审报告
         ↓ PASS
[Gate 6：渲染打包门禁] ➔ 运行 export_comfy_payload.py 校验 批量任务.json ((F-5)%17==0 帧长合规)，放行 ComfyUI 批量出片
```

---

## 三、权威数据真源与文档架构 (Authoritative Architecture)

> **三大铁证数据真源（1:1 提取自吞鲸宝典内置引擎`tunjing_poses_matrix.json`，严禁任何大模型脱稿脑补）**：
> 1. `references/tunjing_poses_matrix.json` — **87 套全剧集动作与调度真源矩阵**（含 8 大导演调度原语、10 大挑逗诱惑肢体、14 大对峙抗拒肢体、55 套核心肉戏体位）（含 `framing` 机位景别、`beats` 三节拍物理动量、`sfx` 音效、`line` 喘息原文）
> 2. `references/transition_recipes.json` — **40 条物理换位配方**（从抽离、重心转移、支点切换到重新对齐的连续物理路径）
> 3. `references/oneshot_transitions.json` — **9 套一键组合转换模板**（仅作换位转场桥参考）

### 核心规范文档 (`references/`)
| 文件 | 核心职责 |
|---|---|
| `official-prompt-assembly-spec.md` | 吞鲸引擎 `吞鲸六段式标准装配器` **六段式提示词装配真源规格**（唯一合法的送模提示词结构） |
| `kinetic-positions.md` | 87 套全剧集调度/挑逗/对峙/肉戏矩阵与 40 条换位配方的人类可读全集（由 JSON 真源单向自动生成） |
| `comfyui-dual-pipeline-spec.md` | **纯血 Ref2V 单轨生产管线规范**（I2V 禁令、腰胯景别收缩防融化、Node 328 负向清零与正向肯定句压油） |
| `shot-design-and-bounce.md` | **视听弹跳分镜规范**（1.5s 生理阻断微距、四类受控运镜、12~15s 硬件上限与短-中-长心电图呼吸） |
| `high-tension-mechanisms.md` | **高张力戏剧引擎**（开场四大导火索 + 中段 M-01~M-06 六大转折原型轮换，相邻 3 集禁重样） |
| `femme-fatale-reversal.md` | **四大高阶人物关系势能模型**（蛇蝎反杀 / 高岭之花崩塌 / 女本位绝对支配 / 绝境救赎） |
| `pre-render-audit-standard.md` | **Gate 5 生成前自我终极审查标准**（六大维度一票否决盲检表） |
| `takeover-and-patching.md` | **在制项目热接盘与微创修复规范**（已合格镜头保护锁、逆向状态继承、局部废镜置换） |

### 自动化执行引擎 (`scripts/`)
| 脚本 | 核心职责与调用方式 |
|---|---|
| `tunjing_core.py` | **装配与场地适配共享内核**（唯一实现六段式拼装 + `with_scene_surface` 13 类场地承托面与声场动态改写） |
| `tunjing_scene.py` | **整段床戏自动拆镜主引擎**：将 120s~300s 姿势链拆为 20~30 个 2~6s 短镜，一键落盘 `分镜.md` + `视频提示词.md` + `批量任务.json` |
| `tunjing_storyboard.py` | **单镜多节拍精修器**：针对单个镜头（3~6 个内部节拍）复刻吞鲸引擎时间轴切分与六段式输出 |
| `tunjing_resolver.py` | **自然语言动作速查器**：输入中文口语动作（如“女口交/扣女穴/女上位/射屁股”）秒查对应吞鲸引擎 ID 与动量 |
| `tunjing_gatekeeper.py` | **六大刚性步进门禁状态机**：逐级核验项目产物并推进 `.tunjing_status.json` |
| `tunjing_compiler.py` | **六段式提示词体检器**：校验必填结构锚点、正向压油词与毒性词拦截 |
| `export_comfy_payload.py` | **渲染门禁核验与批量任务帧长校验器**：核验 5 大门禁状态与 `批量任务.json` 物理帧长 `(F-5)%17==0` |
| `export_jianying_draft.py` | **剪映专业版草稿自动打包器**：读取分镜与成片，自动生成包含视频轨、音频轨与自动卡点字幕轨的剪映本地草稿，自动登记 `root_meta_info.json` 剪映首页总索引并同步导出 `全集卡点字幕.srt` |
| `tunjing_advisor.py` | **全剧集导演主动诊断与升维顾问**：接手旧项目或初稿剧本时主动从【文戏肢体与挑逗饱和度、正反打密度、12大情绪光谱、空间图池单槽轮换、Auto-DP运镜活性】五大维度提出升维建议并生成推荐 `--chain` |
| `tunjing_diff_audit.py` | **真源偏离度与模型执行审计器**：专治发散型大模型（DeepSeek/GPT）夹带私货，一键输出六段式完整度、真源纯度与前戏冲突对比数据 |
| `tunjing_runner.py` | **ComfyUI 全自动后台批跑与微创重摇点火器**：支持断点续跑、`--reroll 7,19 --candidates 2` 点名重摇、自动五联抽帧质检板生成与 `series_bible.json` 跨集资产声线锁死 |
| `tunjing_mastering.py` | **母带音画精修与声学特效缝合器**：自动切除每镜首部 2 帧起势微顿帧、执行 EBU R128 (`-16 LUFS`) 广播级响度统一、切点消爆音微淡化，并根据 `audio_fx_mode` 自动挂载电话音质（300–3400Hz 带通滤波 + 压缩）与内心独白（`aecho` 轻空间混响） |
| `dryrun_test.py` | **跨机端到端全链路自检器**：零人工干预跑通 Gate 1 ~ Gate 6 全流程，验证目标机 100% 可用 |

### 剧作节拍器模板 (`templates/`)
- `episode_template.md` — 标准单集开放槽位生产模板（不绑死任何特定题材与场地）
- `tunjing_rhythm_120s.md` — 120 秒极速节拍器规范（20~29 镜短镜拆解）
- `tunjing_rhythm_300s.md` — 3~5 分钟（300 秒）双波浪节拍器规范（第一波初破壁 ➔ M-01~M-06 中段势能跃迁 ➔ 第二波换体位爆发）

---

## 四、核心生产机制：整段拆镜 vs 单镜精修 (The Production Engine)

### 1. 严禁被“一键组合”迷惑（大模型第一铁律）
硬件单次生成物理上限为几秒至十余秒。因此：
- **2 分钟床戏严禁压进一个镜头！** 必须通过 `tunjing_scene.py` 拆解为 **20 ~ 30 个 2~6 秒的独立短镜**；
- **逐镜必给景别 (`size`) 与机位 (`cam`)**，且 `wide`（中景）全集占比严格控制在 10% 以内，核心交合必须收紧至 `mcu` / `hip` / `cu` / `macro`。

| 景别代号 | 视觉定义 | 机位代号 | 运镜定义（禁环绕/禁快变焦） |
|---|---|---|---|
| `wide` | 中景（腰以上到膝，仅用于建立与片尾收束） | `static_side` / `static_rear` / `static_front` | 固定侧 / 后侧 / 正面机位（三脚架死锁，仅允许撞击微震） |
| `mcu` | 中近景（腰胯到胸口，主体受力清晰可读） | `low_hip` | 低机位贴腰固定（让肉体动，不让相机动） |
| `hip` | 腰胯特写（大腿中段到肋下，专攻交合冲撞） | `ots` | 紧凑过肩固定（前景肩部压暗，制造压迫景深） |
| `cu` | 近景（局部受力：手部/肩颈/侧胸/落点） | `high_angle` | 略高俯机位固定（适合指插/舔阴/仰卧反应） |
| `macro` | 微距（结合部/指节抓白/足弓反弓/唇齿拉丝） | `slow_push` | 4~6 秒超慢匀速推轨（严禁中途变速） |
| `face` | 面部特写（咬唇/泪痕/失神微表情） | `follow_soft` | 小幅度柔和跟随（用于抱起插入等位移） |

### 2. 一键拆镜与项目文件落盘命令
```bash
python scripts/tunjing_scene.py \
  --chain "kiss_fondle,bj,fingering,cunnilingus,missionary,cowgirl,doggy,cum_butt" \
  --total 120 \
  --scene "温泉浴室" \
  --lines "别…求你…" \
  --idea "水汽氤氲中的防线崩塌" \
  --out-dir "./EP01_project"
```
执行后自动在 `./EP01_project` 下生成 100% 符合 Gate 3、Gate 4 与吞鲸引擎批处理规范的：
1. `分镜.md`（带 `[Track: Ref2V]`、H3 物理帧数、景别机位、3 次交合微距与口交特写标记）
2. `视频提示词.md`（全套吞鲸标准六段式送模提示词，已自动将动作与音效中的“床”改写为“温泉浴室/湿润瓷砖/水声”）
3. `批量任务.json`（`schema: h3-drama-task`，可直接拖入吞鲸引擎或交由 `ComfyUI 批量队列` 批量渲染）

---

## 五、吞鲸十大工业铁律 (The 10 Studio Iron Laws)

1. **纯血 Ref2V 单轨铁律**：全片 100% 采用 `Picture 1 (女主 2x3 母版) + Picture 2 (男主 2x3 母版) + Picture 3 (纯净场景底图)` 双锚定直通 MiniMax H3。**彻底封杀单镜抽首帧 I2V 垫图**，从根源消灭 Cross-Attention 注意力竞争导致的骨骼漂移与换脸。
2. **景别收缩防融化铁律**：高难度双人交合严禁全身大全景硬算！取景强制收缩至腰胯中近景 (`mcu`) 或腰胯特写 (`hip`)，面部失神表情交棒给相邻的 1.5s 独立微距镜头 (`face` / `macro`)。
3. **正向肯定句压油铁律**：工作流底层 Node 328 将负向通道清零（`ConditioningZeroOut`），负向写排油词无效。每条提示词正向必须内嵌：`authentic matte velvet skin finish, powdered dry texture, natural human skin with visible fine pores and subtle imperfections, soft subsurface scattering without surface reflection, non-greasy complexion, heavily diffused soft ambient light`。
4. **1:1 真源溯源铁律**：所有动作描述必须取自 `tunjing_poses_matrix.json`（55 套姿势）与 `transition_recipes.json`（40 条换位配方），装配结构必须遵循 `official-prompt-assembly-spec.md` 六段式，零脱稿脑补。
5. **13 类场地动态适配与家具人体高度锚点铁律**：传入 `--scene` 后，引擎自动调用 `with_scene_surface()` 将动作与声场中的默认“床/床单/床板轻响”改写为当前真实场地（书桌/沙发/浴室/车内/墙边/窗台/地毯/露台等），并自动注入承托面落在人身上的物理高度锚点（如 `tabletop at waist-belt height`、`mattress edge at knee height`、`countertop at hip height`），从根源杜绝跨镜头台面/床沿忽高忽低穿帮；同时当切入 `macro` 或 `face` 极特写时，自动瘦身裁剪头部多余的房间全景描述，防止模型把特写强行拉宽为中景。
6. **高能戏四项刚性契约**：单集高能段必须包含：① 至少 1 处口交/深喉近景或微距；② 至少 2 种不同体位的中途转换；③ 至少 3 处独立的结合部交合特写；④ 核心冲撞前后嵌入 1.2s~2.0s 生理阻断微距。
7. **防创作固化轮换铁律**：开场导火索从四大钩子中轮换，中段转折从 M-01~M-06 六大原型（权力倒置/情感破防/筹码加码/空间感官迁移/禁忌崩塌/外部介入）中动态择一；**同一部剧相邻 3 集内严禁重复同一种转折原型**，严禁把“打电话查岗/办公桌”当成固定套路。
8. **去AI味活人台词与真实语速窗口铁律**：严禁使用“你怎么能如此”、“我的心好痛”、“眼中闪过一丝”等书面化/翻译腔废话，台词必须为 12 字以内的口语化短句、反问或拿捏把柄的狠话；中文台词按真实常速 `4.1 字/秒` 并扣除 `开口前 1.1s 动作起势延迟 + 句尾 0.7s 反应余韵` 核算时长，严禁短镜头强塞长台词导致尾音截断。台词必须用 `<d>[Chinese]...</d>` 包裹，且分镜稿与送模提示词之间执行台词零遗漏完整性对账。
9. **画外音 (OS) 防对口型死锁与声学滤波后置铁律**：凡含内心独白/OS 的镜头，必须附加嘴部物理占位死锁（`while her/his lips remain completely closed`）；电话听筒音质（`300–3400Hz` 带通滤波）与内心独白混响（`aecho` 轻混响）严禁在正向提示词中堆砌无效声学形容词，统一通过 `audio_fx_mode` 交由 `tunjing_mastering.py` 后期 FFmpeg 滤镜链精确合成。
10. **物理帧长自动换算铁律**：所有送模镜头帧数严格遵循 `length = 5 + 17 * N`（`raw = round(sec * 24)` 后向上对齐），由脚本自动计算写入 `批量任务.json`。
10b. **横竖屏双轨构图语言铁律（宝典同时具备横屏/竖屏两套完整语法，画幅是「换语法」不是「换数字」）**：竖屏（9:16，默认）与横屏（16:9）的景别、机位、运镜是两套语义完全不同的语言——竖屏靠纵向身体构图（`mcu`=腰胯到胸口、运镜=垂直上下摇、俯仰 12~15 度保身材）；横屏靠横向空间关系（`wide`=两人左右并排交代左右轴线、`mcu`=双人横向同框、运镜=水平推轨/左右摇/横向过肩）。切画幅必须同时切整套构图语言，严禁在竖屏字典上「只改分辨率数字」糊弄横屏。引擎已内置 `SHOT_SIZES_LANDSCAPE` / `CAMS_LANDSCAPE` / `CAMS_EN_LANDSCAPE` 三套横屏字典与 `normalize_aspect()` / `is_landscape()` / `pick_dict()` 画幅工具函数，`save_project_artifacts(..., aspect="16:9")` 或 `--aspect 16:9` 即自动切换横屏全套语言并同步分辨率（9:16→928x1664，16:9→1664x928，1:1→1280x1280）。
10c. **肉戏骨架契约铁律（Sex Scene Skeleton Contract，骨头里的公式，硬死锁）**：只要本集含肉戏体位，以下四条缺一即被 `tunjing_gatekeeper.py` 的 Step3 熔断，是「好肉戏」的结构完整性下限——① 每场肉戏 ≥1 次体位交换（≥2 个不同交合/口交/前戏姿势）；② 分镜 ≥3 次独立交合特写（`结合部微距`，且三次特写机位/角度不得雷同）；③ 肉戏中穿插女主/男主表情反馈反打（`srs_female`/`srs_male` 正反打或面部特写，不能全程只看交合处）；④ 肉戏全程有女主呻吟/浪叫或男主粗喘等声音反馈（`overall_soundscape` + 分镜表显式写「声音反馈」标注）。引擎收敛后肉戏镜自动写入「- 声音反馈: 全程呻吟/浪叫…」供监制审阅。另附肉戏优化三准则（强默认，非硬锁）：换体位必须写「抽出→挪腿移重心→重新支点→再结合」物理过渡链；拔除必须先于潮吹（体内痉挛→才抽出）；前戏强度递进「挑逗→前戏→插入→加速→高潮→余韵」。
10d. **H3 官方四段格式升级铁律（对齐外部 H3 生态）**：提示词正向后缀新增 `[Visual Constraints | Do Not Speak]` 负向声明锚（前置声明「这些是视觉约束、绝不出声不朗读」），并在 `Audio rule` 内新增 `Never speak stage directions...` + `Voice discipline` 反念稿死锁，杜绝模型把 Goal/姿势名/机位/负向等工程文本当台词念出来。中文台词仍只许在 `<d>[Chinese]…</d>` 内（正面视觉描述保持纯英文），严禁在视觉段混排中文（会诱发字幕烫印）。
10e. **文戏镜头语言铁律（Documentary Cinematography，补「发散型大模型不会设计文戏镜头」的空白）**：肉戏有据可查（体位代号→自动出镜头），文戏过去靠模型自由发挥导致站桩干聊、机位乱跳。治本办法是给文戏也造「查表式镜头配方」——写文戏先判「戏剧意图」，再查 `scripts/tunjing_dialogue.py` 的 `DIALOGUE_SHOT_RECIPES` 取「景别+机位+运镜+剪接节奏」。八类意图：`establish`(建立/wide/pull_reveal)、`confront`(对峙/cu/ots_depth)、`reaction`(反应/face/high_downward)、`escalate`(递进/mcu/push_tension)、`reveal`(揭示/mcu/arc_subtle)、`tease`(挑逗/cu/handheld_breath)、`standoff`(僵持/wide/static_side)、`breakdown`(崩溃/face/pull_reveal)。一段文戏标准呼吸 =「建立→对峙→反应→递进/揭示→收尾反应」，严禁一个景别拍到底、严禁跳轴、严禁只拍说话人不拍反应。详细配方见 `references/文戏镜头语言手册.md`。模型写文戏时不许自由发挥景别机位，必须 `--intent "意图"` 查表后填 `--chain`。
11. **自包含与零外部引用铁律（防跨机 Agent 幻觉与来源污染）**：本技能包是 100% 闭环的唯一权威母版。严禁在文档、模板、代码注释或提示词中引用任何不存在于本技能目录内的外部桌面目录、外部前端脚本、特定项目剧名/角色名、外部博主/教程来源或历史事故编号，所有经验一律内化为通用工业标准术语。
12. **派生文档单向生成与门禁同步铁律**：人类可读字典 `kinetic-positions.md` 必须由 `tunjing_poses_matrix.json` 单向生成，严禁手改脱节；任何提示词格式或体位 ID 规范的升级，必须同步更新 `tunjing_gatekeeper.py` 与 `dryrun_test.py`，确保自产产物 100% 通过自身门禁。
13. **双轨物理分流与构图排他死锁铁律（防浮空人脸与多手鬼影）**：严禁在同一镜头内“既要近景面部表情，又要下半身交合碰撞”（会导致 Cross-Attention 分裂产生浮空人脸或裁掉交合动作）。`hip`/`macro` 交合特写轨必须强制注入 R4 全肯定物理切边（`The frame is tightly cropped from waist to mid-thigh, containing exclusively the lower torso, hips, and pelvic contact junction`）；`face`/`cu`/`mcu` 情绪对白轨必须注入 `The frame is tightly cropped from chest and collarbones up to the head, containing exclusively the upper torso, neck, and face`（严禁在正向文本混入 `OUT OF FRAME` 否定词根，已由 `tunjing_core.py` 的 `sanitize_positive_only()` 自动净化）（交合仅靠肩颈震颤与发丝晃动体现），且特写框内严格执行肢体减法（最多 1 只手入画，其余手置于画外）。
14. **正向纯英文视觉隔离、四大字幕诱导元凶死锁与台词三段式气口铁律（防字幕烫印与身体僵死）**：
    - `integrated_multimodal_description` 视觉动作描述 100% 采用专业物理英文（严禁在 `<d>` 标签外残留任何中文字符被视觉编码器当成海报字幕烫印），画面描述与音效严格分栏（严禁在画面段写入 `sound / echoes / music / bgm` 等声音词汇诱发画面凭空找人张嘴）；
    - **四大字幕反向诱导元凶死刑禁令**（在 `Node 328 ConditioningZeroOut` 与 `CFG=1.0` 下，以下任一写法都会直接激活 Qwen3-VL 视觉字幕渲染器，在台词念出瞬间于人物腰腹部烫印白底描边大字幕）：
      1. **严禁在送入 `Node 263` 的正向文本末尾混入 `=== NEGATIVE ===` 段落**（负面清单只能留存于离线 JSON 字段，`Node 265` 的 `negative_prompt` 端口必须锁为 `None`）；
      2. **严禁在正向文本任何位置出现 `subtitles`、`captions`、`on-screen text`、`burn-in text`、`text ban` 等否定禁字词根**（模型对 `NO` 不敏感，但对 `SUBTITLES / ON-SCREEN TEXT` 词根极度敏感，写 `STRICTLY NO SUBTITLES` 等于命令模型画字幕；正向只需写 `clean full-bleed raw 35mm cinema frame`）；
      3. **严禁将说话人动作 `says:` 与 `<d>[Chinese]...</d>` 回车断成两行**（断行成 `<Subject 2> (S2) says:\n<d>...` 会被多模态编码器识别为 SRT 剧本字幕块，必须同行紧接写为 `SPEECH: From X.XXs to Y.YYs, ..., <Subject N> (Sx) says: <d>[Chinese]...</d> while ...`）；
      4. **严禁在 `At 0.00s,` 后机械复读 `mcu, static_side;` 等工程景别代号**（会破坏画幅裁切边界、拉远景别并在人物下半身留出深色字幕排版区）；
      5. **严禁 speaker 传真人名（如 `唐曼`/`陆骁`）——真人名不含「女/男」性别字，会命中引擎 `is_female_spk = ("女" in speaker or "S1" in speaker or "Subject 1" in speaker)` 的性别熔断被判成男声 → 自动转 off-screen voiceover 画外音 + 闭唇锁 → 嘴不能动 → 台词汉字被 H3 画成画面字幕**。speaker 只认引擎原生命名 `女子A`/`男子A`，其余（含真人名、任意缺失性别字的字符串）一律在 `tunjing_core.py` 源头强制归一，绝不带着真人名往下走。
    - 中文台词仅允许置于 `<d>[Chinese]...</d>` 容器内，且必须采用“前 25%（≥1.0s）纯动作起势 ➔ 中间念白 ➔ 尾段（≥0.7s）动作落定”三段式留白，成片抽帧质检必须精确抽检**台词发声中段（如 3.0s 处）**而非仅看起尾静音帧。
15. **反发散模型越权与首镜五联切片真质检铁律**：针对发散型大模型，严禁让模型手写提示词，只允许其选定 `--chain`、`--total`、`--scene`、`--lines` 参数并调用 `tunjing_scene.py` 机械装配，随后运行 `tunjing_diff_audit.py` 出具真源偏离度审计报告；渲染阶段废除仅看文件大小与 PSNR 的伪质检，强制执行“首镜生成落盘 ➔ 抽取 2%/50%/94% 关键帧肉眼核验通过 ➔ 放行全集批跑”，且每镜后调用 `/free` 冷却 10 秒释放显存碎片。
15b. **反古德哈特死锁·代码层查物理事实而非关键词铁律（防门禁被“改词”绕过）**：门禁若只查关键词，发散型大模型就只改关键词凑 PASS（古德哈特定律：指标一旦可被“写对”就失去判别力）——字幕连错多次的根正是「门禁查 NO SUBTITLES 词根 → 模型删词根 → 字照样画」。治本办法是在 `tunjing_core.py`（源头）、`tunjing_gatekeeper.py`（门禁）、`tunjing_runner.py`（提交闸门）三层各加「物理事实锁」：① speaker 真人名黑名单熔断；② 每条真实台词 `<d>[Chinese]…</d>` 前必须存在 `<Subject N> says:` 口型锚点；③ `says:` 不得与 `<d>` 断行。锁只看不可再“改词”糊弄的物理事实（真人名在不在、锚点在不在、断不断行），不看可改写的否定词。
    - **注：正则自检锁的两个容易踩的坑**（自己写的锁必须先自测再落地）：① 真人名黑名单用 `re.findall(r'(唐曼|陆骁|沈峥|许宁)', ...)` 精确字面匹配，勿用会把英文说话动词 `says`/`speaks` 误判成英文名的宽泛 `[A-Z][a-z]+` 模式；② 口型锚点检查只针对 `<d>[Chinese]…</d>` 真实台词，必须排除 engine header 里教 H3 语法的文法示例 `<d>...</d>`（不含 `[Chinese]`）。
16. **分号 (`;`) 黄金分割律、量化运镜与正向空间不变式铁律（防画红线与运镜失控）**：
    - 每条 `[Shot N]` 镜行必须以分号 `;` 一分为二：分号前仅写摄像机指令（`景别, 机位角度, 运动类型+幅度+速度量化值`），且强制执行**先静后动三段式运镜**（`0.00s to 1.00s holds steady locking the initial posture, then from 1.00s to T-0.80s [运镜], holding steady for the final 0.80s`，防开局前 15 帧脸手变形），9:16 竖屏俯仰角严格收紧在 `12~15度` 微仰/微俯以保身材修长比例，分号后只写人与物的可见物理动作；工作景别阶梯（Working Shot Ladder）确保 `macro` / `wide` 极端景别用完一镜后自动弹回 `mcu` / `cu` 工作景别；
    - 单人正反打强制执行**屏幕左右方向与俯仰视线互补锁**（`srs_male` 锁画面左侧向右下 12 度凝视，`srs_female` 锁画面右侧向左上 12 度迎视），确保剪辑视线严丝合缝对撞；
    - 严禁在画面段出现 `axis`、`line`、`lines`、`越轴`、`轴线`、`分界线` 等具象构图名词（会被视觉编码器直接画成实体线条），统一采用**正向空间不变式（Positive Invariant）**：`The camera stays on the same side of them throughout; <Subject 1> is on the left, <Subject 2> is on the right.`；
    - 严禁使用 `very slowly`、`extremely`、`slightly`、`suddenly` 等模糊程度副词，一律替换为厘米与秒数的确定性物理量；多镜切换仅允许使用官方 5 大英文切镜绑定短语（`the camera cuts to` / `the shot cuts to` / `the shot transitions to` / `the shot changes to` / `the shot switches to`），严禁使用 `fade / dissolve / wipe` 或中文“镜头切至”。
17. **A/B/C 三档槽位物理隔离、单调服装状态机与弱构图引用铁律（防单人镜鬼影与透视畸变）**：
    - **三档槽位隔离与 9 图 3 音扩展挂载**：永远保持 `<Picture 1>`（Node 51）为女主槽、`<Picture 2>`（Node 49）为男主槽、`<Picture 3>`（Node 50）为场景槽；双人同框镜（Tier A）挂载 `[女母版, 男母版, 场景底图]`；单人正反打特写镜（Tier B，`srs_female` / `srs_male`）必须将未入画角色的槽位强制替换为纯净场景底图占位（女单人 `[女母版, 场景图, 场景图]`、男单人 `[场景图, 男母版, 场景图]`，严禁将男主图错塞入 Node 51 女主槽导致性别特征错乱），从硬件输入端根除背景暗部裂殖出第二张人脸鬼影；纯环境空镜（Tier C，`env_establish` / `empty_cut`）三槽全挂场景底图；工作流完整保留 9 个图像参考槽（`ref_image_0~8`：Nodes 51/49/50 为常驻 3 槽，Nodes 43/19/23/199/200/201 为 `<Picture 4~9>` 扩展槽；当 `00_资产/` 含 `daoju_*` / `prop_*` 道具图且镜头为 `prop_insert` / `present_item` 时，自动挂载至第 4 槽 Node 43 `<Picture 4>` 并在头部声明 `<Subject 4>`，严禁拔掉 Node 50 场景槽顶替道具，无道具镜自动断开 `ref_image_3~8`）与 3 个音频参考槽（`ref_audio_0~2`，Nodes 14/15/48 挂载男女主定版干声 `<Audio 1>` / `<Audio 2>` 锁死全集音色）；
    - **单调不可逆服装状态机**：全片服装按 `穿衣 (dressed) ➔ 半脱 (partially_undressed) ➔ 全裸 (nude)` 单向演进，一旦完成脱衣，后续镜头永久锁死素身母版，严禁回跳穿衣；
    - **场景弱构图引用**：`retention_analysis` 中 `<Subject 3>` 必须声明 `weak_reference for exact camera framing`，防止切近景/特写时被广角场景底图的远景透视拉扯导致家具畸变。
18. **空镜/闪回三不铁律与场景陈设白名单铁律（防门框拉丝与假家具脑补）**：
    - **零胶片特效词**：严禁使用 `flashback, overexposed, halation, dreamy glow, light flare` 等特效词破坏建筑五金几何边缘；
    - **闭门不写推门**：底图为闭合门板时，严禁强写推门进出大位移，必须保持门体与五金静态定格；
    - **陈设 100% 取自底图白名单**：家具与道具描述必须严格锚定 `<Picture 3>` 真实存在的元素，严禁脑补底图不存在的陈设，且单次线性动作严禁在多时间段重复描写两遍。
19. **对话回合制（C27c/C27d）、肌肉神态同句绑定与官方画外音死公式铁律（破除 3 秒静止假人）**：
    - **按回合切镜**：15 秒对话段开口交互 ≥ 6 次，严禁同一角色连续独占 2 个镜头发声，单次发言 ≤ 15 字（超长台词必须拆镜插入听者反应或转局部特写画外音）；
    - **12 大主动表演情绪光谱 + 黄金反应公式（1个明确情绪点名 + 2处可见物理泄露 + 1.5s内落定保持）**：严禁角色静止超过 3 秒；内置 12 种主动表演情绪底色（`生气/anger_rage`、`冷怒/cold_wrath`、`忧伤/grief_sorrow`、`委屈/humiliated_tears`、`得意冷笑/triumph_smirk`、`欣喜温柔/warm_joy`、`恐惧惊慌/fear_panic`、`嫉妒怨恨/jealousy_spite`、`嘲讽/mockery`、`挑衅/provocation`、`隐忍/forbearance`、`迷离失神/ecstasy`）与 3 大反应阶段（`inhibition/surge/aftermath`），每条情绪统一采用「1个精准情绪词点名 + 2处当前景别可见解剖/呼吸泄露 + 1.5秒内落定保持（`settling within 1.5 seconds`）」黄金配方，支持 `--lines "4:男子A(生气):台词|5:女子A(委屈):台词"` 显式标注或根据台词字面自动感知，且同时声明未说话听者的闭口微反应（`while <Subject M> keeps lips completely closed`）；
    - **画外音三要素死公式**：凡内嵌画外音/内心独白，必须严格采用 `<Subject N> (Sx) says in an off-screen voiceover: <d>[Chinese]...</d> while her/his lips remain completely closed.`；交合微距镜（`hip/macro`）若有台词，必须自动转为该画外音公式，且对话镜严禁误锁 `HEADS OUT OF FRAME`，换体位转场镜严禁误锁 `LOWER BODY OUT OF FRAME`。
20. **剧本原义死锁（00b）、三级戏份门禁与工作流黄金拓扑铁律**：
    - **原义死锁与全剧集视听导演调度**：严禁自发温吞慢热降级篡改剧本开篇强冲突动作，严禁私加事后温存躺床戏或剧本外体位；全集拆镜必须具备完整的“开场环境建立 (`env_establish`) ➔ 双人封堵对峙 (`blocking_2s`) ➔ 单人正反打交锋 (`srs_male` ⇄ `srs_female`) ➔ 场间物象微距 (`prop_insert`) ➔ 多体位冲撞与正反打交替 ➔ 尾声收束 (`outro_solo`)”导演调度，严禁全片仅排双人连体中景；道具微距原语保持抽象槽位 `prop_insert`，严禁写死特定剧集物件（如房卡/婚戒/支票）以免诱发大模型刻板印象；
    - **空间图池单槽轮换法（Multi-View Pool, Single-View Per Shot）**：同一房间准备 3~4 张不同视角底图（主全景 `scene_main.png`、墙面立面 `scene_wall.png`、承托面近景 `scene_close.png`），但每一镜的 `<Picture 3>`（槽位 2）**只挂 1 张最匹配当前机位/景别的空间底图**（切特写/微距挂 `scene_close.png` 防丢背景，墙边戏挂 `scene_wall.png`），严禁单镜同时混喂多张空间图导致空间错乱，且 `<Picture 3>` 全片永不断电；
    - **三级戏份门禁**：Gate 3 自动按「含口交戏 / 独处自慰戏 / 纯插入交合戏」三级分档核验，不强迫无口交剧本硬塞口交；
    - **工作流黄金拓扑与满血底模锁**：Node 38 优先挂载 `qwen3vl_32b_minimax_h3_ultra_uncensored_heretic_int8_convrot.safetensors`（大内存下替代 4-bit `nvfp4` 以保多图跨模态对齐精度），Node 400 挂载 `MysticXXX_MMH3-V5-ref2va.safetensors`（文戏/穿衣/空镜权重强制归 `0.0`，肉戏恢复 `0.45~0.50`），Node 53 (DMAD) 与 Node 404 (如梦似幻) 锁定 `0.80`，Node 265 `ref_image_size` 统一设为 `match`，Node 364 `filename_prefix` 与全链路切片命名统一采用 `EP00X_SHOT_00X` 格式；物理切除悬空的 `Node 333 (MiniMaxH3SigmaShift)` 与武打倍速 LoRA 组（342~345），锁死 12GB 低显存四护法链（`Node 331 -> 332 -> 403 -> 401`）；每次提交动态更新帧长时必须同时同步 `Node 259 (PrimitiveFloat 秒数)` 与 `Node 250 (ComfyMathExpression)`，严禁锁死 15.0s 导致台词后半段进入无指令真空期诱发字幕；每镜渲染后调用 `/free` 释放显存时仅执行 `.read()`，严禁对空响应调用 `json.loads()`；所有资产文件名必须为纯 ASCII 英文/数字/下划线，启动前动态校验 ComfyUI `--input-directory` 真实挂载目录并覆盖 `male_master.png / female_master.png / scene_main.png` 模板占位符，确保单实例进程运行防 OOM；跨镜接缝两边必须换视角或换景别，需要定格抽尾帧时追加 `The movement stops and the picture holds still for the last second.`。
