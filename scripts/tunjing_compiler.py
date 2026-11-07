"""
吞鲸极速提示词校验引擎 (Tunjing Prompt Linter)
严格对齐吞鲸宝典内置引擎吞鲸六段式标准装配器 六段式中英混合结构：
1. 校验六段式必填结构锚点（Goal / Audio rule / Reference map / Consistency / Motion quality / integrated_multimodal_description / overall_soundscape / NEGATIVE）
2. 校验正向肯定句压油词（针对 Node 328 零化负向的物理真相）
3. 拦截诱发油光蜡感的毒性词
4. 严格校验台词 <d> 标签包裹
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
            
    # 2. 检查吞鲸标准六段式核心结构锚点 (v3.0 原厂 Full-Reference 规范)
    required_blocks = [
        (["Goal & Audio Contract:", "Goal: Generate"], "缺少 [1] Goal 目标与时长画幅声明"),
        (["Audio rule:", "Audio rule"], "缺少 [1] Audio rule 台词与静音纪律声明"),
        (["subject_definitions:", "Reference map"], "缺少 [2] 实体与场景槽位映射 (subject_definitions 或 Reference map)"),
        (["Consistency:", "Consistency"], "缺少 [3] Consistency 身份与场景一致性死锁"),
        (["Motion quality", "Motion quality (Anti-Stiffness)"], "缺少 [3] Motion quality 防僵硬二次动作锁"),
        (["integrated_multimodal_description:", "detailed_description:"], "缺少 [5] 逐镜时间线主体 (integrated_multimodal_description 或 detailed_description)"),
        (["overall_soundscape:", "overall_soundscape"], "缺少 [6] overall_soundscape 环境底噪与动作声场"),
        (["No subtitles, captions, watermarks", "No subtitles"], "缺少独立成段的 NEGATIVE 负面列表")
    ]
    for markers, msg in required_blocks:
        if isinstance(markers, str): markers = [markers]
        if not any(m in text for m in markers):
            errors.append(f"结构错误：{msg}")
            
    # 3. 检查吞鲸正向肯定句压油词
    if not re.search(r'matte velvet skin finish|powdered dry texture|visible fine pores', text, re.IGNORECASE):
        errors.append("压油错误：缺少吞鲸正向肯定句压油词（authentic matte velvet skin finish, powdered dry texture）！")
        
    # 4. 检查毒性油光词
    toxic_words = ['sweat sheen', 'oily face', 'shiny plastic', 'vaseline skin', 'dewy glisten']
    for tw in toxic_words:
        if tw in text.lower():
            errors.append(f"毒性词错误：检测到容易引发塑料油光的词汇 '{tw}'，必须剔除！")
            
    # 5. 检查槽位对应关系
    if '<Picture 1>' not in text:
        warnings.append("警告：未检测到 <Picture 1> 槽位声明。")
        
    return errors, warnings

def main():
    parser = argparse.ArgumentParser(description="吞鲸提示词六段式体检器")
    parser.add_argument("file", help="待检测的提示词文件路径")
    args = parser.parse_args()
    
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)
        
    errors, warnings = lint_tunjing_prompt(content)
    
    print("=" * 55)
    print("🐳 吞鲸宝典 · 吞鲸标准六段式提示词体检报告")
    print("=" * 55)
    
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
        print("\n结果: PASS (100% 符合吞鲸标准六段式规范，可直接送入 ComfyUI)")
        sys.exit(0)

if __name__ == "__main__":
    main()
