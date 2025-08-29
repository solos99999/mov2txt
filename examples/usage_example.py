#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MP4转文本工具使用示例
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """基本使用示例"""
    print("=== MP4转文本工具使用示例 ===\n")
    
    # 检查主程序文件
    if os.path.exists(os.path.join(project_root, "sherpa_ncnn_video_to_text.py")):
        print("[OK] 主程序文件存在")
    else:
        print("[ERROR] 主程序文件不存在")
        return
    
    # 检查配置文件
    if os.path.exists(os.path.join(project_root, "config.json")):
        print("[OK] 配置文件存在")
    else:
        print("[ERROR] 配置文件不存在")
        return
    
    # 检查模型文件
    model_path = os.path.join(project_root, "models", "sherpa-ncnn-streaming-zipformer-bilingual-zh-en-2023-02-13")
    if os.path.exists(model_path):
        print("[OK] 流式双语模型存在")
    else:
        print("[ERROR] 流式双语模型不存在")
        return
    
    print("\n使用方法:")
    print("1. 转换单个视频文件:")
    print("   python sherpa_ncnn_video_to_text.py \"video.mp4\"")
    print("2. 指定输出文件:")
    print("   python sherpa_ncnn_video_to_text.py \"video.mp4\" -o \"output.txt\"")
    print("3. 查看系统状态:")
    print("   python sherpa_ncnn_video_to_text.py --status")
    print("4. 批量处理:")
    print("   python batch_sherpa_ncnn.py \"video_directory/\"")
    
    print("\n请将您的视频文件放在项目目录中，然后运行上述命令")

if __name__ == "__main__":
    main()