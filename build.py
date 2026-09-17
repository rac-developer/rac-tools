#!/usr/bin/env python3
"""
OmniFloat - Cross-Platform Build Script
Compiles OmniFloat into a standalone, single-file executable for Windows (.exe) or Linux (ELF binary).
Requires: pyinstaller (pip install pyinstaller)
"""
import os
import sys
import subprocess
import shutil

def build():
    print("=" * 60)
    print(f"Building OmniFloat Standalone Executable on {sys.platform.upper()}")
    print("=" * 60)

    # 1. Verify PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("[Build] PyInstaller not found. Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Prepare build command
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(script_dir, "main.py")
    icon_path = os.path.join(script_dir, "assets", "icon.png")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name=OmniFloat",
        "--clean",
    ]

    # Add icon if available
    if os.path.exists(icon_path):
        cmd.extend(["--add-data", f"{icon_path}{os.pathsep}assets"])
        if sys.platform == "win32":
            # For Windows .exe icon
            cmd.extend([f"--icon={icon_path}"])

    cmd.append(main_py)

    print("[Build] Executing command:", " ".join(cmd))
    res = subprocess.call(cmd)
    if res == 0:
        print("\n" + "=" * 60)
        output_name = "OmniFloat.exe" if sys.platform == "win32" else "OmniFloat"
        dist_path = os.path.join(script_dir, "dist", output_name)
        print(f"SUCCESS: Executable created at: {dist_path}")
        print("=" * 60)
    else:
        print(f"\nERROR: Build failed with exit code {res}")
        sys.exit(res)

if __name__ == "__main__":
    build()
