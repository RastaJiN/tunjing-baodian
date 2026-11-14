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
3: "第 3 步：弹跳分镜与节拍呼吸 (Bounce Storyboard)",
4: "第 4 步：纯血Ref2V提示词编译 (Prompt Audit)",
5: "第 5 步：生成前自我终极审核 (Pre-Render Self-Audit)",
6: "第 6 步：渲染提交与工程出片 (Render Dispatch)"
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
    has_male = any(("男" in f or "male" in f.lower()) for f in files)
    has_female = any(("女" in f or "female" in f.lower()) for f in files)
    has_scene = any(("场景" in f or "scene" in f.lower() or "room" in f.lower() or "corridor" in f.lower()) for f in files)
    
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
    if "第一幕" not in content or "第二幕" not in content:
        return False, "剧本门禁未通过：剧本必须包含清晰的幕次结构（至少具备【第一幕】与【第二幕】）！"
    
    if "<d>" not in content or "</d>" not in content:
        return False, "剧本门禁未通过：台词必须严格使用 <d>[Chinese]...</d> 标签包裹！"

    # 去AI味翻译腔与书面套话拦截
    cliche_hits = re.findall(r"(你怎么能如此|我的心好痛|充满了不可思议|眼中闪过一丝|嘴角勾起一抹弧度|三分薄凉|既然你如此无情|休怪我无义)", content)
    if cliche_hits:
        return False, f"剧本门禁未通过：[AI腔台词拦截] 检测到书面套话/翻译腔 {sorted(set(cliche_hits))}！请改为 12 字以内的口语化狠话或潜台词短句。"
        
    # 检查是否提及体位（吞鲸 v3.0 标准 55 套原生 pose id）
    KNOWN_IDS = {'fix_attire', 'loosen_tie', 'chin_lift', 'lap_sit', 'titjob', 'cut_insert', 'spatial_shift', 'stand_doggy_wall', 'undress', 'squat_bj', 'clutch_fabric', 'chest_push', 'cunnilingus', 'lip_thumb_wipe', 'tip_lick', 'prop_insert', 'nape_grip', 'breast_rub', 'mirror_ear_whisper', 'stand_face_hug', 'cowgirl', 'prone_bj', 'squirting_climax', 'collapse_sob', 'facesit', 'shoulder_strap_slide', 'facefuck', 'trace_collar', 'floor_missionary', 'deepthroat', 'sixty_nine', 'fingering', 'penis_slap', 'squat_cowgirl', 'doggy', 'blocking_2s', 'stand_bend_doggy', 'tie_pull_seduce', 'reverse_cowgirl', 'srs_female', 'neck_nuzzle_inhale', 'nipple_lick', 'ear_whisper_tease', 'kiss_pin', 'footjob', 'kiss_fondle', 'pov_insert', 'cum_belly', 'side_spoon', 'wall_caging', 'face_insert', 'finger_interlock_pin', 'bedside_stand', 'cum_face', 'srs_male', 'thigh_grind', 'bj', 'cum_butt', 'leg_brush_tease', 'kiss_force', 'solo_masturbate', 'cum_chest', 'creampie', 'turn_evade', 'waist_pull_collision', 'step_back_guard', 'ball_lick', 'cowgirl_upright', 'table_doggy', 'outro_solo', 'lap_sit_back', 'ass_rub', 'missionary_legup', 'env_establish', 'sofa_cunni', 'kiss_her', 'head_thrust', 'carry_insert', 'wrist_pin', 'back_arch_lean', 'present_item', 'grab_lapel', 'side_face', 'missionary', 'anal', 'handjob', 'rub_temple'}
    # 反作弊锁 5：严禁将英文代码箭头 (pose_a -> pose_b) 粗暴塞入 Markdown 标题行充数！
    heading_cheat = re.findall(r'^#{1,4}\s+.*?\([a-z_]+\s*->\s*[a-z_]+.*\)', content, re.MULTILINE)
    if heading_cheat:
        return False, f"剧本门禁未通过：[反作弊拦截·标题塞代码作弊] 检测到标题行被强行塞入代码括号 {heading_cheat[:2]}！请保持标题纯净中文文学性。"

    # 支持自然中文动作描述或标准 ID 识别（无需为迎合正则污染剧本标题）
    ZH_ACTION_KEYWORDS = re.findall(r'(站立按墙|按墙后入|后入|跪姿口交|口交|深喉|传教士|正面交合|观音坐莲|女上位|骑乘|侧卧|指插|自慰|潮吹|高潮|捏下巴|壁咚|递卡|房卡)', content)
    ids_in_script = set(re.findall(r'\b([a-z][a-z_]{1,24})\b', content)) & KNOWN_IDS
    if not ids_in_script and len(set(ZH_ACTION_KEYWORDS)) < 2:
        return False, "剧本门禁未通过：剧本必须包含至少 2 处明确的阶段性动作/体位推进描述（支持自然中文如“站立按墙/口交/观音坐莲/正面交合”或吞鲸标准 ID）！"
        
    detected_desc = sorted(ids_in_script) if ids_in_script else sorted(set(ZH_ACTION_KEYWORDS))
    return True, f"刀锋剧本结构、活人感台词与动作演进 ({detected_desc[:6]}) 验收 PASS！允许进入分镜设计。"

def audit_step_3(project_dir):
    """门禁 3：拆镜密度、景别机位与纯血单轨路由检查（含台词时长毫秒级咬合）"""
    sb_file = os.path.join(project_dir, "分镜.md")
    if not os.path.exists(sb_file):
        return False, "缺少 '分镜.md'！请先拆解分镜。"
        
    with open(sb_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 1. 必须有生理阻断微距
    if not re.search(r'1\.[0-9]s|微距|生理阻断|特写', content):
        return False, "分镜门禁未通过：核心交合动作前后必须插入至少一个 1.2s~2.0s 的生理阻断微距特写（指节抓白/足弓反弓/咬唇）！"
        
    # 2. 检查纯血 Ref2V 轨道标注
    if "Ref2V" not in content:
        return False, "分镜门禁未通过：全片必须统一采用纯血 Ref2V 轨道 [Track: Ref2V]！"
        
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

    # 4. 吞鲸高能段三级戏份分档检测逻辑（含口交戏 / 独处自慰戏 / 纯插入交合戏）
    KNOWN_IDS = {'fix_attire', 'loosen_tie', 'chin_lift', 'lap_sit', 'titjob', 'cut_insert', 'spatial_shift', 'stand_doggy_wall', 'undress', 'squat_bj', 'clutch_fabric', 'chest_push', 'cunnilingus', 'lip_thumb_wipe', 'tip_lick', 'prop_insert', 'nape_grip', 'breast_rub', 'mirror_ear_whisper', 'stand_face_hug', 'cowgirl', 'prone_bj', 'squirting_climax', 'collapse_sob', 'facesit', 'shoulder_strap_slide', 'facefuck', 'trace_collar', 'floor_missionary', 'deepthroat', 'sixty_nine', 'fingering', 'penis_slap', 'squat_cowgirl', 'doggy', 'blocking_2s', 'stand_bend_doggy', 'tie_pull_seduce', 'reverse_cowgirl', 'srs_female', 'neck_nuzzle_inhale', 'nipple_lick', 'ear_whisper_tease', 'kiss_pin', 'footjob', 'kiss_fondle', 'pov_insert', 'cum_belly', 'side_spoon', 'wall_caging', 'face_insert', 'finger_interlock_pin', 'bedside_stand', 'cum_face', 'srs_male', 'thigh_grind', 'bj', 'cum_butt', 'leg_brush_tease', 'kiss_force', 'solo_masturbate', 'cum_chest', 'creampie', 'turn_evade', 'waist_pull_collision', 'step_back_guard', 'ball_lick', 'cowgirl_upright', 'table_doggy', 'outro_solo', 'lap_sit_back', 'ass_rub', 'missionary_legup', 'env_establish', 'sofa_cunni', 'kiss_her', 'head_thrust', 'carry_insert', 'wrist_pin', 'back_arch_lean', 'present_item', 'grab_lapel', 'side_face', 'missionary', 'anal', 'handjob', 'rub_temple'}
    ORAL_SET = {"bj","squat_bj","prone_bj","deepthroat","head_thrust","facefuck","sixty_nine","tip_lick","ball_lick","penis_slap"}
    SOLO_SET = {"solo_masturbate","fingering","clit_tease"}

    all_poses = set(re.findall(r'\b([a-z][a-z_]{1,24})\b', content)) & KNOWN_IDS
    has_oral_pose = bool(all_poses & ORAL_SET)
    is_solo_only = bool(all_poses) and all_poses.issubset(SOLO_SET | {"undress", "breast_rub", "squirting_climax"})

    if has_oral_pose:
        if not re.search(r'口交|深喉|oral|blowjob|bj|deepthroat|facefuck', content, re.IGNORECASE):
            return False, "分镜门禁未通过：本集包含口爱动作，必须明确标注【口交/深喉近景特写】！"
    elif is_solo_only:
        if not re.search(r'微距|特写|macro|cu', content, re.IGNORECASE):
            return False, "分镜门禁未通过：独处戏份必须包含指节/湿润微距特写！"
    else:
        if len(all_poses) < 2:
            return False, (f"分镜门禁未通过：双人高能戏必须中途【换体位】！"
                           f"实测仅检测到 {len(all_poses)} 个姿势，必须包含至少 2 个不同吞鲸标准姿势！")

    if not is_solo_only:
        if len(all_poses) < 2:
            return False, (f"分镜门禁未通过：单集肉戏必须中途【换体位】！"
                           f"实测仅检测到 {len(all_poses)} 个姿势，必须包含至少 2 个不同吞鲸标准姿势！")
        macro_matches = re.findall(r'交合特写|结合部微距|结合特写|macro pelvic|macro penetration|macro interlocking', content, re.IGNORECASE)
        if len(macro_matches) < 3:
            return False, f"分镜门禁未通过：双人高能戏必须包含至少 3 次【独立的交合/结合部微距特写】！实测仅检测到 {len(macro_matches)} 次！"

        # 反作弊锁 2：核验每个标注【交合特写/结合部微距】的镜头块是否名实相符（景别必须为 hip/macro，严禁在 mcu/wide/cu 镜头上硬贴假标签凑数！）
        for blk in shot_blocks[1:]:
            if re.search(r'交合特写|结合部微距', blk):
                if not re.search(r'\b(hip|macro)\b|腰胯特写|微距', blk, re.IGNORECASE):
                    return False, "分镜门禁未通过：[反作弊拦截·假特写标签] 检测到某镜头贴了【交合特写/结合部微距】标签，但该镜景别并非 hip/macro！严禁用脚本机械贴标签凑数！"

    # D. 【拆镜密度门禁】逐镜必须有景别 + 机位，且镜头密度符合硬件上限
    shot_marks = re.findall(r'(?:^|\n)\s*(?:###?\s*)?\[?SHOT[\s\-]?\d+', content, re.IGNORECASE)
    shot_count = len(shot_marks)
    if shot_count == 0:
        return False, ("分镜门禁未通过：未检测到任何 [SHOT-N / ### SHOT N] 镜头标记！"
                       "必须逐镜拆解，每镜独立成条。")

    # 景别必须逐镜出现（mcu/cu/macro/hip/face/wide 或中文景别词）
    size_hits = len(re.findall(r'\b(?:wide|mcu|cu|macro|hip|face)\b|中景|中近景|近景|微距|腰胯特写|面部特写', content))
    if size_hits < shot_count * 0.8:
        return False, (f"分镜门禁未通过：【景别标注缺失】！检测到 {shot_count} 个镜头，"
                       f"但仅 {size_hits} 处景别标注。逐镜必须标明景别"
                       f"（wide/mcu/cu/macro/hip/face 或中景/中近景/近景/微距/腰胯特写/面部特写）！")

    # 机位必须逐镜出现
    cam_hits = len(re.findall(r'push_tension|pull_reveal|tilt_up_desire|tilt_down_impact|ots_depth|arc_subtle|handheld_breath|low_upward|high_downward|static_side|static_rear|static_front|low_hip|ots|high_angle|slow_push|follow_soft|固定|侧机位|后侧|低机位|过肩|俯|仰|推|拉|摇|手持', content))
    if cam_hits < shot_count * 0.8:
        return False, (f"分镜门禁未通过：【机位标注缺失】！检测到 {shot_count} 个镜头，"
                       f"但仅 {cam_hits} 处机位标注。逐镜必须标明机位"
                       f"（static_side/static_rear/low_hip/ots/high_angle 等）！")

    # 镜头密度：从时长反推，平均单镜不得超过 8 秒（硬件上限）
    durations = [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*(?:秒|s)\b', content)]
    if durations and shot_count:
        avg = sum(d for d in durations if d <= 30) / max(1, len([d for d in durations if d <= 30]))
        if avg > 8.0:
            return False, (f"分镜门禁未通过：【镜头过长，违反硬件上限】！"
                           f"平均单镜 {avg:.1f}s，超过 8s 上限。"
                           f"2 分钟床戏应拆成 20~30 个 2~6s 短镜，严禁把多个体位压进一镜！")
        
    # ── 肉戏骨架契约 (Sex Scene Skeleton Contract)：骨头里的公式，硬死锁 ──
    # 只要本集含肉戏体位（非纯文戏调度），以下四条缺一即熔断，是「好肉戏」的结构完整性下限。
    # 1) 每场肉戏 ≥1 次体位交换；2) 分镜 ≥3 次交合特写；3) 穿插男女主表情反馈反打；4) 全程呻吟/声音反馈。
    sex_staging = {"env_establish", "blocking_2s", "prop_insert", "cut_insert", "spatial_shift", "outro_solo",
                   "srs_male", "srs_female", "present_item"}
    sex_poses = all_poses - sex_staging
    if sex_poses:
        # 1) 体位交换：肉戏姿势 ≥2 个（前面已有 len(all_poses)<2 拦截，这里对纯肉戏姿势再锁一次）
        if len(sex_poses) < 2:
            return False, (f"分镜门禁未通过：【肉戏公式·体位交换缺失】本集肉戏仅 {len(sex_poses)} 个体位 "
                           f"({sorted(sex_poses)})，一场肉戏必须至少交换 1 次体位（≥2 个不同交合/口交/前戏姿势）！")
        # 2) 交合特写 ≥3 次：前面 macro_matches<3 已拦，这里语义明确为肉戏公式
        # 3) 表情反馈穿插：肉戏必须穿插正反打表情反打 (srs_female/srs_male 或 face 景别表情镜)
        reaction_hits = re.findall(r'srs_female|srs_male|表情|面部特写|face', content, re.IGNORECASE)
        if len(reaction_hits) < 2:
            return False, "分镜门禁未通过：【肉戏公式·表情反馈缺失】肉戏必须穿插女主/男主的表情反馈反打（srs_female/srs_male 正反打或面部特写），不能全程只看交合处！"
        # 4) 全程呻吟/声音反馈：肉戏声场必须含呻吟/浪叫/粗喘等声音反馈（audio/声场/呻吟标注）
        moan_hits = re.findall(r'呻吟|浪叫|粗喘|喘息|娇喘|气声|audio|呻吟|声场|音效|overall_soundscape|soundscape', content, re.IGNORECASE)
        if not moan_hits:
            return False, "分镜门禁未通过：【肉戏公式·声音反馈缺失】肉戏全程必须有女主呻吟/浪叫或男主粗喘等声音反馈标注（声场/音效/呻吟），不能全程无声！"

    return True, "分镜【拆镜密度 + 逐镜景别机位 + 纯血Ref2V单轨 + 音画咬合 + 换体位与3次交合微距 + 肉戏公式死锁】全量验收 PASS！允许进入提示词编译。"

def audit_step_4(project_dir):
    """门禁 4：吞鲸标准六段式提示词结构与正向压油核验"""
    prompt_file = os.path.join(project_dir, "视频提示词.md")
    if not os.path.exists(prompt_file):
        return False, "缺少 '视频提示词.md'！请先编译送模提示词。"
        
    with open(prompt_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 1. 检查吞鲸引擎 吞鲸六段式标准装配器 六段式必填结构锚点 (v3.0 原厂 Full-Reference 规范)
    required_blocks = [
        (["Goal & Audio Contract:", "Goal: Generate"], "缺少 [1] Goal 目标与时长画幅声明"),
        (["Audio rule:", "Audio rule"], "缺少 [1] Audio rule 台词与静音纪律声明"),
        (["subject_definitions:", "Reference map"], "缺少 [2] 实体与场景槽位映射 (subject_definitions 或 Reference map)"),
        (["Consistency:", "Consistency"], "缺少 [3] Consistency 身份与场景一致性死锁"),
        (["Motion quality", "Motion quality (Anti-Stiffness)"], "缺少 [3] Motion quality 防僵硬二次动作锁"),
        (["MOTION FLOOR:", "Motion quality"], "缺少 [3b] MOTION FLOOR 底噪生命力锁"),
        (["integrated_multimodal_description:", "detailed_description:"], "缺少 [5] 逐镜时间线主体 (integrated_multimodal_description 或 detailed_description)"),
        (["overall_soundscape:", "overall_soundscape"], "缺少 [6] overall_soundscape 环境底噪与动作声场"),
    ]
    for markers, err_msg in required_blocks:
        if isinstance(markers, str): markers = [markers]
        if not any(m in content for m in markers):
            return False, f"提示词门禁未通过：{err_msg}（必须严格遵循吞鲸标准六段式结构）！"
            
    # 2. 检查正向肯定句压油（工作流 Node 328 零化负向，必须靠正向压油）
    if not re.search(r'matte velvet skin finish|powdered dry|visible fine pores', content, re.IGNORECASE):
        return False, "提示词门禁未通过：缺少【吞鲸正向肯定句压油词】（authentic matte velvet skin finish, powdered dry texture）！工作流负向通道已零化，必须正向压油！"
        
    # 3. 检查是否误入毒性油光词（采用负向前瞻正则，精准放行 non-greasy / without surface shine 等正向去油描述）
    toxic_oil_match = re.search(r'(?<!non-)(?<!no )(?<!without )\b(sweat sheen|oily face|shiny plastic|vaseline skin|dewy glisten|greasy|glossy|glistening)\b', content, re.IGNORECASE)
    if toxic_oil_match:
        return False, f"提示词门禁未通过：检测到诱发油光蜡感的毒性词 '{toxic_oil_match.group(0)}'！请立即剔除。"

    # 3b. 拦截机械替换产生的反物理荒谬词汇
    absurd_phrases = ['matte bodily fluids', 'dry squirting', 'powdered saliva', 'matte semen', 'matte lubrication']
    for ap in absurd_phrases:
        if ap in content.lower():
            return False, f"提示词门禁未通过：检测到反物理常识的错误替换词 '{ap}'！去油仅针对皮肤表层，严禁将生理体液替换为哑光或干燥。"

    # 3c. 送模代码块全文本 0 汉字盲检（剥离 <d>...</d> 后，正向 Prompt 严禁残留任何汉字防字幕烫印）
    code_blocks = re.findall(r'```(?:text)?\s*(.*?)```', content, re.DOTALL)
    for idx_cb, cb in enumerate(code_blocks, 1):
        if "=== NEGATIVE ===" in cb:
            return False, f"提示词门禁未通过：第 {idx_cb} 镜送模代码块内混入了 '=== NEGATIVE ===' 段落！Node 263 正向提示词必须 100% 剥离负面清单（防反向注意力画字幕）！"
        sub_trig = re.findall(r'\b(subtitles?|captions?|on-screen text|burn-in text|text ban)\b', cb, re.IGNORECASE)
        if sub_trig:
            return False, f"提示词门禁未通过：第 {idx_cb} 镜正向文本含有字幕反向诱导词 {sorted(set(sub_trig))}！严禁在正向写 NO SUBTITLES/CAPTIONS！"
        if re.search(r'says:\s*\n\s*<d>', cb, re.IGNORECASE):
            return False, f"提示词门禁未通过：第 {idx_cb} 镜将 'says:' 与 '<d>' 拆成了两行（SRT字幕格式诱导）！必须同行写为 'says: <d>[Chinese]...</d>'！"
        # 【字幕死锁 1 · 说话人真人名熔断】speaker 只认引擎原生命名女子A/男子A，含真人名必触发性别熔断
        #   → 判画外音 + 强制闭唇 → 嘴不能动 → 模型把台词汉字画成画面字幕。这是字幕烫印的物理根因之一，代码层焊死。
        real_name_hits = re.findall(r'(唐曼|陆骁|沈峥|许宁)', cb)
        if real_name_hits:
            return False, f"提示词门禁未通过：第 {idx_cb} 镜说话人声明夹带了真人名 {sorted(set(real_name_hits))}！speaker 只能写 '女子A'/'男子A'（或 <Subject 1>/<Subject 2>），严禁传唐曼/陆骁等真人名——真人名不含性别字，会触发引擎性别熔断，导致画外音+闭唇锁，嘴不能动就把台词画成字幕！"
        # 【字幕死锁 2 · 台词必须有说话人口型锚点】每条真实台词 <d>[Chinese]…</d> 前必须紧跟 <Subject N> says / 女子A说 的口型声明
        #   没有锚点，模型不清楚这句话是谁在开口，就会在画面里另起一行把它画出来当字幕。
        #   正确格式：'...<Subject 1> (S1) says: <d>[Chinese]台词</d> while ...'（says: 与 <d> 同行紧接）
        #   注意：只查 <d>[Chinese]…</d> 真实台词；跳过 header 里的文法示例 <d>...</d>（那是教 H3 语法，不含 [Chinese]）。
        for dd in re.findall(r'<d>\[Chinese\].*?</d>', cb, re.DOTALL):
            dd_ctx = cb[max(0, cb.find(dd) - 120):cb.find(dd)]
            # 锚点判定：<d> 前 120 字符内存在「说话人标记 + 说话动词 + 冒号」且 says: 与 <d> 紧跟同行
            has_anchor = re.search(r'(?:<subject\s*\d+>\s*\(?s\d+\)?|女子a|男子a|subject\s*\d+)\s*.*?(?:says|speaks|whispers|gasps|moans|murmurs)\s*:\s*$', dd_ctx, re.IGNORECASE)
            if not has_anchor:
                return False, f"提示词门禁未通过：第 {idx_cb} 镜存在一句真实台词 '<d>[Chinese]…</d>' 前方无说话人口型锚点（<Subject N> says / 女子A说，且 says: 与 <d> 同行）！无锚点的台词会被模型当作字幕画进画面，必须每条台词紧跟同行说话人声明。"
        if re.findall(r'(?:,\s*,+|,\s*\.|;\s*,)', cb):
            return False, f"提示词门禁未通过：[反作弊拦截·正则阉割残骸] 第 {idx_cb} 镜检测到 ', ,' 或 ', .' 破碎标点语法！严禁用粗暴 re.sub 挖词糊弄门禁！"
        pos_part = cb.split("=== NEGATIVE ===")[0]
        pos_no_d = re.sub(r'<d>.*?</d>', '', pos_part, flags=re.DOTALL)
        zh_chars = re.findall(r'[\u4e00-\u9fff]+', pos_no_d)
        if zh_chars:
            return False, f"提示词门禁未通过：第 {idx_cb} 个镜头的正向送模文本（<d>标签外）检测到中文汉字残留 {zh_chars[:5]}！这会导致视觉编码器在画面底部烫印中文字幕！"
        if re.search(r'(?:^|\n)\s*###\s+|////', pos_part):
            return False, f"提示词门禁未通过：第 {idx_cb} 个镜头的正向送模文本混入了未截断的 Markdown 标记（### 或 ////）！"

    # 4. 画外音与内心独白 (OS/Voiceover) 绝对防对口型死锁检查（对齐官方 BASE-EN §4.4 公式）
    if re.search(r'says in an off-screen voiceover|voiceover|monologue|\bOS\b', content, re.IGNORECASE):
        mouth_lock_patterns = [
            r'lips remain completely closed',
            r'bite[s]? down on',
            r'jaw completely clamped',
            r'lips are pressed into',
            r'sealed around',
            r'oral cavity is physically locked',
            r'lips remain parted in breathless gasps',
            r'back of her head',
            r'viewpoint is from behind'
        ]
        has_mouth_lock = any(re.search(p, content, re.IGNORECASE) for p in mouth_lock_patterns)
        if not has_mouth_lock:
            return False, "提示词门禁未通过：检测到包含画外音/内心独白(Voiceover/OS)，但未添加【嘴部物理占位死锁】！必须采用官方公式 '<Subject N> (Sx) says in an off-screen voiceover: <d>...</d> while her/his lips remain completely closed.'"
            
    return True, "提示词【吞鲸标准六段式结构 + 正向肯定句压油 + OS防对口型死锁】全量验收 PASS！允许进入生成前终审。"

def audit_step_5(project_dir):
    """门禁 5：生成前机器实测终审与 SHA-256 防伪签名核验（彻底废除手写假报告）"""
    import hashlib
    import tunjing_diff_audit as diff_mod

    batch_file = os.path.join(project_dir, "批量任务.json")
    if not os.path.exists(batch_file):
        return False, "终审门禁未通过：缺少 '批量任务.json'，无法执行机器终审签名！"

    # 自动调用 tunjing_diff_audit 进行真实盲检并签发带 SHA-256 指纹的终审报告
    rep = diff_mod.audit_project(project_dir)
    if rep.get("violations"):
        diff_mod.write_signed_audit_report(project_dir, rep)
        return False, f"终审门禁未通过：[机器盲检抓出 {len(rep['violations'])} 项真实违规] 首项: {rep['violations'][0]}"

    report_file = os.path.join(project_dir, "审查", "生成前终审报告.md")
    if not os.path.exists(report_file):
        report_file = diff_mod.write_signed_audit_report(project_dir, rep)
        diff_mod.write_producer_receipt(project_dir, rep)

    with open(report_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 校验报告中的 SHA-256 指纹是否与当前 批量任务.json 100% 匹配（拦截手写假报告或改后未重审）
    expected_sha = diff_mod.compute_batch_sha256(project_dir)
    if expected_sha not in content:
        # 自动刷新签名报告并再次校验
        report_file = diff_mod.write_signed_audit_report(project_dir, rep)
        diff_mod.write_producer_receipt(project_dir, rep)
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()
        if expected_sha not in content:
            return False, "终审门禁未通过：[反作弊拦截·伪造终审报告] 报告缺少与当前 批量任务.json 匹配的 SHA-256 机器签名指纹！严禁手写假报告！"

    if "PASS" not in content or "REJECT" in content:
        return False, "终审门禁未通过：终审报告中存在未解决的 REJECT 项或未明确标注 PASS！必须全部达标！"

    required_checks = ["资产实名与槽位", "音画台词咬合", "换体位与特写契约", "受控运镜规范", "提示词纯净度", "纯血Ref2V单轨规范"]
    missing = [c for c in required_checks if c not in content]
    if missing:
        return False, f"终审门禁未通过：终审报告缺少以下维度的审核记录: {missing}！必须六项全检！"

    return True, f"生成前六大维度机器盲检与 SHA-256 防伪签名 ({expected_sha[:12]}...) 100% PASS！正式签发放行出片！"

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
        4: audit_step_4,
        5: audit_step_5
    }
    
    if target_step in auditors:
        ok, msg = auditors[target_step](project_dir)
        if ok:
            print(f"\n[✓] 门禁通过: {msg}")
            if target_step in (2, 3):
                try:
                    import tunjing_advisor
                    adv = tunjing_advisor.diagnose_project(project_dir)
                    if adv.get("suggestions"):
                        print("\n" + "─" * 65)
                        print("💡 【鲸鲸导演主动升维顾问 (Proactive Director Advisor)】：")
                        for idx_s, sg in enumerate(adv["suggestions"], 1):
                            print(f"  {idx_s}. {sg['dimension']} -> {sg['action'].splitlines()[0]}")
                        print(f"  👉 可随时运行 `python scripts/tunjing_advisor.py '{project_dir}'` 查看完整升维方案与推荐拆镜链！")
                        print("─" * 65)
                except Exception:
                    pass
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
    elif target_step == 6:
        print("\n[✓] 前序 5 大门禁（含生成前终极自审）已全部通关！允许执行终端渲染命令 (python export_comfy_payload.py)！")
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
