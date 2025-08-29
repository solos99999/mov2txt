#!/usr/bin/env python3
"""
sherpa-ncnn图形化配置管理工具
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import sys
from pathlib import Path
from config_manager import ConfigManager


class ConfigGUI:
    """配置管理图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("sherpa-ncnn 配置管理工具")
        self.root.geometry("800x600")
        
        self.config_manager = ConfigManager()
        self.current_config = self.config_manager.config.copy()
        
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 模型配置选项卡
        model_frame = ttk.Frame(notebook)
        notebook.add(model_frame, text="模型配置")
        self.setup_model_tab(model_frame)
        
        # 识别配置选项卡
        recognition_frame = ttk.Frame(notebook)
        notebook.add(recognition_frame, text="识别配置")
        self.setup_recognition_tab(recognition_frame)
        
        # 音频配置选项卡
        audio_frame = ttk.Frame(notebook)
        notebook.add(audio_frame, text="音频配置")
        self.setup_audio_tab(audio_frame)
        
        # 输出配置选项卡
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="输出配置")
        self.setup_output_tab(output_frame)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置配置", command=self.reset_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="验证配置", command=self.validate_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新状态", command=self.refresh_status).pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.update_status("配置已加载")
    
    def setup_model_tab(self, parent):
        """设置模型配置选项卡"""
        # 模型列表框架
        list_frame = ttk.LabelFrame(parent, text="可用模型", padding="10")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 模型列表
        self.model_listbox = tk.Listbox(list_frame, height=8)
        self.model_listbox.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.model_listbox.bind('<<ListboxSelect>>', self.on_model_select)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.model_listbox.yview)
        scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
        self.model_listbox.config(yscrollcommand=scrollbar.set)
        
        # 模型详情框架
        detail_frame = ttk.LabelFrame(parent, text="模型详情", padding="10")
        detail_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 模型ID
        ttk.Label(detail_frame, text="模型ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.model_id_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.model_id_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 模型名称
        ttk.Label(detail_frame, text="模型名称:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.model_name_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.model_name_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 模型描述
        ttk.Label(detail_frame, text="模型描述:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.model_desc_var = tk.StringVar()
        ttk.Entry(detail_frame, textvariable=self.model_desc_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 模型目录
        ttk.Label(detail_frame, text="模型目录:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.model_dir_var = tk.StringVar()
        dir_frame = ttk.Frame(detail_frame)
        dir_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        ttk.Entry(dir_frame, textvariable=self.model_dir_var, width=25).pack(side=tk.LEFT)
        ttk.Button(dir_frame, text="浏览", command=self.browse_model_dir).pack(side=tk.LEFT, padx=5)
        
        # 采样率
        ttk.Label(detail_frame, text="采样率:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.sample_rate_var = tk.StringVar(value="16000")
        ttk.Entry(detail_frame, textvariable=self.sample_rate_var, width=30).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 语言
        ttk.Label(detail_frame, text="语言:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.language_var = tk.StringVar()
        ttk.Combobox(detail_frame, textvariable=self.language_var, 
                     values=["chinese", "english", "multilingual"], width=27).grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 模型文件配置
        file_frame = ttk.LabelFrame(detail_frame, text="模型文件", padding="5")
        file_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.file_vars = {}
        files = [
            ("tokens", "tokens.txt"),
            ("encoder_param", "encoder.ncnn.param"),
            ("encoder_bin", "encoder.ncnn.bin"),
            ("decoder_param", "decoder.ncnn.param"),
            ("decoder_bin", "decoder.ncnn.bin"),
            ("joiner_param", "joiner.ncnn.param"),
            ("joiner_bin", "joiner.ncnn.bin")
        ]
        
        for i, (key, default_name) in enumerate(files):
            ttk.Label(file_frame, text=f"{default_name}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            var = tk.StringVar()
            self.file_vars[key] = var
            
            file_entry_frame = ttk.Frame(file_frame)
            file_entry_frame.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2)
            
            ttk.Entry(file_entry_frame, textvariable=var, width=30).pack(side=tk.LEFT)
            ttk.Button(file_entry_frame, text="浏览", 
                       command=lambda k=key: self.browse_model_file(k)).pack(side=tk.LEFT, padx=5)
        
        # 模型操作按钮
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="添加模型", command=self.add_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="更新模型", command=self.update_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除模型", command=self.delete_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="设为默认", command=self.set_default_model).pack(side=tk.LEFT, padx=5)
    
    def setup_recognition_tab(self, parent):
        """设置识别配置选项卡"""
        # 创建配置项
        config_items = [
            ("默认模型", "default_model", "combobox", ["chinese", "english", "multilingual"]),
            ("线程数", "num_threads", "spinbox", (1, 16)),
            ("解码方法", "decoding_method", "combobox", ["greedy_search", "modified_beam_search"]),
            ("启用端点检测", "enable_endpoint_detection", "checkbutton", None),
            ("块大小(秒)", "chunk_size", "entry", None),
            ("热词文件", "hotwords_file", "file", None),
            ("热词分数", "hotwords_score", "entry", None),
        ]
        
        self.recognition_vars = {}
        
        for i, (label, key, widget_type, options) in enumerate(config_items):
            ttk.Label(parent, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)
            
            if widget_type == "combobox":
                var = tk.StringVar()
                self.recognition_vars[key] = var
                ttk.Combobox(parent, textvariable=var, values=options, width=20).grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
            elif widget_type == "spinbox":
                var = tk.StringVar()
                self.recognition_vars[key] = var
                ttk.Spinbox(parent, from_=options[0], to=options[1], textvariable=var, width=18).grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
            elif widget_type == "checkbutton":
                var = tk.BooleanVar()
                self.recognition_vars[key] = var
                ttk.Checkbutton(parent, variable=var).grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
            elif widget_type == "file":
                var = tk.StringVar()
                self.recognition_vars[key] = var
                file_frame = ttk.Frame(parent)
                file_frame.grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
                ttk.Entry(file_frame, textvariable=var, width=15).pack(side=tk.LEFT)
                ttk.Button(file_frame, text="浏览", command=lambda k=key: self.browse_file(k, self.recognition_vars)).pack(side=tk.LEFT, padx=5)
            else:  # entry
                var = tk.StringVar()
                self.recognition_vars[key] = var
                ttk.Entry(parent, textvariable=var, width=20).grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
    
    def setup_audio_tab(self, parent):
        """设置音频配置选项卡"""
        config_items = [
            ("采样率", "sample_rate", "spinbox", (8000, 48000)),
            ("声道数", "channels", "spinbox", (1, 2)),
            ("采样宽度", "sample_width", "spinbox", (1, 4)),
            ("编码格式", "codec", "combobox", ["pcm_s16le", "pcm_s16be", "pcm_f32le"]),
        ]
        
        self.audio_vars = {}
        
        for i, (label, key, widget_type, options) in enumerate(config_items):
            ttk.Label(parent, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)
            
            if widget_type == "combobox":
                var = tk.StringVar()
                self.audio_vars[key] = var
                ttk.Combobox(parent, textvariable=var, values=options, width=20).grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
            elif widget_type == "spinbox":
                var = tk.StringVar()
                self.audio_vars[key] = var
                ttk.Spinbox(parent, from_=options[0], to=options[1], textvariable=var, width=18).grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
    
    def setup_output_tab(self, parent):
        """设置输出配置选项卡"""
        config_items = [
            ("输出格式", "format", "combobox", ["txt", "srt", "vtt"]),
            ("文件编码", "encoding", "combobox", ["utf-8", "gbk", "ascii"]),
            ("保存时间戳", "save_timestamps", "checkbutton", None),
            ("保存置信度", "save_confidence", "checkbutton", None),
        ]
        
        self.output_vars = {}
        
        for i, (label, key, widget_type, options) in enumerate(config_items):
            ttk.Label(parent, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)
            
            if widget_type == "combobox":
                var = tk.StringVar()
                self.output_vars[key] = var
                ttk.Combobox(parent, textvariable=var, values=options, width=20).grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
            elif widget_type == "checkbutton":
                var = tk.BooleanVar()
                self.output_vars[key] = var
                ttk.Checkbutton(parent, variable=var).grid(row=i, column=1, sticky=tk.W, pady=5, padx=5)
    
    def load_config(self):
        """加载配置到界面"""
        # 加载模型列表
        self.model_listbox.delete(0, tk.END)
        for model_id, model_config in self.current_config.get("models", {}).items():
            status = "可用" if self.config_manager.available_models.get(model_id, False) else "不可用"
            self.model_listbox.insert(tk.END, f"{model_id} - {model_config.get('name', '')} ({status})")
        
        # 加载识别配置
        rec_config = self.current_config.get("recognition", {})
        for key, var in self.recognition_vars.items():
            if key in rec_config:
                var.set(rec_config[key])
        
        # 加载音频配置
        audio_config = self.current_config.get("audio", {})
        for key, var in self.audio_vars.items():
            if key in audio_config:
                var.set(audio_config[key])
        
        # 加载输出配置
        output_config = self.current_config.get("output", {})
        for key, var in self.output_vars.items():
            if key in output_config:
                var.set(output_config[key])
    
    def on_model_select(self, event):
        """模型选择事件"""
        selection = self.model_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        model_ids = list(self.current_config.get("models", {}).keys())
        if index < len(model_ids):
            model_id = model_ids[index]
            model_config = self.current_config["models"][model_id]
            
            # 填充模型详情
            self.model_id_var.set(model_id)
            self.model_name_var.set(model_config.get("name", ""))
            self.model_desc_var.set(model_config.get("description", ""))
            self.model_dir_var.set(model_config.get("model_dir", ""))
            self.sample_rate_var.set(str(model_config.get("sample_rate", 16000)))
            self.language_var.set(model_config.get("language", ""))
            
            # 填充文件路径
            files = model_config.get("files", {})
            for key, var in self.file_vars.items():
                var.set(files.get(key, ""))
    
    def browse_model_dir(self):
        """浏览模型目录"""
        directory = filedialog.askdirectory(title="选择模型目录")
        if directory:
            self.model_dir_var.set(directory)
    
    def browse_model_file(self, file_key):
        """浏览模型文件"""
        filename = filedialog.askopenfilename(title=f"选择{file_key}文件")
        if filename:
            self.file_vars[file_key].set(filename)
    
    def browse_file(self, file_key, var_dict):
        """浏览文件"""
        filename = filedialog.askopenfilename(title=f"选择{file_key}文件")
        if filename:
            var_dict[file_key].set(filename)
    
    def add_model(self):
        """添加模型"""
        model_id = self.model_id_var.get().strip()
        if not model_id:
            messagebox.showerror("错误", "请输入模型ID")
            return
        
        if model_id in self.current_config.get("models", {}):
            messagebox.showerror("错误", "模型ID已存在")
            return
        
        # 创建模型配置
        model_config = {
            "name": self.model_name_var.get(),
            "description": self.model_desc_var.get(),
            "model_dir": self.model_dir_var.get(),
            "sample_rate": int(self.sample_rate_var.get()),
            "language": self.language_var.get(),
            "files": {}
        }
        
        # 添加文件路径
        for key, var in self.file_vars.items():
            file_path = var.get().strip()
            if file_path:
                model_config["files"][key] = file_path
        
        # 添加到配置
        if "models" not in self.current_config:
            self.current_config["models"] = {}
        
        self.current_config["models"][model_id] = model_config
        
        # 刷新模型列表
        self.load_config()
        self.update_status(f"模型 {model_id} 已添加")
    
    def update_model(self):
        """更新模型"""
        selection = self.model_listbox.curselection()
        if not selection:
            messagebox.showerror("错误", "请选择要更新的模型")
            return
        
        index = selection[0]
        model_ids = list(self.current_config.get("models", {}).keys())
        if index >= len(model_ids):
            return
        
        old_model_id = model_ids[index]
        new_model_id = self.model_id_var.get().strip()
        
        if not new_model_id:
            messagebox.showerror("错误", "请输入模型ID")
            return
        
        # 如果ID改变，删除旧模型
        if old_model_id != new_model_id:
            if new_model_id in self.current_config.get("models", {}):
                messagebox.showerror("错误", "新模型ID已存在")
                return
            del self.current_config["models"][old_model_id]
        
        # 更新模型配置
        model_config = {
            "name": self.model_name_var.get(),
            "description": self.model_desc_var.get(),
            "model_dir": self.model_dir_var.get(),
            "sample_rate": int(self.sample_rate_var.get()),
            "language": self.language_var.get(),
            "files": {}
        }
        
        # 更新文件路径
        for key, var in self.file_vars.items():
            file_path = var.get().strip()
            if file_path:
                model_config["files"][key] = file_path
        
        # 保存配置
        self.current_config["models"][new_model_id] = model_config
        
        # 刷新模型列表
        self.load_config()
        self.update_status(f"模型 {new_model_id} 已更新")
    
    def delete_model(self):
        """删除模型"""
        selection = self.model_listbox.curselection()
        if not selection:
            messagebox.showerror("错误", "请选择要删除的模型")
            return
        
        index = selection[0]
        model_ids = list(self.current_config.get("models", {}).keys())
        if index >= len(model_ids):
            return
        
        model_id = model_ids[index]
        
        if messagebox.askyesno("确认", f"确定要删除模型 {model_id} 吗？"):
            del self.current_config["models"][model_id]
            self.load_config()
            self.update_status(f"模型 {model_id} 已删除")
    
    def set_default_model(self):
        """设置默认模型"""
        selection = self.model_listbox.curselection()
        if not selection:
            messagebox.showerror("错误", "请选择要设为默认的模型")
            return
        
        index = selection[0]
        model_ids = list(self.current_config.get("models", {}).keys())
        if index >= len(model_ids):
            return
        
        model_id = model_ids[index]
        
        if "recognition" not in self.current_config:
            self.current_config["recognition"] = {}
        
        self.current_config["recognition"]["default_model"] = model_id
        self.load_config()
        self.update_status(f"默认模型已设置为 {model_id}")
    
    def save_config(self):
        """保存配置"""
        # 保存识别配置
        if "recognition" not in self.current_config:
            self.current_config["recognition"] = {}
        
        for key, var in self.recognition_vars.items():
            value = var.get()
            if isinstance(value, bool):
                self.current_config["recognition"][key] = value
            elif value:
                self.current_config["recognition"][key] = value
        
        # 保存音频配置
        if "audio" not in self.current_config:
            self.current_config["audio"] = {}
        
        for key, var in self.audio_vars.items():
            value = var.get()
            if value:
                try:
                    self.current_config["audio"][key] = int(value)
                except ValueError:
                    self.current_config["audio"][key] = value
        
        # 保存输出配置
        if "output" not in self.current_config:
            self.current_config["output"] = {}
        
        for key, var in self.output_vars.items():
            value = var.get()
            if isinstance(value, bool):
                self.current_config["output"][key] = value
            elif value:
                self.current_config["output"][key] = value
        
        # 保存到文件
        if self.config_manager.save_config(self.current_config):
            messagebox.showinfo("成功", "配置保存成功")
            self.update_status("配置已保存")
        else:
            messagebox.showerror("错误", "配置保存失败")
    
    def reset_config(self):
        """重置配置"""
        if messagebox.askyesno("确认", "确定要重置为默认配置吗？"):
            self.current_config = self.config_manager._create_default_config()
            self.load_config()
            self.update_status("配置已重置")
    
    def validate_config(self):
        """验证配置"""
        # 临时保存当前配置
        temp_config = self.current_config.copy()
        
        # 保存当前界面设置
        self.save_config()
        
        # 验证配置
        if self.config_manager.validate_config():
            messagebox.showinfo("验证结果", "配置验证通过")
            self.update_status("配置验证通过")
        else:
            messagebox.showerror("验证结果", "配置验证失败")
            self.update_status("配置验证失败")
    
    def refresh_status(self):
        """刷新状态"""
        self.config_manager = ConfigManager()
        self.current_config = self.config_manager.config.copy()
        self.load_config()
        self.update_status("状态已刷新")
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)


def main():
    """主函数"""
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()