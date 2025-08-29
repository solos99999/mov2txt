#!/usr/bin/env python3
"""
基于sherpa-ncnn的批量视频转文本工具
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import List, Optional
from sherpa_ncnn_video_to_text import VideoToTextSherpaNcnn
from config_manager import ConfigManager


class BatchVideoToText:
    """批量视频转文本工具"""
    
    def __init__(self, config_file: str = "config.json", model_id: str = None):
        """
        初始化批量处理工具
        
        Args:
            config_file: 配置文件路径
            model_id: 模型ID
        """
        self.config_manager = ConfigManager(config_file)
        self.converter = VideoToTextSherpaNcnn(config_file, model_id)
        self.processed_files = []
        self.failed_files = []
        self.config_file = config_file
    
    def find_video_files(self, directory: str, extensions: List[str] = None) -> List[Path]:
        """
        查找目录中的视频文件
        
        Args:
            directory: 搜索目录
            extensions: 视频文件扩展名列表
            
        Returns:
            视频文件路径列表
        """
        if extensions is None:
            extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']
        
        directory = Path(directory)
        if not directory.exists():
            print(f"目录不存在: {directory}")
            return []
        
        video_files = []
        for ext in extensions:
            video_files.extend(directory.rglob(f"*{ext}"))
            video_files.extend(directory.rglob(f"*{ext.upper()}"))
        
        return sorted(video_files)
    
    def process_single_file(self, video_path: Path, output_dir: Path = None, 
                          chunk_size: float = 0.1) -> bool:
        """
        处理单个视频文件
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            chunk_size: 流式处理块大小
            
        Returns:
            处理是否成功
        """
        if output_dir is None:
            output_dir = video_path.parent
        
        output_path = output_dir / f"{video_path.stem}.txt"
        
        print(f"\n处理文件: {video_path}")
        print(f"输出文件: {output_path}")
        
        try:
            success = self.converter.process_video(
                str(video_path), str(output_path), chunk_size
            )
            
            if success:
                self.processed_files.append(video_path)
                print(f"✓ 处理成功: {video_path}")
            else:
                self.failed_files.append(video_path)
                print(f"✗ 处理失败: {video_path}")
            
            return success
            
        except Exception as e:
            self.failed_files.append(video_path)
            print(f"✗ 处理异常: {video_path} - {e}")
            return False
    
    def process_batch(self, input_path: str, output_dir: str = None,
                     chunk_size: float = 0.1, recursive: bool = False) -> bool:
        """
        批量处理视频文件
        
        Args:
            input_path: 输入路径（文件或目录）
            output_dir: 输出目录
            chunk_size: 流式处理块大小
            recursive: 是否递归搜索子目录
            
        Returns:
            是否所有文件都处理成功
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            print(f"输入路径不存在: {input_path}")
            return False
        
        # 设置输出目录
        if output_dir is None:
            output_dir = input_path.parent if input_path.is_file() else input_path / "output"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"输出目录: {output_dir}")
        
        start_time = time.time()
        
        if input_path.is_file():
            # 处理单个文件
            print(f"处理单个文件: {input_path}")
            success = self.process_single_file(input_path, output_dir, chunk_size)
            
        else:
            # 处理目录中的文件
            print(f"处理目录: {input_path}")
            if recursive:
                video_files = self.find_video_files(input_path)
            else:
                video_files = []
                for ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm']:
                    video_files.extend(input_path.glob(f"*{ext}"))
                    video_files.extend(input_path.glob(f"*{ext.upper()}"))
            
            if not video_files:
                print("未找到视频文件")
                return False
            
            print(f"找到 {len(video_files)} 个视频文件")
            
            # 批量处理
            for i, video_file in enumerate(video_files, 1):
                print(f"\n[{i}/{len(video_files)}] 处理文件: {video_file}")
                self.process_single_file(video_file, output_dir, chunk_size)
        
        # 统计结果
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n{'='*50}")
        print(f"批量处理完成")
        print(f"{'='*50}")
        print(f"总用时: {total_time:.2f}秒")
        print(f"成功处理: {len(self.processed_files)} 个文件")
        print(f"处理失败: {len(self.failed_files)} 个文件")
        
        if self.processed_files:
            print(f"\n成功处理的文件:")
            for file_path in self.processed_files:
                print(f"  ✓ {file_path}")
        
        if self.failed_files:
            print(f"\n处理失败的文件:")
            for file_path in self.failed_files:
                print(f"  ✗ {file_path}")
        
        return len(self.failed_files) == 0
    
    def generate_report(self, output_path: str = None):
        """
        生成处理报告
        
        Args:
            output_path: 报告文件路径
        """
        if output_path is None:
            output_path = "batch_processing_report.txt"
        
        report_path = Path(output_path)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("批量视频转文本处理报告\n")
            f.write("="*50 + "\n")
            f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"成功处理: {len(self.processed_files)} 个文件\n")
            f.write(f"处理失败: {len(self.failed_files)} 个文件\n")
            f.write("\n")
            
            if self.processed_files:
                f.write("成功处理的文件:\n")
                for file_path in self.processed_files:
                    f.write(f"  ✓ {file_path}\n")
                f.write("\n")
            
            if self.failed_files:
                f.write("处理失败的文件:\n")
                for file_path in self.failed_files:
                    f.write(f"  ✗ {file_path}\n")
                f.write("\n")
        
        print(f"处理报告已保存到: {report_path}")


def main():
    parser = argparse.ArgumentParser(description='基于sherpa-ncnn的批量视频转文本工具')
    parser.add_argument('input_path', help='输入路径（视频文件或目录）')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('-c', '--config', default='config.json', help='配置文件路径')
    parser.add_argument('-m', '--model', help='模型ID')
    parser.add_argument('--chunk_size', type=float, help='流式处理块大小（秒）')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='递归搜索子目录')
    parser.add_argument('--report', help='生成处理报告文件路径')
    parser.add_argument('--list-models', action='store_true', help='列出可用模型')
    parser.add_argument('--status', action='store_true', help='显示配置状态')
    
    args = parser.parse_args()
    
    try:
        # 显示配置状态
        if args.status:
            config_manager = ConfigManager(args.config)
            config_manager.print_status()
            return
        
        # 初始化批量处理器
        batch_processor = BatchVideoToText(args.config, args.model)
        
        # 列出可用模型
        if args.list_models:
            print("可用模型:")
            for model in batch_processor.converter.get_available_models():
                status_text = "可用" if model["available"] else "不可用"
                print(f"  {model['id']}: {model['name']} ({model['language']}) - {status_text}")
            return
        
        # 批量处理
        success = batch_processor.process_batch(
            args.input_path, args.output, args.chunk_size, args.recursive
        )
        
        if args.report:
            batch_processor.generate_report(args.report)
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        print(f"程序运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()