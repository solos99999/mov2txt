#!/usr/bin/env python3
"""
视频语音转文本工具 - 最终解决方案
支持在线和离线两种模式
"""

import os
import sys
import json
import wave
import argparse
import tempfile
import time
from pathlib import Path

try:
    import speech_recognition as sr
    import moviepy
    from moviepy import VideoFileClip
    import vosk
except ImportError as e:
    print(f"缺少依赖包: {e}")
    print("请运行: pip install moviepy SpeechRecognition vosk")
    exit(1)

class VideoToTextFinal:
    def __init__(self):
        self.online_mode = True
        self.vosk_model = None
        self.model_path = None
        self._setup_vosk()
    
    def _setup_vosk(self):
        """设置Vosk离线模型"""
        # 查找Vosk模型
        current_dir = Path.cwd()
        for model_dir in current_dir.glob("vosk-model-*"):
            if model_dir.is_dir():
                self.model_path = str(model_dir)
                try:
                    print(f"正在加载离线模型: {self.model_path}")
                    self.vosk_model = vosk.Model(self.model_path)
                    print("离线模型加载成功")
                    self.online_mode = False
                except Exception as e:
                    print(f"离线模型加载失败: {e}")
                    print("将使用在线模式")
                break
    
    def extract_audio(self, video_path, output_path=None):
        """从视频中提取音频"""
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"视频文件不存在: {video_path}")
            return None
        
        if output_path is None:
            output_path = video_path.with_suffix('.wav')
        
        print(f"正在提取音频: {video_path}")
        
        try:
            video = VideoFileClip(str(video_path))
            audio = video.audio
            
            if audio is None:
                print("视频中没有音频轨道")
                video.close()
                return None
            
            audio.write_audiofile(str(output_path), codec='pcm_s16le', fps=16000)
            video.close()
            
            print(f"音频提取完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"音频提取失败: {e}")
            return None
    
    def recognize_online(self, audio_path, language='zh-CN'):
        """在线语音识别"""
        recognizer = sr.Recognizer()
        
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
            
            print("正在使用在线语音识别...")
            text = recognizer.recognize_google(audio_data, language=language)
            return text
            
        except sr.UnknownValueError:
            return "无法识别语音内容"
        except sr.RequestError as e:
            print(f"在线识别服务错误: {e}")
            return None
    
    def recognize_offline(self, audio_path):
        """离线语音识别"""
        if not self.vosk_model:
            print("离线模型未加载")
            return None
        
        try:
            with wave.open(audio_path, 'rb') as wf:
                recognizer = vosk.KaldiRecognizer(self.vosk_model, wf.getframerate())
                recognizer.SetWords(True)
                
                results = []
                
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        if 'text' in result and result['text']:
                            results.append(result['text'])
                            print(f"离线识别: {result['text']}")
                
                # 最终结果
                final_result = json.loads(recognizer.FinalResult())
                if 'text' in final_result and final_result['text']:
                    results.append(final_result['text'])
                
                text = ' '.join(results)
                print(f"离线识别完成: {text}")
                return text
                
        except Exception as e:
            print(f"离线识别失败: {e}")
            return None
    
    def process_video(self, video_path, output_path=None, mode='auto', language='zh-CN'):
        """处理视频文件"""
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"视频文件不存在: {video_path}")
            return False
        
        if output_path is None:
            output_path = video_path.with_suffix('.txt')
        
        print(f"开始处理视频: {video_path}")
        print(f"模式: {mode}")
        
        # 提取音频
        audio_path = self.extract_audio(video_path)
        if not audio_path:
            return False
        
        # 语音识别
        text = None
        
        if mode == 'online':
            text = self.recognize_online(audio_path, language)
        elif mode == 'offline':
            text = self.recognize_offline(audio_path)
        elif mode == 'auto':
            # 优先使用离线，如果不可用则使用在线
            if self.vosk_model:
                text = self.recognize_offline(audio_path)
                if text is None:
                    print("离线识别失败，尝试在线识别...")
                    text = self.recognize_online(audio_path, language)
            else:
                text = self.recognize_online(audio_path, language)
        
        # 保存结果
        if text:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"转换完成！结果保存到: {output_path}")
            print(f"识别结果: {text}")
            return True
        else:
            print("识别失败")
            return False

def main():
    parser = argparse.ArgumentParser(description='视频语音转文本工具 - 最终解决方案')
    parser.add_argument('video_path', help='视频文件路径')
    parser.add_argument('-o', '--output', help='输出文本文件路径')
    parser.add_argument('-m', '--mode', choices=['online', 'offline', 'auto'], 
                       default='auto', help='识别模式')
    parser.add_argument('-l', '--language', default='zh-CN', 
                       help='识别语言（仅在线模式）')
    
    args = parser.parse_args()
    
    converter = VideoToTextFinal()
    success = converter.process_video(args.video_path, args.output, args.mode, args.language)
    
    if not success:
        exit(1)

if __name__ == "__main__":
    main()