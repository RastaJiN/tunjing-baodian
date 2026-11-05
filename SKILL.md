---
name: tunjing-adult-drama-engine
description: 吞鲸工作室专属·成人漫剧极速生产引擎。专治文戏乏味、动作像流水账配种、体位融化及分镜平铺。会话中说「吞鲸开始」即刻唤醒并启动门禁流水线。
version: 1.1.0
author: 吞鲸工作室 (Swallowing Whale Studio)
license: MIT
metadata:
  hermes:
    tags: [adult-drama, anime, kinetic-kama-sutra, bounce-cut, tunjing]
    related_skills: [drama-production-standard]
---

# 吞鲸工作室 · 成人漫剧极速生产引擎 (Tunjing Adult Drama Engine v1.1)

> **吞鲸宗旨**：**文戏带刀有张力，做爱带电有花样，步步门禁不跳步，工业流程一次过。**
> 会话中输入启动口令「吞鲸开始」，系统立即挂载本引擎并进入五大刚性门禁流水线作业。

---

## 一、唯一启动口令与握手协议 (Trigger & Handshake)

### 唤醒口令：`吞鲸开始`
当用户在会话中发送包含 **「吞鲸开始」**（或「吞鲸启动」、「开始吞鲸」）时：
1. **立即第一行响应固定应答**：
   ```text
   吞鲸成人漫剧引擎已启动！吞鲸工作室流水线就绪，正在进行第 1 步资产门禁检测……
   ```
2. **强制挂载本 SKILL 全部规则**，初始化项目状态机文件 `.tunjing_status.json`；
3. **严禁越级直接写剧本或分镜**，必须按顺序执行五大刚性门禁（Gate 1 ➔ Gate 5）。

---

## 二、五大刚性步进门禁 (The 5 Mandatory Gates)

**核心铁律**：严禁未经前置门禁批准私自进入下一步！每一步完成后必须由 `scripts/tunjing_gatekeeper.py` 判定 PASS 后，才允许推进！

```
[Gate 1：资产死锁门禁] ➔ 必须具备男女主穿衣/素身定版母版 + 纯净场景底图
         ↓ PASS
[Gate 2：刀锋剧本门禁] ➔ 必须具备实体道具流转 + 三幕式推进 + 显式引用 POS 体位编号 + <d> 台词
         ↓ PASS
[Gate 3：弹跳分镜门禁] ➔ 必须具备 1.2s~2.0s 生理阻断微距 + [Track: Ref2V / I2V_Pose] 双轨标注
         ↓ PASS
[Gate 4：提示词编译门禁] ➔ 必须纯英文物理动量正文 + 零毒性油光词 + 继承 kinetic-positions 动量
         ↓ PASS
[Gate 5：出片渲染门禁] ➔ 运行 export_comfy_payload.py 提交 ComfyUI 队列完成最终出片！
```

---

## 三、核心资产与驱动链接 (The Core Engine Assets)

1. **【五大步进门禁中枢】**：`scripts/tunjing_gatekeeper.py`
   - 命令行调用：`python scripts/tunjing_gatekeeper.py <项目目录> [步骤1-5]`
   - 步进拦截：前置步骤不合格时直接抛出 `[X] 阻断拦截`，严禁跳步。
2. **【12套生物力学体位字典】**：`references/kinetic-positions.md`
   - POS-01 到 POS-12，全套由支点、受力凹陷、脊柱反弓与神经痉挛写成；
   - 随调随用，支持一键注入分镜与提示词。
2. **【视听弹跳分镜规范】**：`references/shot-design-and-bounce.md`
   - 镜头组架构（Inquiry ➔ Denial ➔ Kinetic ➔ Aftermath）；
   - 1.5s 生理阻断微距（咬唇/抓床单/足弓反弓）+ 双轨（Ref2V / I2V_Pose）分流。
3. **【ComfyUI 双轨渲染工作流与节点规范】**：`references/comfyui-dual-pipeline-spec.md`
   - 明确锁死：文戏纯血 Ref2V 与 高危肉戏 I2V 姿态垫图的节点架构与参数（CFG=1.0、Steps=10-12、9:16画幅）。
4. **【单集工业化生产模板】**：`templates/episode_template.md`
   - 一键脚手架，标准化三幕式剧本与钩子设定。
5. **【提示词编译器与体检工具】**：`scripts/tunjing_compiler.py`
   - 全英文物理动量输出，零废话，自动拦截语法与槽位错误。
6. **【通用 ComfyUI 跨机分发脚本】**：`scripts/export_comfy_payload.py`
   - 保证任何机器下载后，只要运行端口 8188 即可 1:1 无损提交渲染队列。
7. **【一键最小闭环跑通脚本】**：`scripts/dryrun_test.py`
   - 换到任何新工作机，运行这一个脚本，立刻自动生成标准 EP001 测试用例，换算物理帧长并导出 ComfyUI Payload，验证当前机器是否 100% 具备出片能力。

---

## 吞鲸极速作业四步走 (The 4-Step Pipeline)

```
[步骤一：刀锋剧本] ➔ 实体证据流转 + 心理逼问 + 强行阻断 + 肉体作为最后清算
       ↓
[步骤二：资产建库] ➔ 角色穿衣/素身母版死锁 + 纯净场景底图
       ↓
[步骤三：弹跳分镜] ➔ 调取 POS 体位字典 + 嵌入 1.5s 生理阻断特写 + 标注双轨
       ↓
[步骤四：出片合成] ➔ Ref2V(文戏) / I2V姿态垫图(高危肉戏) + 音轨切点咬合成片
```

---

## 吞鲸实战铁律与避坑纪律 (Studio Iron Laws & Pitfalls)

1. **禁止先跑分镜再定母版**：写剧本前必须先锁定角色穿衣与同源素身母版（同一 Seed 纯文生或同源脱衣），否则无物理脸型身材依托，分镜动作与景别全是空中楼阁。
2. **文戏不聊闲天**：开场 15 秒必须砸出具象证据道具（发票/内衣/录音/手机），每一句台词都在剥心理防线，拒绝无因果对坐聊天。
3. **前戏必有物理阻断**：第一次身体接触必须遭遇阻断（电话震动/门外脚步声/诛心拒绝），将观众情欲预期压至临界点。
4. **做爱必带台词**：插入和深顶时，男方必须进行诛心逼问（复刻伴侣习惯/戳穿婚姻伪善），女方必须经历从道德抗拒到生理失控高潮的完整弧线。
5. **体位必须带电**：严禁写“后入/抽送”等抽象词汇，必须从 `kinetic-positions.md` 提取物理动量（脊柱反弓、桌面抓白、大腿凹陷、水汽与神经痉挛）。
6. **高难度动作坚决垫图 (双轨制)**：复杂多人缠绕体位（POS-01 ~ POS-11），在生图底模打出姿态关键帧走 I2V 启动动力学，严禁文生视频纯血 Ref2V 硬赌导致四肢融化。
7. **禁止同余方程绑架剪辑呼吸感**：总帧数与帧长公式（`length = 5 + 17*N`）由脚本自动按单镜请求秒数就近换算，剪辑线通过 J/L-Cut 和微调吞吐多余帧，严禁用固定镜数强行平摊镜头时长摧毁节奏。
8. **跨机 1:1 交付前先跑 Dry-Run**：在目标机器上正式出片前，必须先执行 `python scripts/dryrun_test.py` 验证帧长算力、Payload 导出与目录连通性，通过后再启动 ComfyUI 批量渲染。
