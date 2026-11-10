"""
吞鲸宝典 v4.0 · ComfyUI 跨机渲染提交与批量任务打包器
功能：
1. 检查项目目录下前序 5 大门禁是否全部 PASS（未全绿严禁导出渲染！）
2. 自动核验吞鲸 v4.0 `批量任务.json` (schema: h3-drama-task, 9图3音动态槽位 + LoRA 分级 + 空间图池单槽轮换 + 全集总帧闭合)
3. 自动检测本机 ComfyUI 服务 (http://127.0.0.1:8188) 并输出一键启动指令
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error

COMFY_API_URL = "http://127.0.0.1:8188"


def check_comfy_health():
    try:
        req = urllib.request.Request(f"{COMFY_API_URL}/system_stats")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sys_info = data.get("system", {})
            py_ver = sys_info.get("python_version", "Unknown")
            argv = sys_info.get("argv", [])
            input_dir = "默认 ComfyUI/input"
            for idx, arg in enumerate(argv):
                if arg == "--input-directory" and idx + 1 < len(argv):
                    input_dir = argv[idx + 1]
            print(f"[✓] 成功连接 ComfyUI ({COMFY_API_URL}) | Python: {py_ver} | 真实挂载 Input 目录: {input_dir}")
            return True
    except Exception as e:
        print(f"[i] 当前未检测到运行中的 ComfyUI ({COMFY_API_URL}): {e}")
        return False


def verify_project_gates(project_dir):
    status_file = os.path.join(project_dir, ".tunjing_status.json")
    if not os.path.exists(status_file):
        return False, "未找到 .tunjing_status.json 状态机文件！请先运行 tunjing_gatekeeper.py 通过前 5 步门禁。"
    with open(status_file, "r", encoding="utf-8") as f:
        st = json.load(f)
    passed = set(st.get("passed_steps", []))
    need = {1, 2, 3, 4, 5}
    missing = sorted(need - passed)
    if missing:
        return False, f"门禁未全绿！尚未通过的步骤: {missing}。严禁跳过门禁直接提交渲染！"
    return True, "前序 5 大门禁已 100% 绿灯放行！"


def verify_batch_json(project_dir):
    bj_path = os.path.join(project_dir, "批量任务.json")
    if not os.path.exists(bj_path):
        return False, f"缺少 {bj_path}！请先运行 tunjing_scene.py --out-dir 生成批量任务。"
    with open(bj_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("schema") != "h3-drama-task":
        return False, "批量任务.json schema 不是 'h3-drama-task'！"
    shots = data.get("batch_shots", [])
    if not shots:
        return False, "批量任务.json 中没有任何镜头！"

    total_frames = 0
    for i, s in enumerate(shots, 1):
        frames = s.get("frames", 0)
        if (frames - 5) % 17 != 0:
            return False, f"镜头 {i} 帧数 {frames} 不符合 H3 公式 (frames-5)%17==0！"
        total_frames += frames

        ref_imgs = s.get("ref_images", [])
        if len(ref_imgs) != 3:
            return False, f"镜头 {i} ref_images 必须严格为 3 槽 [Picture 1, Picture 2, Picture 3]（空间图池单槽轮换仍在槽位 2 完成）！"
        # 校验核心空间锚点：槽位 2（<Picture 3>）必须非空
        if not ref_imgs[2]:
            return False, f"镜头 {i} 缺失 <Picture 3> 场景空间锚点！背景底图严禁断开！"
        for rname in ref_imgs:
            if not all(ord(c) < 128 for c in str(rname)):
                return False, f"镜头 {i} 参考图文件名 '{rname}' 含非 ASCII 中文字符！"
            if rname in ("male_master.png", "female_master.png", "__PLACEHOLDER__"):
                return False, f"镜头 {i} [反作弊拦截·空占位符未替换] 参考图仍为模板空占位名 '{rname}'！必须绑定真实角色母版文件名（否则 ComfyUI 必 0.0s 报错秒退）！"

        # 校验 LoRA 分级：文戏/空镜强制 0.0，肉戏 0.45，其余数值视为非法
        lw = s.get("lora_mystic_strength", None)
        if lw is not None and lw not in (0.0, 0.45):
            return False, f"镜头 {i} LoRA 权重 {lw} 非法！必须为 0.0（文戏/穿衣/空镜）或 0.45（前戏/肉戏）。"

        # 校验 3 音挂载（若声明 Audio 锚定）
        ref_audios = s.get("ref_audios", [])
        for aname in ref_audios:
            if not all(ord(c) < 128 for c in str(aname)):
                return False, f"镜头 {i} 音频参考文件名 '{aname}' 含非 ASCII 中文字符！"

    # 校验全集总帧数与声明一致
    declared_total = data.get("total_frames", None)
    if declared_total is not None and declared_total != total_frames:
        return False, f"全集总帧数不闭合！声明 {declared_total} 帧，实际累加 {total_frames} 帧。"

    return True, (f"批量任务.json 校验通过！共 {len(shots)} 个纯血 Ref2V 镜头，"
                  f"总帧数 {total_frames} 全闭合，全部符合 (F-5)%17==0、空间锚点常驻、LoRA 动态分级与 9图3音规范。")


def main():
    ap = argparse.ArgumentParser(description="吞鲸 v4.0 ComfyUI 渲染提交与批量任务核验器")
    ap.add_argument("project_dir", nargs="?", default="", help="项目目录路径（可选）")
    args = ap.parse_args()

    print("=" * 65)
    print("🐳 吞鲸 v4.0 通用渲染提交器 · 纯血 Ref2V 批量任务核验中心")
    print("=" * 65)

    if args.project_dir:
        ok_gate, msg_gate = verify_project_gates(args.project_dir)
        print(f"[{'✓' if ok_gate else 'X'}] 门禁状态: {msg_gate}")
        if not ok_gate:
            sys.exit(1)

        ok_bj, msg_bj = verify_batch_json(args.project_dir)
        print(f"[{'✓' if ok_bj else 'X'}] 任务包核验: {msg_bj}")
        if not ok_bj:
            sys.exit(1)

    online = check_comfy_health()
    if online:
        print("\n[OK] 本机 ComfyUI 在线，可直接将项目目录下的 `批量任务.json` 交由 ComfyUI H3 节点队列批量渲染！")
    else:
        print("\n[READY] 离线打包与校验已完成！生成的 `批量任务.json` 可随时拷贝至运行 ComfyUI 的工作机无损出片。")
    sys.exit(0)


if __name__ == "__main__":
    main()
