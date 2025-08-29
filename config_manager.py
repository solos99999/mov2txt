#!/usr/bin/env python3
"""
sherpa-ncnn配置管理模块
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.available_models = self._scan_available_models()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_file.exists():
            print(f"配置文件不存在: {self.config_file}")
            print("创建默认配置...")
            return self._create_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"配置文件加载成功: {self.config_file}")
            return config
        except Exception as e:
            print(f"配置文件加载失败: {e}")
            print("使用默认配置...")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        default_config = {
            "models": {
                "chinese": {
                    "name": "中文模型",
                    "description": "优化的中文语音识别模型",
                    "model_dir": "sherpa-ncnn-master",
                    "files": {
                        "tokens": "sherpa-ncnn-master/python-api-examples/AudioSer/model/tokens.txt",
                        "encoder_param": "sherpa-ncnn-master/python-api-examples/AudioSer/model/encoder_jit_trace-pnnx.ncnn.param",
                        "encoder_bin": "sherpa-ncnn-master/python-api-examples/AudioSer/model/encoder_jit_trace-pnnx.ncnn.bin",
                        "decoder_param": "sherpa-ncnn-master/python-api-examples/AudioSer/model/decoder_jit_trace-pnnx.ncnn.param",
                        "decoder_bin": "sherpa-ncnn-master/python-api-examples/AudioSer/model/decoder_jit_trace-pnnx.ncnn.bin",
                        "joiner_param": "sherpa-ncnn-master/python-api-examples/AudioSer/model/joiner_jit_trace-pnnx.ncnn.param",
                        "joiner_bin": "sherpa-ncnn-master/python-api-examples/AudioSer/model/joiner_jit_trace-pnnx.ncnn.bin"
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
                "hotwords_score": 1.5,
                "endpoint_rules": {
                    "rule1_min_trailing_silence": 2.4,
                    "rule2_min_trailing_silence": 1.2,
                    "rule3_min_utterance_length": 20
                }
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
        
        # 保存默认配置
        self.save_config(default_config)
        return default_config
    
    def _scan_available_models(self) -> Dict[str, bool]:
        """扫描可用的模型"""
        available = {}
        
        for model_id, model_config in self.config.get("models", {}).items():
            files = model_config.get("files", {})
            all_files_exist = True
            
            for file_type, file_path in files.items():
                if not Path(file_path).exists():
                    print(f"模型 {model_id} 缺少文件: {file_path}")
                    all_files_exist = False
                    break
            
            available[model_id] = all_files_exist
            
            if all_files_exist:
                print(f"模型 {model_id} ({model_config['name']}) 可用")
            else:
                print(f"模型 {model_id} ({model_config['name']}) 不可用")
        
        return available
    
    def get_model_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """获取模型配置"""
        models = self.config.get("models", {})
        return models.get(model_id)
    
    def get_recognition_config(self) -> Dict[str, Any]:
        """获取识别配置"""
        return self.config.get("recognition", {})
    
    def get_audio_config(self) -> Dict[str, Any]:
        """获取音频配置"""
        return self.config.get("audio", {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """获取输出配置"""
        return self.config.get("output", {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        return self.config.get("performance", {})
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        rec_config = self.get_recognition_config()
        default_model = rec_config.get("default_model", "chinese")
        
        # 如果默认模型不可用，尝试找到第一个可用模型
        if default_model not in self.available_models or not self.available_models[default_model]:
            for model_id, is_available in self.available_models.items():
                if is_available:
                    print(f"默认模型 {default_model} 不可用，使用 {model_id}")
                    return model_id
            
            print("没有可用的模型")
            return ""
        
        return default_model
    
    def list_models(self) -> List[Dict[str, Any]]:
        """列出所有模型"""
        models = []
        
        for model_id, model_config in self.config.get("models", {}).items():
            is_available = self.available_models.get(model_id, False)
            models.append({
                "id": model_id,
                "name": model_config.get("name", ""),
                "description": model_config.get("description", ""),
                "language": model_config.get("language", ""),
                "available": is_available,
                "sample_rate": model_config.get("sample_rate", 16000)
            })
        
        return models
    
    def add_model(self, model_id: str, model_config: Dict[str, Any]) -> bool:
        """添加模型配置"""
        try:
            self.config["models"][model_id] = model_config
            self.available_models = self._scan_available_models()
            self.save_config()
            print(f"模型 {model_id} 添加成功")
            return True
        except Exception as e:
            print(f"添加模型失败: {e}")
            return False
    
    def remove_model(self, model_id: str) -> bool:
        """删除模型配置"""
        try:
            if model_id in self.config["models"]:
                del self.config["models"][model_id]
                self.available_models = self._scan_available_models()
                self.save_config()
                print(f"模型 {model_id} 删除成功")
                return True
            else:
                print(f"模型 {model_id} 不存在")
                return False
        except Exception as e:
            print(f"删除模型失败: {e}")
            return False
    
    def update_config(self, section: str, key: str, value: Any) -> bool:
        """更新配置"""
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = value
            self.save_config()
            print(f"配置更新成功: {section}.{key} = {value}")
            return True
        except Exception as e:
            print(f"配置更新失败: {e}")
            return False
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """保存配置"""
        try:
            if config is None:
                config = self.config
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"配置保存成功: {self.config_file}")
            return True
        except Exception as e:
            print(f"配置保存失败: {e}")
            return False
    
    def validate_config(self) -> bool:
        """验证配置"""
        print("验证配置...")
        
        # 检查必需的配置项
        required_sections = ["models", "recognition", "audio", "output", "performance"]
        for section in required_sections:
            if section not in self.config:
                print(f"缺少配置节: {section}")
                return False
        
        # 检查是否有可用模型
        if not any(self.available_models.values()):
            print("没有可用的模型")
            return False
        
        print("配置验证通过")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """获取配置状态"""
        return {
            "config_file": str(self.config_file),
            "config_exists": self.config_file.exists(),
            "models_count": len(self.config.get("models", {})),
            "available_models": sum(1 for v in self.available_models.values() if v),
            "default_model": self.get_default_model(),
            "validation_passed": self.validate_config()
        }
    
    def print_status(self):
        """打印配置状态"""
        status = self.get_status()
        
        print("=" * 50)
        print("配置状态")
        print("=" * 50)
        print(f"配置文件: {status['config_file']}")
        print(f"配置文件存在: {status['config_exists']}")
        print(f"模型总数: {status['models_count']}")
        print(f"可用模型数: {status['available_models']}")
        print(f"默认模型: {status['default_model']}")
        print(f"配置验证: {status['validation_passed']}")
        
        print("\n可用模型:")
        for model in self.list_models():
            status_text = "可用" if model["available"] else "不可用"
            print(f"  - {model['id']} ({model['name']}): {status_text}")


def main():
    """配置管理工具主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='sherpa-ncnn配置管理工具')
    parser.add_argument('--config', default='config.json', help='配置文件路径')
    parser.add_argument('--status', action='store_true', help='显示配置状态')
    parser.add_argument('--list-models', action='store_true', help='列出所有模型')
    parser.add_argument('--validate', action='store_true', help='验证配置')
    parser.add_argument('--default-model', help='设置默认模型')
    
    args = parser.parse_args()
    
    config_manager = ConfigManager(args.config)
    
    if args.status:
        config_manager.print_status()
    elif args.list_models:
        print("可用模型:")
        for model in config_manager.list_models():
            status_text = "可用" if model["available"] else "不可用"
            print(f"  {model['id']}: {model['name']} ({model['language']}) - {status_text}")
    elif args.validate:
        is_valid = config_manager.validate_config()
        sys.exit(0 if is_valid else 1)
    elif args.default_model:
        success = config_manager.update_config("recognition", "default_model", args.default_model)
        sys.exit(0 if success else 1)
    else:
        config_manager.print_status()


if __name__ == "__main__":
    main()