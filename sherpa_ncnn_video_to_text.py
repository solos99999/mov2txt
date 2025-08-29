#!/usr/bin/env python3
"""
基于sherpa-ncnn的语音转文本模块
提供高效、准确的离线语音识别功能
"""

import os
import sys
import wave
import time
import argparse
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import numpy as np
    import sherpa_ncnn
except ImportError as e:
    print(f"缺少sherpa-ncnn依赖: {e}")
    print("请运行: pip install sherpa-ncnn")
    sys.exit(1)

try:
    from moviepy import VideoFileClip
except ImportError as e:
    print(f"缺少moviepy依赖: {e}")
    print("请运行: pip install moviepy")
    sys.exit(1)

from config_manager import ConfigManager


class SherpaNcnnRecognizer:
    """sherpa-ncnn语音识别器"""
    
    def __init__(self, model_config: Dict[str, Any], recognition_config: Dict[str, Any] = None):
        """
        初始化sherpa-ncnn识别器
        
        Args:
            model_config: 模型配置字典
            recognition_config: 识别配置字典
        """
        self.model_config = model_config
        self.recognition_config = recognition_config or {}
        self.recognizer = None
        self._setup_recognizer()
    
    def _setup_recognizer(self):
        """设置识别器"""
        try:
            # 从模型配置中获取文件路径
            files = self.model_config.get('files', {})
            
            # 从识别配置中获取参数
            rec_config = self.recognition_config
            
            self.recognizer = sherpa_ncnn.Recognizer(
                tokens=files.get('tokens', ''),
                encoder_param=files.get('encoder_param', ''),
                encoder_bin=files.get('encoder_bin', ''),
                decoder_param=files.get('decoder_param', ''),
                decoder_bin=files.get('decoder_bin', ''),
                joiner_param=files.get('joiner_param', ''),
                joiner_bin=files.get('joiner_bin', ''),
                num_threads=rec_config.get('num_threads', 4),
                decoding_method=rec_config.get('decoding_method', 'greedy_search'),
                enable_endpoint_detection=rec_config.get('enable_endpoint_detection', False),
                model_sample_rate=self.model_config.get('sample_rate', 16000),
                hotwords_file=rec_config.get('hotwords_file', ''),
                hotwords_score=rec_config.get('hotwords_score', 1.5),
            )
            print(f"sherpa-ncnn识别器初始化成功，采样率: {self.recognizer.sample_rate}")
        except Exception as e:
            print(f"识别器初始化失败: {e}")
            raise
    
    def recognize_file(self, audio_path: str, chunk_size: float = 0.1, 
                       show_progress: bool = True, progress_interval: float = 5.0) -> str:
        """
        识别音频文件
        
        Args:
            audio_path: 音频文件路径
            chunk_size: 流式处理的块大小（秒）
            show_progress: 是否显示进度条
            progress_interval: 进度更新间隔（秒）
            
        Returns:
            识别的文本
        """
        if not self.recognizer:
            raise RuntimeError("识别器未初始化")
        
        try:
            # 使用更安全的文件处理方式
            with wave.open(audio_path, 'rb') as wf:
                # 检查音频格式
                if wf.getnchannels() != 1:
                    print(f"警告: 音频文件有{wf.getnchannels()}个声道，将使用第一个声道")
                
                if wf.getsampwidth() != 2:
                    print(f"警告: 音频采样宽度为{wf.getsampwidth()}字节，期望2字节")
                
                wave_file_sample_rate = wf.getframerate()
                num_samples = wf.getnframes()
                
                duration = num_samples / wave_file_sample_rate
                print(f"开始识别音频文件: {audio_path}")
                print(f"音频时长: {duration:.2f}秒")
                
                # 分批读取音频数据，避免内存问题
                chunk_samples = int(chunk_size * wave_file_sample_rate)
                total_chunks = (num_samples + chunk_samples - 1) // chunk_samples
                
                # 进度显示相关变量
                last_progress_time = time.time()
                processed_chunks = 0
                
                # 分批处理音频数据
                for chunk_idx in range(total_chunks):
                    start_sample = chunk_idx * chunk_samples
                    end_sample = min(start_sample + chunk_samples, num_samples)
                    
                    # 读取当前片段
                    wf.setpos(start_sample)
                    chunk_frames = wf.readframes(end_sample - start_sample)
                    
                    if not chunk_frames:
                        break
                    
                    # 转换为numpy数组
                    samples_int16 = np.frombuffer(chunk_frames, dtype=np.int16)
                    if wf.getnchannels() > 1:
                        samples_int16 = samples_int16.reshape(-1, wf.getnchannels())[:, 0]
                    
                    samples_float32 = samples_int16.astype(np.float32) / 32768.0
                    
                    # 处理音频片段
                    try:
                        self.recognizer.accept_waveform(wave_file_sample_rate, samples_float32)
                    except Exception as chunk_error:
                        print(f"处理片段 {chunk_idx + 1}/{total_chunks} 时出错: {chunk_error}")
                        # 尝试重置识别器并继续
                        try:
                            self.recognizer.reset()
                            # 重新初始化识别器
                            self._setup_recognizer()
                            print("识别器已重置，继续处理...")
                        except Exception as reset_error:
                            print(f"重置识别器失败: {reset_error}")
                            raise
                    
                    processed_chunks = chunk_idx + 1
                    
                    # 计算和显示进度
                    if show_progress and (time.time() - last_progress_time >= progress_interval or chunk_idx == total_chunks - 1):
                        progress = (processed_chunks / total_chunks) * 100
                        elapsed_time = time.time() - last_progress_time
                        
                        try:
                            current_text = self.recognizer.text
                        except:
                            current_text = ""
                        
                        # 估算剩余时间
                        if progress > 0:
                            total_estimated_time = elapsed_time * (100 / progress)
                            remaining_time = total_estimated_time - elapsed_time
                        else:
                            remaining_time = 0
                        
                        # 创建进度条（使用ASCII字符避免编码问题）
                        progress_bar = self._create_progress_bar_ascii(progress, 50)
                        
                        # 限制识别文本长度，避免控制台混乱
                        display_text = current_text[:80] + "..." if len(current_text) > 80 else current_text
                        
                        progress_info = f"\r进度: {progress_bar} {progress:.1f}%"
                        progress_info += f" | 已用时: {elapsed_time/60:.1f}分钟"
                        progress_info += f" | 剩余: {remaining_time/60:.1f}分钟"
                        progress_info += f" | 片段: {processed_chunks}/{total_chunks}"
                        if display_text.strip():
                            progress_info += f" | 识别: {display_text}"
                        
                        print(progress_info, end='', flush=True)
                        last_progress_time = time.time()
                    
                    # 减少延迟，提高处理速度
                    time.sleep(chunk_size * 0.005)  # 减少延迟
                
                # 添加尾部静音以完成识别
                try:
                    tail_paddings = np.zeros(int(wave_file_sample_rate * 0.5), dtype=np.float32)
                    self.recognizer.accept_waveform(wave_file_sample_rate, tail_paddings)
                    self.recognizer.input_finished()
                except Exception as tail_error:
                    print(f"添加尾部静音时出错: {tail_error}")
                
                # 获取最终识别结果
                try:
                    final_text = self.recognizer.text
                except Exception as text_error:
                    print(f"获取识别结果时出错: {text_error}")
                    final_text = ""
                
                # 显示最终进度
                if show_progress:
                    progress_bar = self._create_progress_bar_ascii(100, 50)
                    total_time = duration / 60  # 音频时长转换为分钟
                    actual_time = (time.time() - last_progress_time + duration/60)
                    print(f"\r进度: {progress_bar} 100.0% | 总时长: {actual_time:.1f}分钟 | 识别完成！{' ' * 20}")
                
                # 重置识别器以便下次使用
                try:
                    self.recognizer.reset()
                except Exception as reset_error:
                    print(f"重置识别器时出错: {reset_error}")
                    # 尝试重新初始化
                    self._setup_recognizer()
                
                return final_text
                
        except Exception as e:
            print(f"音频识别失败: {e}")
            # 尝试重新初始化识别器
            try:
                self._setup_recognizer()
            except:
                pass
            raise
    
    def _create_progress_bar(self, progress: float, width: int = 50) -> str:
        """
        创建进度条
        
        Args:
            progress: 进度百分比 (0-100)
            width: 进度条宽度
            
        Returns:
            进度条字符串
        """
        filled = int(width * progress / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}]"
    
    def _create_progress_bar_ascii(self, progress: float, width: int = 50) -> str:
        """
        创建ASCII进度条（避免编码问题）
        
        Args:
            progress: 进度百分比 (0-100)
            width: 进度条宽度
            
        Returns:
            进度条字符串
        """
        filled = int(width * progress / 100)
        bar = '=' * filled + ' ' * (width - filled)
        return f"[{bar}]"


class VideoToTextSherpaNcnn:
    """基于sherpa-ncnn的视频转文本工具"""
    
    def __init__(self, config_file: str = "config.json", model_id: str = None):
        """
        初始化视频转文本工具
        
        Args:
            config_file: 配置文件路径
            model_id: 模型ID，如果为None则使用默认模型
        """
        self.config_manager = ConfigManager(config_file)
        self.model_id = model_id or self.config_manager.get_default_model()
        
        if not self.model_id:
            raise ValueError("没有可用的模型")
        
        self.model_config = self.config_manager.get_model_config(self.model_id)
        self.recognition_config = self.config_manager.get_recognition_config()
        self.audio_config = self.config_manager.get_audio_config()
        self.output_config = self.config_manager.get_output_config()
        
        print(f"使用模型: {self.model_config.get('name', self.model_id)}")
        
        # 初始化识别器
        self.recognizer = SherpaNcnnRecognizer(self.model_config, self.recognition_config)
    
    def get_available_models(self) -> list:
        """获取可用模型列表"""
        return self.config_manager.list_models()
    
    def switch_model(self, model_id: str) -> bool:
        """切换模型"""
        if model_id not in [m['id'] for m in self.get_available_models()]:
            print(f"模型 {model_id} 不存在")
            return False
        
        try:
            self.model_id = model_id
            self.model_config = self.config_manager.get_model_config(model_id)
            self.recognizer = SherpaNcnnRecognizer(self.model_config, self.recognition_config)
            print(f"已切换到模型: {self.model_config.get('name', model_id)}")
            return True
        except Exception as e:
            print(f"切换模型失败: {e}")
            return False
    
    def extract_audio(self, video_path: str, output_path: str = None) -> Optional[str]:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            output_path: 输出音频文件路径
            
        Returns:
            音频文件路径，失败返回None
        """
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"视频文件不存在: {video_path}")
            return None
        
        if output_path is None:
            output_path = video_path.with_suffix('.wav')
        
        print(f"正在提取音频: {video_path} -> {output_path}")
        
        # 确保输出目录存在
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        video = None
        try:
            # 验证视频文件
            video_size = video_path.stat().st_size
            print(f"视频文件大小: {video_size / (1024*1024):.2f} MB")
            
            # 加载视频文件
            video = VideoFileClip(str(video_path))
            
            if video.duration == 0:
                print("视频时长为0")
                return None
            
            print(f"视频时长: {video.duration:.2f} 秒")
            
            audio = video.audio
            
            if audio is None:
                print("视频中没有音频轨道")
                return None
            
            # 使用配置中的音频参数
            sample_rate = self.audio_config.get('sample_rate', 16000)
            codec = self.audio_config.get('codec', 'pcm_s16le')
            
            print(f"音频参数: 采样率={sample_rate}Hz, 编码={codec}")
            
            # 提取音频
            audio.write_audiofile(str(output_path), codec=codec, fps=sample_rate, 
                                 logger=None)  # 禁用logger避免输出冲突
            
            # 验证提取的音频文件
            if not output_path.exists():
                print("音频文件提取失败")
                return None
            
            audio_size = output_path.stat().st_size
            print(f"提取的音频文件大小: {audio_size / (1024*1024):.2f} MB")
            
            # 验证音频文件是否可读
            try:
                with wave.open(str(output_path), 'rb') as wf:
                    duration = wf.getnframes() / wf.getframerate()
                    print(f"音频时长: {duration:.2f} 秒")
            except Exception as wave_error:
                print(f"音频文件验证失败: {wave_error}")
                return None
            
            print(f"音频提取完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"音频提取失败: {e}")
            # 打印详细错误信息
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
            return None
        finally:
            # 确保视频文件被正确关闭
            if video is not None:
                try:
                    video.close()
                except Exception as close_error:
                    print(f"关闭视频文件时出错: {close_error}")
    
    def process_video(self, video_path: str, output_path: str = None, 
                     chunk_size: float = None, show_progress: bool = True,
                     progress_interval: float = 5.0) -> bool:
        """
        处理视频文件
        
        Args:
            video_path: 视频文件路径
            output_path: 输出文本文件路径
            chunk_size: 流式处理块大小（秒）
            show_progress: 是否显示进度条
            progress_interval: 进度更新间隔（秒）
            
        Returns:
            处理是否成功
        """
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"视频文件不存在: {video_path}")
            return False
        
        if output_path is None:
            output_path = video_path.with_suffix('.txt')
        
        # 使用配置中的块大小
        if chunk_size is None:
            chunk_size = self.recognition_config.get('chunk_size', 0.1)
        
        print(f"开始处理视频: {video_path}")
        print(f"使用模型: {self.model_config.get('name', self.model_id)}")
        print(f"语言: {self.model_config.get('language', 'unknown')}")
        if show_progress:
            print("进度显示: 已启用")
        
        # 确保输出目录存在
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        audio_path = None
        start_time = time.time()
        
        try:
            # 提取音频
            print("正在提取音频...")
            audio_path = self.extract_audio(video_path)
            if not audio_path:
                print("音频提取失败")
                return False
            
            # 验证音频文件
            if not Path(audio_path).exists():
                print("音频文件不存在")
                return False
            
            audio_size = Path(audio_path).stat().st_size
            print(f"音频文件大小: {audio_size / (1024*1024):.2f} MB")
            
            # 语音识别
            print("开始语音识别...")
            text = self.recognizer.recognize_file(
                audio_path, chunk_size, show_progress, progress_interval
            )
            
            # 验证识别结果
            if text and text.strip():
                # 清理文本
                text = text.strip()
                text = ' '.join(text.split())  # 规范化空格
                
                # 使用配置中的输出设置
                encoding = self.output_config.get('encoding', 'utf-8')
                
                # 保存结果
                print(f"正在保存结果到: {output_path}")
                with open(output_path, 'w', encoding=encoding) as f:
                    f.write(text)
                
                # 计算处理时间
                total_time = time.time() - start_time
                
                print(f"\n{'='*50}")
                print(f"转换完成！")
                print(f"{'='*50}")
                print(f"输出文件: {output_path}")
                print(f"识别文本长度: {len(text)} 字符")
                print(f"总处理时间: {total_time:.1f} 秒")
                print(f"处理速度: {len(text)/total_time:.1f} 字符/秒")
                
                if len(text) > 200:
                    print(f"识别结果预览: {text[:200]}...")
                else:
                    print(f"识别结果: {text}")
                
                return True
            else:
                print("识别结果为空")
                return False
                
        except KeyboardInterrupt:
            print("\n用户中断处理")
            return False
        except Exception as e:
            print(f"处理过程中发生错误: {e}")
            # 打印详细错误信息
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
            return False
        finally:
            # 清理临时音频文件
            if audio_path and Path(audio_path).exists():
                try:
                    Path(audio_path).unlink()
                    print(f"已清理临时音频文件: {audio_path}")
                except Exception as cleanup_error:
                    print(f"清理临时文件失败: {cleanup_error}")


def main():
    parser = argparse.ArgumentParser(description='基于sherpa-ncnn的视频语音转文本工具')
    parser.add_argument('video_path', nargs='?', help='视频文件路径')
    parser.add_argument('-o', '--output', help='输出文本文件路径')
    parser.add_argument('-c', '--config', default='config.json', help='配置文件路径')
    parser.add_argument('-m', '--model', help='模型ID')
    parser.add_argument('--chunk_size', type=float, help='流式处理块大小（秒）')
    parser.add_argument('--progress-interval', type=float, default=5.0, 
                       help='进度更新间隔（秒），默认5秒')
    parser.add_argument('--no-progress', action='store_true', 
                       help='禁用进度条显示')
    parser.add_argument('--recovery-mode', action='store_true',
                       help='启用恢复模式（处理失败时自动尝试恢复）')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='最大重试次数，默认3次')
    parser.add_argument('--list-models', action='store_true', help='列出可用模型')
    parser.add_argument('--status', action='store_true', help='显示配置状态')
    
    args = parser.parse_args()
    
    try:
        # 显示配置状态
        if args.status:
            config_manager = ConfigManager(args.config)
            config_manager.print_status()
            return
        
        # 初始化转换器
        converter = VideoToTextSherpaNcnn(args.config, args.model)
        
        # 列出可用模型
        if args.list_models:
            print("可用模型:")
            for model in converter.get_available_models():
                status_text = "可用" if model["available"] else "不可用"
                print(f"  {model['id']}: {model['name']} ({model['language']}) - {status_text}")
            return
        
        # 处理视频
        if not args.video_path:
            parser.print_help()
            sys.exit(1)
        
        show_progress = not args.no_progress
        
        if args.recovery_mode:
            print(f"启用恢复模式，最大重试次数: {args.max_retries}")
            
            # 恢复模式处理
            success = False
            for attempt in range(args.max_retries):
                print(f"\n{'='*60}")
                print(f"尝试 {attempt + 1}/{args.max_retries}")
                print(f"{'='*60}")
                
                try:
                    success = converter.process_video(
                        args.video_path, 
                        args.output, 
                        args.chunk_size,
                        show_progress,
                        args.progress_interval
                    )
                    
                    if success:
                        print(f"第 {attempt + 1} 次尝试成功！")
                        break
                    else:
                        print(f"第 {attempt + 1} 次尝试失败")
                        
                except Exception as attempt_error:
                    print(f"第 {attempt + 1} 次尝试发生异常: {attempt_error}")
                
                # 如果不是最后一次尝试，等待一段时间
                if attempt < args.max_retries - 1:
                    wait_time = 5 * (attempt + 1)  # 递增等待时间
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    
                    # 重新初始化转换器
                    try:
                        print("重新初始化转换器...")
                        converter = VideoToTextSherpaNcnn(args.config, args.model)
                    except Exception as init_error:
                        print(f"重新初始化失败: {init_error}")
                        continue
        else:
            # 普通模式处理
            success = converter.process_video(
                args.video_path, 
                args.output, 
                args.chunk_size,
                show_progress,
                args.progress_interval
            )
        
        if not success:
            print("\n处理失败！")
            if args.recovery_mode:
                print("建议：")
                print("1. 检查视频文件是否完整")
                print("2. 尝试使用较小的chunk_size")
                print("3. 检查系统内存是否充足")
                print("4. 尝试重新启动程序")
            sys.exit(1)
            
    except Exception as e:
        print(f"程序运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()