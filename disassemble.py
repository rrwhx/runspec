#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

# 配置交叉工具链路径
CROSS_ROOT = Path("~/cross-gcc").expanduser()

OBJDUMP_MAP = {
    "aarch64": CROSS_ROOT / "cross-aarch64-linux-gnu/bin/aarch64-linux-gnu-objdump",
    "riscv64": CROSS_ROOT / "cross-riscv64-linux-gnu/bin/riscv64-linux-gnu-objdump",
    "x86_64": "objdump",  # 使用系统自带 objdump
}

def get_arch_from_dirname(dirname: str):
    if dirname.startswith("_base.aarch64"):
        return "aarch64"
    elif dirname.startswith("_base.riscv64"):
        return "riscv64"
    elif dirname.startswith("_base.x86_64"):
        return "x86_64"
    else:
        return None

def is_executable_file(filepath: Path):
    return filepath.is_file() and os.access(filepath, os.X_OK)

def run_objdump(objdump_path, binary_path, output_file, with_source=False):
    flag = "-S" if with_source else "-d"
    cmd = [str(objdump_path), flag, "--disassemble", str(binary_path)]
    try:
        with open(output_file, "w") as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)
        print(f"  -> {output_file.name}")
    except subprocess.CalledProcessError as e:
        print(f"  !! Failed: {binary_path.name} ({e.stderr.decode().strip()})", file=sys.stderr)
    except FileNotFoundError:
        print(f"  !! objdump not found: {objdump_path}", file=sys.stderr)

def main():
    current_dir = Path(".")
    base_dirs = [d for d in current_dir.iterdir() if d.is_dir() and d.name.startswith("_base.")]

    if not base_dirs:
        print("No _base.* directories found.")
        return

    for base_dir in sorted(base_dirs):
        arch = get_arch_from_dirname(base_dir.name)
        if arch is None:
            print(f"Skipping (unknown arch): {base_dir.name}")
            continue

        objdump_tool = OBJDUMP_MAP.get(arch)
        if isinstance(objdump_tool, Path) and not objdump_tool.exists():
            print(f"Warning: objdump for {arch} missing, skipping {base_dir.name}")
            continue

        # 定义输出目录
        asm_dir = current_dir / f"{base_dir.name}.asm"
        asm_source_dir = current_dir / f"{base_dir.name}.asm.source"

        # 创建输出目录
        asm_dir.mkdir(exist_ok=True)
        asm_source_dir.mkdir(exist_ok=True)

        print(f"Processing: {base_dir.name} → {arch}")
        executables = [f for f in base_dir.iterdir() if is_executable_file(f)]

        if not executables:
            print(f"  (no executables found)")
            continue

        for exe in executables:
            print(f"  Disassembling: {exe.name}")
            # 无源码版本 → .asm 目录
            run_objdump(objdump_tool, exe, asm_dir / f"{exe.name}.asm", with_source=False)
            # 带源码版本 → .asm.source 目录
            run_objdump(objdump_tool, exe, asm_source_dir / f"{exe.name}.asm.source", with_source=True)

    print("\n✅ Done. Generated .asm and .asm.source directories.")

if __name__ == "__main__":
    main()

