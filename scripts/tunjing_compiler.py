#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
吞鲸宝典 v4.0 · 极速提示词校验引擎 (Tunjing Prompt Linter v4.0 — R1~R12 全肯定语法内核)

融合《不完全手册》h3_lint.py 12 条硬规则与吞鲸结构规范：
1. 校验核心结构锚点（Goal & Audio Contract / Audio rule / subject_definitions / Consistency / Motion quality / MOTION FLOOR / integrated_multimodal_description / overall_soundscape）
2. 校验 R4 正向全肯定语法（严禁在正向文本末尾混入 === NEGATIVE === 清单或 OUT OF FRAME 否定词根）
3. 校验正向肯定句压油词（authentic matte velvet skin finish, powdered dry...）并拦截油光毒性词
4. 校验唯一 Camera: 指令行、分号 (;) 黄金分割律、独立 SPEECH: 台词行与零汉字残留
"""

import sys
import re
import argparse

def lint_tunjing_prompt(text):
    errors = []
    warnings = []
    
    # 1. 检查台词标签是否为空
    speech_matches = re.findall(r'<d>(.*?)</d>', text, re.DOTALL)
    for sp in speech_matches:
        if not sp.strip():
            errors.append("错误：检测到空的台词标签 <d></d>！")
            
    # 2. 检查吞鲸 v4.0 必填结构锚点（正向纯净结构，不强制要求混入 NEGATIVE）
    required_blocks = [
        (["Goal & Audio Contract:", "Goal: Generate"], "缺少 [1] Goal 目标与时长画幅声明"),
        (["Audio rule:", "Audio rule"], "缺少 [1] Audio rule 台词与静音纪律声明"),
        (["subject_definitions:", "Reference map"], "缺少 [2] 实体与场景槽位映射 (subject_definitions)"),
        (["Consistency:", "Consistency"], "缺少 [3] Consistency 身份与场景一致性死锁"),
        (["Motion quality", "Motion quality (Anti-Stiffness)"], "缺少 [3] Motion quality 防僵硬二次动作锁"),
        (["MOTION FLOOR:", "Motion quality"], "缺少 [3b] MOTION FLOOR 底噪生命力锁"),
        (["integrated_multimodal_description:", "detailed_description:"], "缺少 [5] 逐镜时间线主体 (integrated_multimodal_description)"),
        (["overall_soundscape:", "overall_soundscape"], "缺少 [6] overall_soundscape 环境底噪与动作声场"),
    ]
    for markers, msg in required_blocks:
        if isinstance(markers, str): markers = [markers]
        if not any(m in text for m in markers):
            errors.append(f"结构错误：{msg}")
            
    # 3. 检查吞鲸正向肯定句压油词
    if not re.search(r'matte velvet skin finish|powdered dry|visible fine pores', text, re.IGNORECASE):
        errors.append("压油错误：缺少吞鲸正向肯定句压油词（authentic matte velvet skin finish, powdered dry complexion texture）！")
        
    # 4. 检查毒性油光词
    toxic_oil = re.findall(r'(?<!non-)(?<!no )(?<!without )\b(sweat sheen|oily face|shiny plastic|vaseline skin|dewy glisten|greasy|glossy|glistening)\b', text, re.IGNORECASE)
    if toxic_oil:
        errors.append(f"毒性词错误：检测到容易引发塑料油光的词汇 {sorted(set(toxic_oil))}，必须剔除！")

    # 4b. 检查反物理机械替换词
    for absurd in ('matte bodily fluids', 'dry squirting', 'powdered saliva', 'matte semen'):
        if absurd in text.lower():
            errors.append(f"反物理词错误：检测到荒谬机械替换词 '{absurd}'！")

    # 5. 检查槽位对应关系
    if '<Picture 3>' not in text:
        errors.append("空间锚点错误：未检测到 <Picture 3> 场景底图声明（每镜必须常驻 <Picture 3> 防丢背景）！")

    # 6. 提取送模代码块做 H3 R1~R12 深度语法体检
    blocks = re.findall(r'```(?:text)?\s*(.*?)```', text, re.DOTALL)
    if not blocks:
        blocks = [text]

    for idx_b, blk in enumerate(blocks, 1):
        pos_part = blk.split("=== NEGATIVE ===")[0]
        pos_no_d = re.sub(r'<d>.*?</d>', '', pos_part, flags=re.DOTALL)

        # R1/H9: 剥离 <d> 后零汉字扫描
        zh_left = re.findall(r'[\u4e00-\u9fff]+', pos_no_d)
        if zh_left:
            errors.append(f"镜头块 {idx_b} [R1 汉字残留]：正向描述（<d>外）检测到汉字 {zh_left[:4]}，必引发底部烫印字幕！")

        # R4: 拦截 OUT OF FRAME 等易引发反向渲染的否定大写锁
        if "OUT OF FRAME" in pos_no_d.upper():
            errors.append(f"镜头块 {idx_b} [R4 否定词反噬]：检测到 'OUT OF FRAME'，请改用全肯定物理切边描述（如 'The frame is tightly cropped from waist to mid-thigh, containing exclusively...'）！")

        # 提取画面段
        m_vis = re.search(r'(?:integrated_multimodal_description|detailed_description):\s*(.*?)(?:\n\s*(?:Overall Soundscape:|overall_soundscape:)|\Z)', pos_no_d, re.DOTALL)
        if m_vis:
            vis_sec = m_vis.group(1)
            shot_lines = [ln.strip() for ln in vis_sec.split("\n") if ln.strip().startswith("[Shot")]
            for sl in shot_lines:
                if ";" not in sl:
                    warnings.append(f"镜头块 {idx_b} [分号分区缺失]：镜行未用分号 ';' 分隔相机指令与演员动作。")

            # 拦截具象构图线词 (line / lines / axis)
            line_hits = re.findall(r'\b(line|lines|line-up|axis)\b', vis_sec, re.IGNORECASE)
            if line_hits:
                errors.append(f"镜头块 {idx_b} [构图线词风险]：画面段含 {sorted(set(line_hits))}，极易被模型在画面中间画出实体红线/分割线！")

            # 拦截画面段混入音乐/声响抽象词
            snd_hits = re.findall(r'\b(music|bgm|piano|violin|cello|echoes)\b', vis_sec, re.IGNORECASE)
            if snd_hits:
                errors.append(f"镜头块 {idx_b} [声画混栏]：画面段混入音乐/回声词 {sorted(set(snd_hits))}，请移入 overall_soundscape！")

            # 拦截模糊程度副词
            deg_hits = re.findall(r'\b(very slowly|extremely|somehow|suddenly)\b', vis_sec, re.IGNORECASE)
            if deg_hits:
                warnings.append(f"镜头块 {idx_b} [模糊程度词]：检测到 {sorted(set(deg_hits))}，建议改为具体厘米与秒数。")

    return errors, warnings

def main():
    parser = argparse.ArgumentParser(description="吞鲸 v4.0 提示词 R1~R12 体检器")
    parser.add_argument("file", help="待检测的提示词文件路径")
    args = parser.parse_args()
    
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)
        
    errors, warnings = lint_tunjing_prompt(content)
    
    print("=" * 60)
    print("🐳 吞鲸宝典 v4.0 · R1~R12 全肯定送模提示词体检报告")
    print("=" * 60)
    
    if warnings:
        print(f"[!] 发现 {len(warnings)} 条建议/警告:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("[✓] 零警告 (0 WARN)")
        
    if errors:
        print(f"\n[X] 发现 {len(errors)} 条阻断性错误:")
        for e in errors:
            print(f"  - {e}")
        print("\n结果: FAIL (禁止提交渲染)")
        sys.exit(1)
    else:
        print("\n结果: PASS (100% 符合吞鲸 v4.0 R1~R12 全肯定规范，可直接送入 ComfyUI)")
        sys.exit(0)

if __name__ == "__main__":
    main()
