#!/usr/bin/env python3
"""
sherpa-ncnn安装和配置向导
"""

import os
import sys
import subprocess
import json
from pathlib import Path


class SherpaNcnnSetupWizard:
    """sherpa-ncnn安装和配置向导"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.config_file = self.current_dir / "config.json"
        self.setup_complete = False
    
    def print_banner(self):
        """打印横幅"""
        print("=" * 60)
        print("sherpa-ncnn 安装和配置向导")
        print("=" * 60)
        print()
        print("本向导将帮助您完成sherpa-ncnn的安装和配置")
        print()
    
    def check_python(self):
        """检查Python环境"""
        print("检查Python环境...")
        
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            print(f"Python版本: {result.stdout.strip()}")
            return True
        except Exception as e:
            print(f"Python检查失败: {e}")
            return False
    
    def install_dependencies(self):
        """安装依赖包"""
        print("\n安装依赖包...")
        
        dependencies = [
            ("numpy", "numpy"),
            ("moviepy", "moviepy"),
            ("sherpa-ncnn", "sherpa-ncnn"),
        ]
        
        failed_packages = []
        
        for package_name, import_name in dependencies:
            print(f"检查 {package_name}...")
            
            try:
                __import__(import_name)
                print(f"  ✓ {package_name} 已安装")
            except ImportError:
                print(f"  ✗ {package_name} 未安装，正在安装...")
                
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                                 check=True, capture_output=True)
                    print(f"  ✓ {package_name} 安装成功")
                except subprocess.CalledProcessError as e:
                    print(f"  ✗ {package_name} 安装失败: {e}")
                    failed_packages.append(package_name)
        
        if failed_packages:
            print(f"\n以下包安装失败: {failed_packages}")
            print("请手动安装这些包")
            return False
        
        print("所有依赖包安装成功")
        return True
    
    def create_config(self):
        """创建配置文件"""
        print("\n创建配置文件...")
        
        # 检查现有配置文件
        if self.config_file.exists():
            print("配置文件已存在")
            overwrite = input("是否覆盖现有配置? (y/N): ").lower().strip()
            if overwrite != 'y':
                print("保留现有配置文件")
                return True
        
        # 创建默认配置
        default_config = {
            "models": {
                "chinese": {
                    "name": "中文模型",
                    "description": "优化的中文语音识别模型",
                    "model_dir": "sherpa-ncnn-conv-emformer-transducer-2023-06-26",
                    "files": {
                        "tokens": "sherpa-ncnn-conv-emformer-transducer-2023-06-26/tokens.txt",
                        "encoder_param": "sherpa-ncnn-conv-emformer-transducer-2023-06-26/encoder_jit_trace-pnnx.ncnn.param",
                        "encoder_bin": "sherpa-ncnn-conv-emformer-transducer-2023-06-26/encoder_jit_trace-pnnx.ncnn.bin",
                        "decoder_param": "sherpa-ncnn-conv-emformer-transducer-2023-06-26/decoder_jit_trace-pnnx.ncnn.param",
                        "decoder_bin": "sherpa-ncnn-conv-emformer-transducer-2023-06-26/decoder_jit_trace-pnnx.ncnn.bin",
                        "joiner_param": "sherpa-ncnn-conv-emformer-transducer-2023-06-26/joiner_jit_trace-pnnx.ncnn.param",
                        "joiner_bin": "sherpa-ncnn-conv-emformer-transducer-2023-06-26/joiner_jit_trace-pnnx.ncnn.bin"
                    },
                    "sample_rate": 16000,
                    "language": "chinese"
                }
            },
            "recognition": {
                "default_model": "chinese",
                "num_threads": 4,
                "decoding_method": "greedy_search",
                "enable_endpoint_detection": True,
                "chunk_size": 0.1,
                "hotwords_file": "",
                "hotwords_score": 1.5
            },
            "audio": {
                "sample_rate": 16000,
                "channels": 1,
                "sample_width": 2,
                "codec": "pcm_s16le"
            },
            "output": {
                "format": "txt",
                "encoding": "utf-8",
                "save_timestamps": False,
                "save_confidence": False
            },
            "performance": {
                "max_file_size_mb": 500,
                "max_duration_minutes": 60,
                "batch_processing": True,
                "parallel_threads": 2
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"配置文件已创建: {self.config_file}")
            return True
        except Exception as e:
            print(f"配置文件创建失败: {e}")
            return False
    
    def download_model_guide(self):
        """显示模型下载指南"""
        print("\n模型下载指南")
        print("-" * 40)
        print()
        print("sherpa-ncnn需要下载预训练模型才能工作")
        print("请按以下步骤下载模型:")
        print()
        print("1. 访问模型下载页面:")
        print("   https://github.com/k2-fsa/sherpa-ncnn/releases/tag/models")
        print()
        print("2. 推荐模型:")
        print("   - 中文模型: sherpa-ncnn-conv-emformer-transducer-2023-06-26")
        print("   - 英文模型: sherpa-ncnn-conv-emformer-transducer-2022-12-06")
        print("   - 多语言模型: sherpa-ncnn-conv-emformer-transducer-multilingual-2023-06-26")
        print()
        print("3. 下载并解压到当前目录")
        print()
        print("4. 确保解压后的目录包含以下文件:")
        print("   - tokens.txt")
        print("   - encoder.ncnn.param")
        print("   - encoder.ncnn.bin")
        print("   - decoder.ncnn.param")
        print("   - decoder.ncnn.bin")
        print("   - joiner.ncnn.param")
        print("   - joiner.ncnn.bin")
        print()
        
        continue_choice = input("下载完成后按回车继续...")
        return True
    
    def check_models(self):
        """检查模型文件"""
        print("\n检查模型文件...")
        
        if not self.config_file.exists():
            print("配置文件不存在")
            return False
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"配置文件读取失败: {e}")
            return False
        
        models = config.get("models", {})
        if not models:
            print("配置中没有模型")
            return False
        
        available_models = 0
        
        for model_id, model_config in models.items():
            print(f"检查模型: {model_id}")
            
            files = model_config.get("files", {})
            missing_files = []
            
            for file_type, file_path in files.items():
                if not Path(file_path).exists():
                    missing_files.append(file_type)
            
            if missing_files:
                print(f"  ✗ 缺少文件: {missing_files}")
            else:
                print(f"  ✓ 模型完整")
                available_models += 1
        
        print(f"\n可用模型: {available_models}/{len(models)}")
        
        if available_models == 0:
            print("警告: 没有可用的模型")
            print("请按照上面的指南下载模型文件")
            return False
        
        return True
    
    def test_setup(self):
        """测试设置"""
        print("\n测试设置...")
        
        try:
            # 测试配置管理器
            from config_manager import ConfigManager
            config_manager = ConfigManager()
            print("✓ 配置管理器正常")
            
            # 测试主程序
            from sherpa_ncnn_video_to_text import VideoToTextSherpaNcnn
            converter = VideoToTextSherpaNcnn()
            print("✓ 主程序正常")
            
            # 测试批量处理
            from batch_sherpa_ncnn import BatchVideoToText
            batch_processor = BatchVideoToText()
            print("✓ 批量处理程序正常")
            
            return True
            
        except Exception as e:
            print(f"✗ 设置测试失败: {e}")
            return False
    
    def show_usage(self):
        """显示使用说明"""
        print("\n使用说明")
        print("-" * 40)
        print()
        print("安装完成！现在您可以使用以下命令:")
        print()
        print("1. 查看配置状态:")
        print("   python sherpa_ncnn_video_to_text.py --status")
        print()
        print("2. 列出可用模型:")
        print("   python sherpa_ncnn_video_to_text.py --list-models")
        print()
        print("3. 转换单个视频:")
        print("   python sherpa_ncnn_video_to_text.py \"视频文件.mp4\"")
        print()
        print("4. 批量转换:")
        print("   python batch_sherpa_ncnn.py \"目录路径\"")
        print()
        print("5. 图形化配置:")
        print("   python config_gui.py")
        print()
        print("6. Windows用户:")
        print("   sherpa_ncnn_tool.bat")
        print()
    
    def run(self):
        """运行向导"""
        self.print_banner()
        
        steps = [
            ("检查Python环境", self.check_python),
            ("安装依赖包", self.install_dependencies),
            ("创建配置文件", self.create_config),
            ("模型下载指南", self.download_model_guide),
            ("检查模型文件", self.check_models),
            ("测试设置", self.test_setup),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*50}")
            print(f"步骤: {step_name}")
            print('='*50)
            
            if not step_func():
                print(f"\n{step_name} 失败")
                print("请解决上述问题后重新运行向导")
                return False
        
        self.show_usage()
        
        print("\n" + "="*60)
        print("设置完成！")
        print("="*60)
        print()
        print("sherpa-ncnn已成功安装和配置")
        print("您可以开始使用视频转文本功能了")
        print()
        
        self.setup_complete = True
        return True


def main():
    """主函数"""
    wizard = SherpaNcnnSetupWizard()
    
    try:
        success = wizard.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n向导运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()