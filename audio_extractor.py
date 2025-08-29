#!/usr/bin/env python3
"""
音频提取工具
将视频中的音频提取为WAV文件
"""

import os
import argparse
from pathlib import Path

try:
    from moviepy import VideoFileClip
except ImportError:
    print("Installing moviepy...")
    import subprocess
    subprocess.run(["pip", "install", "moviepy"], check=True)
    from moviepy import VideoFileClip

def extract_audio(video_path, output_path=None):
    """从视频中提取音频"""
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"视频文件不存在: {video_path}")
        return False
    
    if output_path is None:
        output_path = video_path.with_suffix('.wav')
    
    print(f"正在提取音频: {video_path} -> {output_path}")
    
    try:
        video = VideoFileClip(str(video_path))
        audio = video.audio
        
        if audio is None:
            print("视频中没有音频轨道")
            video.close()
            return False
        
        # 提取音频为WAV格式
        audio.write_audiofile(str(output_path), codec='pcm_s16le', fps=16000)
        video.close()
        
        print(f"音频提取完成: {output_path}")
        return True
        
    except Exception as e:
        print(f"音频提取失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='视频音频提取工具')
    parser.add_argument('video_path', help='视频文件路径')
    parser.add_argument('-o', '--output', help='输出音频文件路径')
    
    args = parser.parse_args()
    
    success = extract_audio(args.video_path, args.output)
    
    if success:
        print("\n音频文件已准备就绪！")
        print("你可以使用以下方式进行语音识别：")
        print("1. 在线识别服务")
        print("2. 离线识别工具")
        print("3. 其他语音识别软件")
    else:
        exit(1)

if __name__ == "__main__":
    main()