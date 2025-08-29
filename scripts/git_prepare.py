#!/usr/bin/env python3
"""
Git提交准备脚本
用于清理项目文件，准备提交到GitHub
"""

import os
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, description=""):
    """运行命令并显示结果"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def clean_project():
    """清理项目文件"""
    print("清理项目文件...")
    
    # 清理Python缓存
    patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        "*.egg-info",
        "build",
        "dist",
        ".pytest_cache",
        ".mypy_cache"
    ]
    
    for pattern in patterns:
        if os.path.exists(pattern):
            if os.path.isdir(pattern):
                shutil.rmtree(pattern)
                print(f"删除目录: {pattern}")
            else:
                os.remove(pattern)
                print(f"删除文件: {pattern}")
    
    # 清理日志和临时文件
    for dirname in ["logs", "temp", "output", "cache"]:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
            print(f"删除目录: {dirname}")
    
    # 清理生成的文本文件
    for txt_file in Path(".").glob("*.txt"):
        if txt_file.name not in ["README.md", "requirements.txt", "offline_requirements.txt"]:
            txt_file.unlink()
            print(f"删除文件: {txt_file}")
    
    print("项目清理完成")

def check_git_status():
    """检查Git状态"""
    print("检查Git状态...")
    
    if not run_command("git status", "检查Git状态"):
        return False
    
    # 检查是否有未跟踪的文件
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    untracked = result.stdout.strip()
    
    if untracked:
        print("发现未跟踪的文件:")
        print(untracked)
        print("\n请使用 'git add' 添加要提交的文件")
    else:
        print("没有未跟踪的文件")
    
    return True

def create_commit_message():
    """创建提交消息"""
    import datetime
    
    now = datetime.datetime.now()
    commit_message = f"更新项目文件 - {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    print(f"建议的提交消息: {commit_message}")
    return commit_message

def main():
    """主函数"""
    print("=== Git提交准备脚本 ===\n")
    
    # 1. 清理项目
    if input("是否清理项目文件? (y/N): ").lower() == 'y':
        clean_project()
    
    # 2. 检查Git状态
    check_git_status()
    
    # 3. 检查重要文件
    print("\n检查重要文件...")
    important_files = [
        "README.md",
        "requirements.txt", 
        "config.json",
        "sherpa_ncnn_video_to_text.py",
        "LICENSE",
        ".gitignore"
    ]
    
    for file in important_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} (缺失)")
    
    # 4. 创建提交消息
    commit_message = create_commit_message()
    
    # 5. 提供提交建议
    print("\n提交建议:")
    print("1. git add .")
    print("2. git status")
    print("3. git commit -m \"更新项目文件\"")
    print("4. git push origin main")
    
    # 6. 检查项目大小
    print("\n检查项目大小...")
    total_size = 0
    for root, dirs, files in os.walk("."):
        # 跳过某些目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'env']]
        
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    
    print(f"项目总大小: {total_size / (1024*1024):.2f} MB")
    
    if total_size > 100 * 1024 * 1024:  # 100MB
        print("⚠️ 项目较大，建议使用Git LFS管理大文件")
    
    print("\n=== 准备完成 ===")

if __name__ == "__main__":
    main()