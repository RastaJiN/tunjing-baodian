import sys
import os

print("=== 🐳 吞鲸宝典引擎自检开始 ===")
skill_dir = r"C:\Users\Rasta\AppData\Local\hermes\skills\tunjing-adult-drama-engine"

files = [
    os.path.join(skill_dir, "SKILL.md"),
    os.path.join(skill_dir, "references", "kinetic-positions.md"),
    os.path.join(skill_dir, "references", "shot-design-and-bounce.md"),
    os.path.join(skill_dir, "scripts", "tunjing_compiler.py"),
]

all_ok = True
for f in files:
    if os.path.exists(f):
        print(f"[OK] {os.path.basename(f)} 存在 ({os.path.getsize(f)} bytes)")
    else:
        print(f"[FAIL] {f} 缺失！")
        all_ok = False

if all_ok:
    print("=== 吞鲸引擎所有物理组件验证 PASS ===")
    sys.exit(0)
else:
    sys.exit(1)
