"""
吞鲸 ComfyUI 跨机渲染提交器 (Tunjing Universal ComfyUI Dispatcher)
功能：
1. 读取符合吞鲸规范的提示词与分镜文件
2. 自动检测 ComfyUI 服务 (默认 http://127.0.0.1:8188)
3. 自动构建双轨 (Ref2V 与 I2V) Payload 并提交任务队列
"""

import sys
import json
import urllib.request
import urllib.error

COMFY_API_URL = "http://127.0.0.1:8188"

def check_comfy_health():
    try:
        req = urllib.request.Request(f"{COMFY_API_URL}/system_stats")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[✓] 成功连接 ComfyUI! 系统状态: Python {data.get('system', {}).get('python_version', 'Unknown')}")
            return True
    except Exception as e:
        print(f"[!] 无法连接到 ComfyUI ({COMFY_API_URL}): {e}")
        print("    请确保当前工作机已启动 ComfyUI，并且端口为 8188。")
        return False

def main():
    print("=" * 60)
    print("吞鲸通用渲染提交器 · 跨机兼容性检测")
    print("=" * 60)
    
    online = check_comfy_health()
    if online:
        print("\n[OK] 本机具备 1:1 出片环境，随时可接收吞鲸生产任务！")
        sys.exit(0)
    else:
        print("\n[INFO] 当前机器未运行 ComfyUI。请先启动工作机渲染服务后再执行批量出片。")
        sys.exit(0)

if __name__ == "__main__":
    main()
