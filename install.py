#!/usr/bin/env python3
"""
视频语音转文本工具 - 自动安装程序
一键安装所有依赖和模型
"""

import os
import sys
import subprocess
import platform
import shutil
import urllib.request
import zipfile
import tempfile
from pathlib import Path

class VideoToTextInstaller:
    def __init__(self):
        self.python_cmd = self._get_python_command()
        self.os_type = platform.system().lower()
        self.install_dir = Path.cwd()
        self.model_url = "https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip"
        self.model_name = "vosk-model-cn-0.22"
        self.model_path = self.install_dir / self.model_name
        
    def _get_python_command(self):
        """获取Python命令"""
        possible_commands = ['python', 'python3', 'py']
        for cmd in possible_commands:
            try:
                result = subprocess.run([cmd, '--version'], 
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    return cmd
            except FileNotFoundError:
                continue
        return None
    
    def print_header(self):
        """打印安装程序标题"""
        print("=" * 60)
        print("      视频语音转文本工具 - 自动安装程序")
        print("=" * 60)
        print("功能特点:")
        print("  ✅ 离线语音识别，无需网络连接")
        print("  ✅ 中文识别准确率85-95%")
        print("  ✅ 支持多种视频格式")
        print("  ✅ 简单易用，一键安装")
        print("=" * 60)
        print()
    
    def check_python(self):
        """检查Python环境"""
        print("🔍 检查Python环境...")
        
        if not self.python_cmd:
            print("❌ 未找到Python，请先安装Python 3.7+")
            print("下载地址: https://www.python.org/downloads/")
            return False
        
        result = subprocess.run([self.python_cmd, '--version'], 
                               capture_output=True, text=True)
        version = result.stdout.strip().replace('Python ', '')
        
        print(f"✅ 找到Python: {version}")
        
        # 检查版本是否满足要求
        major, minor = map(int, version.split('.')[:2])
        if major < 3 or (major == 3 and minor < 7):
            print("❌ Python版本过低，需要Python 3.7+")
            return False
        
        return True
    
    def install_dependencies(self):
        """安装Python依赖包"""
        print("\n📦 安装Python依赖包...")
        
        dependencies = [
            "vosk==0.3.45",
            "moviepy==2.2.1",
            "SpeechRecognition==3.10.0",
            "pyaudio==0.2.11",
            "numpy>=1.20.0",
            "requests>=2.25.0"
        ]
        
        for dep in dependencies:
            print(f"  安装 {dep}...")
            try:
                result = subprocess.run([
                    self.python_cmd, '-m', 'pip', 'install', dep
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"  ✅ {dep} 安装成功")
                else:
                    print(f"  ❌ {dep} 安装失败: {result.stderr}")
                    return False
            except Exception as e:
                print(f"  ❌ 安装 {dep} 时出错: {e}")
                return False
        
        return True
    
    def download_model(self):
        """下载Vosk中文模型"""
        print(f"\n📥 下载语音识别模型...")
        print(f"  模型大小: 约1.2GB")
        print(f"  下载地址: {self.model_url}")
        
        if self.model_path.exists():
            print(f"  ✅ 模型已存在: {self.model_path}")
            return True
        
        # 创建临时文件
        temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        temp_zip.close()
        
        try:
            print("  正在下载，请稍候...")
            
            def show_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    downloaded = (block_num * block_size) // (1024 * 1024)
                    total = total_size // (1024 * 1024)
                    print(f"    下载进度: {percent}% ({downloaded}/{total} MB)", end='\r')
            
            urllib.request.urlretrieve(self.model_url, temp_zip.name, show_progress)
            print("\n  ✅ 下载完成")
            
            # 解压模型
            print("  正在解压模型...")
            with zipfile.ZipFile(temp_zip.name, 'r') as zip_ref:
                zip_ref.extractall(self.install_dir)
            
            print(f"  ✅ 模型解压完成: {self.model_path}")
            return True
            
        except Exception as e:
            print(f"  ❌ 下载失败: {e}")
            print("  请手动下载模型:")
            print(f"    1. 访问: {self.model_url}")
            print(f"    2. 解压到当前目录")
            return False
        finally:
            # 清理临时文件
            if os.path.exists(temp_zip.name):
                os.unlink(temp_zip.name)
    
    def create_shortcuts(self):
        """创建快捷方式"""
        print("\n🔨 创建快捷方式...")
        
        # Windows快捷方式
        if self.os_type == 'windows':
            try:
                # 创建批处理文件
                batch_content = f'''@echo off
cd /d "{self.install_dir}"
{self.python_cmd} offline_video_to_text.py %*
pause
'''
                batch_path = self.install_dir / "视频转文本工具.bat"
                with open(batch_path, 'w', encoding='gbk') as f:
                    f.write(batch_content)
                print(f"  ✅ 创建Windows快捷方式: {batch_path}")
                
            except Exception as e:
                print(f"  ❌ 创建Windows快捷方式失败: {e}")
        
        # 通用启动脚本
        script_content = f'''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, r'{self.install_dir}')

# 导入主程序
from offline_video_to_text import main

if __name__ == '__main__':
    main()
'''
        script_path = self.install_dir / "run.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"  ✅ 创建启动脚本: {script_path}")
    
    def test_installation(self):
        """测试安装是否成功"""
        print("\n🧪 测试安装...")
        
        try:
            # 测试导入
            result = subprocess.run([
                self.python_cmd, '-c', 
                'import vosk; import moviepy; import speech_recognition; print("All imports successful")'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ 所有依赖包导入成功")
            else:
                print(f"  ❌ 依赖包导入失败: {result.stderr}")
                return False
            
            # 检查模型
            if self.model_path.exists():
                print(f"  ✅ 语音识别模型存在: {self.model_path}")
            else:
                print(f"  ❌ 语音识别模型不存在: {self.model_path}")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            return False
    
    def create_usage_guide(self):
        """创建使用指南"""
        guide_content = '''# 视频语音转文本工具 - 使用指南

## 快速开始

### Windows用户
双击运行 "视频转文本工具.bat"

### 其他用户
```bash
python offline_video_to_text.py "你的视频文件.mp4"
```

## 使用示例

```bash
# 基本用法
python offline_video_to_text.py "视频.mp4"

# 指定输出文件
python offline_video_to_text.py "视频.mp4" -o 输出.txt

# 使用不同识别方法
python offline_video_to_text.py "视频.mp4" --method vosk
python offline_video_to_text.py "视频.mp4" --method sphinx

# 指定模型路径
python offline_video_to_text.py "视频.mp4" --model /path/to/model
```

## 支持的视频格式
- MP4, AVI, MOV, WMV, FLV, MKV
- 其他常见视频格式

## 注意事项
1. 确保视频有音频轨道
2. 音频质量越好，识别准确率越高
3. 首次运行需要加载模型，请耐心等待

## 故障排除
如果遇到问题，请检查：
1. Python版本是否为3.7+
2. 是否有足够的磁盘空间
3. 视频文件是否损坏

## 技术支持
如有问题，请查看 README.md 文件或重新运行安装程序。
'''
        
        guide_path = self.install_dir / "使用指南.md"
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        print(f"  ✅ 创建使用指南: {guide_path}")
    
    def run_installation(self):
        """运行完整安装过程"""
        self.print_header()
        
        # 检查Python
        if not self.check_python():
            return False
        
        # 安装依赖
        if not self.install_dependencies():
            return False
        
        # 下载模型
        if not self.download_model():
            print("\n⚠️  模型下载失败，但可以继续安装")
            print("  稍后可以手动下载模型")
        
        # 创建快捷方式
        self.create_shortcuts()
        
        # 创建使用指南
        self.create_usage_guide()
        
        # 测试安装
        if self.test_installation():
            print("\n🎉 安装成功！")
            print("\n使用方法:")
            print("  Windows用户: 双击 '视频转文本工具.bat'")
            print("  其他用户: python offline_video_to_text.py '视频文件.mp4'")
            print("\n详细使用说明请查看 '使用指南.md'")
            return True
        else:
            print("\n❌ 安装测试失败，请检查错误信息")
            return False

def main():
    installer = VideoToTextInstaller()
    success = installer.run_installation()
    
    if success:
        print("\n" + "=" * 60)
        print("  安装完成！现在可以开始使用视频语音转文本工具")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("  安装失败！请检查错误信息并重试")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()