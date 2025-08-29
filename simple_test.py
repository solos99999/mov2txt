#!/usr/bin/env python3
"""
简化的视频转文本测试脚本
"""

import sys
import wave
import time
import numpy as np
import sherpa_ncnn
from pathlib import Path

def recognize_audio_simple(audio_path: str) -> str:
    """简单的音频识别函数"""
    try:
        # 初始化识别器
        recognizer = sherpa_ncnn.Recognizer(
            tokens="models/sherpa-ncnn-streaming-zipformer-bilingual-zh-en-2023-02-13/tokens.txt",
            encoder_param="models/sherpa-ncnn-streaming-zipformer-bilingual-zh-en-2023-02-13/encoder_jit_trace-pnnx.ncnn.param",
            encoder_bin="models/sherpa-ncnn-streaming-zipformer-bilingual-zh-en-2023-02-13/encoder_jit_trace-pnnx.ncnn.bin",
            decoder_param="models/sherpa-ncnn-streaming-zipformer-bilingual-zh-en-2023-02-13/decoder_jit_trace-pnnx.ncnn.param",
            decoder_bin="models/sherpa-ncnn-streaming-zipformer-bilingual-zh-en-2023-02-13/decoder_jit_trace-pnnx.ncnn.bin",
            joiner_param="models/sherpa-ncnn-streaming-zipformer-bilingual-zh-en-2023-02-13/joiner_jit_trace-pnnx.ncnn.param",
            joiner_bin="models/sherpa-ncnn-streaming-zipformer-bilingual-zh-en-2023-02-13/joiner_jit_trace-pnnx.ncnn.bin",
            num_threads=4,
            decoding_method='greedy_search',
            enable_endpoint_detection=False,
            model_sample_rate=16000,
        )
        
        print(f"开始识别音频文件: {audio_path}")
        
        with wave.open(audio_path, 'rb') as wf:
            wave_file_sample_rate = wf.getframerate()
            num_samples = wf.getnframes()
            samples = wf.readframes(num_samples)
            
            # 转换为numpy数组
            samples_int16 = np.frombuffer(samples, dtype=np.int16)
            if wf.getnchannels() > 1:
                samples_int16 = samples_int16.reshape(-1, wf.getnchannels())[:, 0]
            
            samples_float32 = samples_int16.astype(np.float32) / 32768.0
            
            print(f"音频时长: {num_samples / wave_file_sample_rate:.2f}秒")
            
            # 流式处理
            chunk_size = 0.1  # 100ms chunks
            chunk_samples = int(chunk_size * wave_file_sample_rate)
            start = 0
            
            while start < samples_float32.shape[0]:
                end = start + chunk_samples
                end = min(end, samples_float32.shape[0])
                
                chunk = samples_float32[start:end]
                recognizer.accept_waveform(wave_file_sample_rate, chunk)
                
                # 实时显示识别结果
                current_text = recognizer.text
                if current_text:
                    print(f"识别中: {current_text}")
                
                start = end
                
                # 减少延迟以便更快完成
                time.sleep(chunk_size * 0.01)
            
            # 添加尾部静音以完成识别
            tail_paddings = np.zeros(int(wave_file_sample_rate * 0.5), dtype=np.float32)
            recognizer.accept_waveform(wave_file_sample_rate, tail_paddings)
            recognizer.input_finished()
            
            final_text = recognizer.text
            print(f"识别完成: {final_text}")
            
            return final_text
            
    except Exception as e:
        print(f"音频识别失败: {e}")
        return ""

def main():
    if len(sys.argv) < 2:
        print("使用方法: python simple_test.py <音频文件路径>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    
    if not Path(audio_path).exists():
        print(f"音频文件不存在: {audio_path}")
        sys.exit(1)
    
    # 识别音频
    text = recognize_audio_simple(audio_path)
    
    if text:
        # 保存结果
        output_path = Path(audio_path).with_suffix('.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"转换完成！结果保存到: {output_path}")
        print(f"识别结果长度: {len(text)} 字符")
    else:
        print("识别结果为空")

if __name__ == "__main__":
    main()