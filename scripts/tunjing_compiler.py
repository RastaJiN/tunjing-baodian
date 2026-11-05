"""
吞鲸极速提示词装配与校验引擎 (Tunjing Prompt Compiler & Linter)
专为 MiniMax H3 / 视频扩散模型打造：
1. 自动注入吞鲸体位字典 (Kinetic Kama-Sutra)
2. 剥离人类废话，全英文物理动词
3. 严格校验台词包裹与槽位对齐
"""

import sys
import re
import argparse

def lint_tunjing_prompt(text):
    errors = []
    warnings = []
    
    # 1. 检查台词是否规范
    speech_matches = re.findall(r'<d>(.*?)</d>', text, re.DOTALL)
    if not speech_matches and 'Track: Ref2V' in text:
        warnings.append("提示：本镜头标注为 Ref2V 但未检测到台词 <d> 标签，若为纯动作镜请忽略。")
        
    for sp in speech_matches:
        if not sp.strip():
            errors.append("错误：检测到空的台词标签 <d></d>！")
            
    # 2. 检查是否有未经翻译的中文描述（排除台词内部）
    # 将台词部分剔除后检查正向文本
    clean_text = re.sub(r'<d>.*?</d>', '', text, flags=re.DOTALL)
    # 排除中文标点和常用注释标记
    chinese_chars = re.findall(r'[\u4e00-\u9fa5]', clean_text)
    if len(chinese_chars) > 20: # 允许少量注释，但正文必须全英文
        errors.append(f"错误：正文描述包含过多中文字符 ({len(chinese_chars)} 个)！送模正文必须为纯英文物理描述。")
        
    # 3. 检查受控词与毒性油光词
    toxic_words = ['sweat sheen', 'oily face', 'shiny plastic', 'vaseline skin', 'dewy glisten']
    for tw in toxic_words:
        if tw in clean_text.lower():
            warnings.append(f"警告：检测到容易引发塑料油光的词汇 '{tw}'，建议改用纯哑光柔光描述。")
            
    # 4. 检查槽位对应关系
    if '<Subject 1>' in text and 'ref_image_0' not in text and '<Picture 1>' not in text:
        warnings.append("警告：声明了 <Subject 1> 但未检测到对应的母版绑定 (<Picture 1> 或 ref_image_0)。")
        
    return errors, warnings

def main():
    parser = argparse.ArgumentParser(description="吞鲸提示词编译器")
    parser.add_argument("file", help="待检测的提示词文件路径")
    args = parser.parse_args()
    
    try:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        sys.exit(1)
        
    errors, warnings = lint_tunjing_prompt(content)
    
    print("=" * 50)
    print("吞鲸成人漫剧引擎 · 提示词体检报告")
    print("=" * 50)
    
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
        print("\n结果: PASS (可直接送入 ComfyUI 队列)")
        sys.exit(0)

if __name__ == "__main__":
    main()
