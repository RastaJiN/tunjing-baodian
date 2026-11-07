# 吞鲸生成前自我终极审查标准 (Tunjing Pre-Render Self-Audit Standard)
> 吞鲸工作室专属军规 · 任何项目在进入 Gate 6 渲染导出前，必须通过本标准的六大维度 100% 盲检并出具报告。
> 唯一准则：全部维度 PASS 方可放行；任一维度出现 REJECT 立即阻断修复。

---

## 终审六大维度硬核指标（One-Strike Kill 违者必杀）

### 维度一：资产实名与槽位 (Asset & Slot Alignment)
- [ ] **定版母版齐全**：`00_资产/` 目录下男主 2x3 母版、女主 2x3 母版、纯净场景底图物理存在且非空；
- [ ] **Reference map 槽位对齐**：提示词中 `<Picture 1>` 锁定场景环境（仅锁空间与光影，不锁人物姿态），`<Picture 2>` 与 `<Picture 3>` 锁定男女角色身份；
- [ ] **无第三人裂殖隐患**：双人镜头严禁在正文中描写任何未挂载母版的第三人入画。

### 维度二：音画台词咬合 (Audio-Visual Sync)
- [ ] **台词时长公式合规**：每句台词满足 $\frac{\text{汉字数}}{3.0} + (\text{省略号数} \times 0.8) + 1.0\text{s} \le \text{本镜时长}$；
- [ ] **Audio rule 声明到位**：包含 `characters may only speak the exact words inside <d>...</d>; never read pose, intensity, camera, or negative instructions aloud`；
- [ ] **OS 防对口型物理死锁**：凡含画外音/内心独白的镜头，必须写明嘴部物理占位锁（`lips remain completely closed` / `bite down on lower lip`）或采用背向/微距机位逃逸。

### 维度三：换体位与特写契约 (Intimate Choreography Contract)
- [ ] **中途换体位**：单集高能段至少调用 2 个不同的吞鲸引擎交合体位 ID（如 `missionary` ➔ `cowgirl` ➔ `doggy`），并通过物理换位配方平滑衔接；
- [ ] **3 次结合部交合特写**：包含至少 3 处独立的腰胯/结合部特写（`hip` / `macro`），严禁用手部或面部充数；
- [ ] **口交/深喉特写独立成镜**：包含至少 1 处 `bj` / `deepthroat` 等口爱近景或唇齿微距；
- [ ] **1.5s 生理阻断微距**：核心冲撞前后嵌入指节抓紧承托沿、足弓绷直或咬唇的微观受力特写。

### 维度四：受控运镜规范 (Controlled Camera & Shot Density)
- [ ] **短镜拆解密度合规**：2 分钟高能戏拆解为 20~30 个 2~6s 独立短镜（平均单镜 ≤8s），严禁将多个体位压进单一长镜头；
- [ ] **逐镜景别与机位齐全**：每一镜均明确标注景别（`wide`/`mcu`/`hip`/`cu`/`macro`/`face`）与受控机位（`static_side`/`static_rear`/`low_hip`/`ots`/`high_angle`/`slow_push`/`follow_soft`），且 `wide` 占比 ≤10%；
- [ ] **零毒性运镜词**：全片无 `orbit, 360, fast zoom, chaotic reframing` 等诱发换脸与肢体崩塌的运镜。

### 维度五：提示词纯净度 (Six-Block Structure & Anti-Grease)
- [ ] **吞鲸标准六段式完整**：每条提示词完整具备 `[1] Goal & Audio rule`、`[2] Reference map`、`[3] Consistency & Motion quality`、`[4] Pose focus chain`、`[5] integrated_multimodal_description`、`[6] overall_soundscape` 及独立成段的 `NEGATIVE` 列表；
- [ ] **正向肯定句压油内嵌**：包含 `authentic matte velvet skin finish, powdered dry texture, natural human skin with visible fine pores`，零 `sweat sheen, oily face, shiny plastic` 等毒性词；
- [ ] **场地承托面动态一致**：动作描述与环境底噪已通过 `with_scene_surface` 适配当前 `--scene` 场地，无跨场地家具穿帮（如在书桌或浴室出现“床单/床板声”）。

### 维度六：纯血Ref2V单轨规范 (Pure Ref2V Pipeline Compliance)
- [ ] **100% 纯血 Ref2V**：全片统一标定 `[Track: Ref2V]`，彻底杜绝单镜抽首帧 I2V 垫图；
- [ ] **物理帧长合规**：导出的 `批量任务.json` 每一镜帧数严格满足 `(frames - 5) % 17 == 0`；
- [ ] **双轨构图死锁与反伪质检**：交合镜具备 `HEADS AND FACES STRICTLY OUT OF FRAME`，面部对白镜具备 `LOWER BODY STRICTLY OUT OF FRAME`，且首批渲染严格执行“首镜五联/三点切片（2%/50%/94%）肉眼核验放行制”，严禁仅凭文件大小或 PSNR 盲跑全集。

---

## 终审交付凭证模板 (`审查/生成前终审报告.md`)

```markdown
# 吞鲸工作室 · 渲染放行终审报告 (Clearance Report)
- 剧集：{{ DRAMA_NAME }} · EP{{ EP_NUM }}
- 自审执行人：鲸鲸 (执行导演)
- 审查结论：[PASS 放行 / REJECT 驳回修复]

### 核查清单对账：
1. 资产实名与槽位：[PASS / REJECT] (男女2x3母版与场景底图齐全，Picture 1/2/3 槽位严格对齐)
2. 音画台词咬合：[PASS / REJECT] (台词均满足 3.0字/s+1.0s 余量，OS 具备闭口物理锁)
3. 换体位与特写契约：[PASS / REJECT] (多体位转换清晰，交合特写≥3次，口交特写与阻断微距齐全)
4. 受控运镜规范：[PASS / REJECT] (2~6s 短镜拆解，逐镜标明景别与受控机位，wide 占比合规)
5. 提示词纯净度：[PASS / REJECT] (吞鲸标准六段式完整，内嵌正向肯定句压油，场地承托面零穿帮)
6. 纯血Ref2V单轨规范：[PASS / REJECT] (全片 100% 纯血 Ref2V 单轨，批量任务帧长全部符合 5+17*N)
```
