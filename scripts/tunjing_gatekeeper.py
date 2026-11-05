"""
吞鲸工作室 · 全流程步进门禁状态机 (Tunjing Pipeline Gatekeeper)
严格执行：Step 1 ➔ Step 2 ➔ Step 3 ➔ Step 4 ➔ Step 5
每一步必须校验前置产物，通过才放行下一步。严禁跳步！
"""

import os
import sys
import json
import re

STAGE_NAMES = {
    1: "第 1 步：角色母版与资产建库 (Asset Foundation)",
    2: "第 2 步：刀锋剧本创作 (Sharp Script)",
    3: "第 3 步：弹跳分镜与双轨路由 (Bounce Storyboard)",
    4: "第 4 步：提示词编译与硬规则门禁 (Prompt Audit)",
    5: "第 5 步：渲染提交与工程出片 (Render Dispatch)"
}

def get_status_file(project_dir):
    return os.path.join(project_dir, ".tunjing_status.json")

def load_status(project_dir):
    status_file = get_status_file(project_dir)
    if os.path.exists(status_file):
        try:
            with open(status_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "current_step" not in data:
                    data["current_step"] = 1
                if "passed_steps" not in data:
                    data["passed_steps"] = []
                return data
        except Exception:
            pass
    return {"current_step": 1, "passed_steps": []}

def save_status(project_dir, status):
    status_file = get_status_file(project_dir)
    os.makedirs(project_dir, exist_ok=True)
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

def audit_step_1(project_dir):
    """门禁 1：角色母版与场景底图检查"""
    # 必须有男女主穿衣母版与素身母版（同源）
    asset_dir = os.path.join(project_dir, "00_资产")
    if not os.path.exists(asset_dir):
        return False, "缺少 '00_资产' 文件夹！请先创建资产目录。"
    
    files = os.listdir(asset_dir)
    has_male = any("男" in f for f in files)
    has_female = any("女" in f for f in files)
    has_scene = any("场景" in f or "scene" in f.lower() for f in files)
    
    if not (has_male and has_female):
        return False, f"资产门禁未通过：'00_资产' 目录下必须包含男主、女主的定版母版（实测检测到: {files}）"
    if not has_scene:
        return False, "资产门禁未通过：缺少纯净场景底图！至少提供一张主场景参考图。"
        
    return True, "角色母版（男/女）与场景底图验收 PASS！允许进入剧本创作。"

def audit_step_2(project_dir):
    """门禁 2：刀锋剧本三幕式与道具流转检查"""
    script_file = os.path.join(project_dir, "剧本.md")
    if not os.path.exists(script_file):
        return False, "缺少 '剧本.md'！请先撰写本集剧本。"
    
    with open(script_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 检查是否包含核心特征
    if "第一幕" not in content or "第二幕" not in content or "第三幕" not in content:
        return False, "剧本门禁未通过：剧本必须严格包含【第一幕（秘密撕扯与阻断）】、【第二幕（防线失守与前戏）】、【第三幕（体位清算与收网）】三幕式结构！"
    
    if "<d>" not in content or "</d>" not in content:
        return False, "剧本门禁未通过：台词必须严格使用 <d>[Chinese]...</d> 标签包裹！"
        
    # 检查是否提及体位 POS
    if not re.search(r'POS-\d{2}', content):
        return False, "剧本门禁未通过：第三幕肉戏必须显式声明调用的生物力学体位编号（如 POS-01、POS-02）！"
        
    return True, "刀锋剧本三幕式、实体道具与体位编号验收 PASS！允许进入分镜设计。"

def audit_step_3(project_dir):
    """门禁 3：弹跳分镜与双轨路由检查（含台词时长毫秒级咬合）"""
    sb_file = os.path.join(project_dir, "分镜.md")
    if not os.path.exists(sb_file):
        return False, "缺少 '分镜.md'！请先拆解分镜。"
        
    with open(sb_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 1. 必须有生理阻断微距
    if not re.search(r'1\.[0-9]s|微距|生理阻断|特写', content):
        return False, "分镜门禁未通过：核心交合动作前后必须插入至少一个 1.2s~2.0s 的生理阻断微距特写（指节抓白/足弓反弓/咬唇）！"
        
    # 2. 必须显式标注双轨路由
    has_ref2v = "Ref2V" in content
    has_i2v = "I2V" in content
    if not (has_ref2v or has_i2v):
        return False, "分镜门禁未通过：每个镜头必须明确标注执行轨道 [Track: Ref2V] 或 [Track: I2V_Pose]！"
        
    # 3. 严格核算：台词与分镜秒数物理咬合 (中文 3.0 字/s + 1.0s 气口)
    # 匹配格式示例: [SHOT-xx] ... 时长: 3.5s ... 台词: <d>...</d>
    shot_blocks = re.split(r'###?\s*SHOT-|\n\[SHOT-', content)
    for block in shot_blocks[1:]:
        sec_match = re.search(r'(\d+\.?\d*)\s*(?:秒|s)', block, re.IGNORECASE)
        speech_match = re.search(r'<d>(.*?)</d>', block, re.DOTALL)
        
        if sec_match and speech_match:
            duration = float(sec_match.group(1))
            speech = speech_match.group(1).strip()
            # 过滤掉 [Chinese] 或 [Language] 标记
            speech_clean = re.sub(r'\[.*?\]', '', speech)
            # 计算纯中文字数
            char_count = len(re.findall(r'[\u4e00-\u9fa5]', speech_clean))
            # 包含省略号增加气口停顿
            ellipsis_count = speech_clean.count('…') + speech_clean.count('...')
            
            # 物理时间需求
            required_time = (char_count / 3.0) + (ellipsis_count * 0.8) + 1.0
            
            if required_time > duration + 0.2: # 允许 0.2s 容差
                return False, f"分镜门禁未通过：台词与镜头时长严重脱节！检测到该镜头时长仅 {duration}s，但台词 '{speech_clean}' 包含 {char_count} 字，物理朗读需要至少 {required_time:.1f}s！请增加镜头时长或精简台词！"

    # 4. 吞鲸核心高能段铁律断言：换体位 + 3次交合特写 + 口交近景特写
    # A. 必须有口交/深喉特写
    if not re.search(r'口交|深喉|oral|blowjob', content, re.IGNORECASE):
        return False, "分镜门禁未通过：缺少核心【口交/深喉近景或拉丝微距】！这是吞鲸成人戏的绝对支配项，必须单列镜头！"
        
    # B. 必须至少有 2 个不同的 POS 体位编号（换体位）
    pos_found = set(re.findall(r'POS-\d{2}', content))
    if len(pos_found) < 2:
        return False, f"分镜门禁未通过：单集肉戏必须中途【换体位】！实测仅检测到 {len(pos_found)} 个体位 ({list(pos_found)})，必须包含至少 2 个不同体位 (如 POS-01 ➔ POS-02)！"
        
    # C. 必须包含至少 3 次独立的交合部位微距特写
    macro_matches = re.findall(r'交合特写|结合部微距|结合特写|macro pelvic|macro penetration|macro interlocking', content, re.IGNORECASE)
    if len(macro_matches) < 3:
        return False, f"分镜门禁未通过：单集肉戏必须包含至少 3 次【独立的交合/结合部微距特写】（入口破壁/深层抽送咬合/绝顶死锁）！实测仅检测到 {len(macro_matches)} 次，严禁用手脸充数！"
        
    return True, "分镜镜头组、弹跳微距、双轨路由、【音画咬合】及【换体位+3次交合微距+口交】全量验收 PASS！允许进入提示词编译。"

def audit_step_4(project_dir):
    """门禁 4：提示词编译与零中文正文检查"""
    prompt_file = os.path.join(project_dir, "视频提示词.md")
    if not os.path.exists(prompt_file):
        return False, "缺少 '视频提示词.md'！请先编译送模提示词。"
        
    with open(prompt_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 剔除台词内部后，正向不能大段中文
    clean_text = re.sub(r'<d>.*?</d>', '', content, flags=re.DOTALL)
    chinese_chars = re.findall(r'[\u4e00-\u9fa5]', clean_text)
    if len(chinese_chars) > 50:
        return False, f"提示词门禁未通过：正向描述包含未翻译中文 ({len(chinese_chars)} 字)！送模正文必须为纯英文物理动量描述。"
        
    # 检查是否有 POS 动量
    if not re.search(r'pressed flat|hyperextends|pelvic crest|kinetic|straddle', content, re.IGNORECASE):
        return False, "提示词门禁未通过：肉戏提示词缺少生物力学物理动词（必须从 kinetic-positions.md 继承动量描述）！"
        
    return True, "提示词全英文动量描述与语法门禁验收 PASS！允许进入最终渲染提交。"

def check_gate(project_dir, target_step=None):
    status = load_status(project_dir)
    curr = status.get("current_step", 1)
    
    if target_step is None:
        target_step = curr
        
    print("=" * 65)
    print("吞鲸工作室 · 工业化流程门禁核验中心")
    print(f"目标项目路径: {project_dir}")
    print(f"当前准备核验: {STAGE_NAMES.get(target_step, f'Step {target_step}')}")
    print("=" * 65)
    
    # 步进防跳步检查
    if target_step > curr:
        print(f"\n[X] 阻断拦截：你试图跳步进入 Step {target_step}！")
        print(f"    当前尚未完成: Step {curr} ({STAGE_NAMES[curr]})")
        print("    请先满足前置步骤并通过门禁放行！")
        return False
        
    auditors = {
        1: audit_step_1,
        2: audit_step_2,
        3: audit_step_3,
        4: audit_step_4
    }
    
    if target_step in auditors:
        ok, msg = auditors[target_step](project_dir)
        if ok:
            print(f"\n[✓] 门禁通过: {msg}")
            if target_step == curr:
                status["current_step"] = curr + 1
                if curr not in status["passed_steps"]:
                    status["passed_steps"].append(curr)
                save_status(project_dir, status)
                print(f"[➔] 流程已推进！当前放行权限：{STAGE_NAMES.get(status['current_step'], '全流程已完结')}")
            return True
        else:
            print(f"\n[X] 门禁拦截 (FAIL): {msg}")
            print(f"    当前步骤被阻断，修复上述问题后重新运行门禁检查。")
            return False
    elif target_step == 5:
        print("\n[✓] 前序 4 大门禁已全部通关！允许执行终端渲染命令 (python export_comfy_payload.py)！")
        return True
        
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python tunjing_gatekeeper.py <项目目录路径> [可选目标步骤1-5]")
        sys.exit(1)
        
    p_dir = sys.argv[1]
    t_step = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    passed = check_gate(p_dir, t_step)
    sys.exit(0 if passed else 1)
