# sherpa-ncnn 模型下载指南

## 当前状态
✅ **程序安装成功** - sherpa-ncnn已正确安装
✅ **配置文件正常** - config.json已创建
⚠️ **需要下载模型** - 模型文件尚未下载

## 模型下载步骤

### 1. 访问模型下载页面
打开浏览器访问：https://github.com/k2-fsa/sherpa-ncnn/releases/tag/models

### 2. 下载推荐模型

#### 中文模型（推荐）
- **文件名**: `sherpa-ncnn-conv-emformer-transducer-2023-06-26.tar.bz2`
- **大小**: 约50MB
- **语言**: 中文
- **特点**: 优化的中文语音识别

#### 英文模型
- **文件名**: `sherpa-ncnn-conv-emformer-transducer-2022-12-06.tar.bz2`
- **大小**: 约50MB
- **语言**: 英文
- **特点**: 高质量英文语音识别

#### 多语言模型
- **文件名**: `sherpa-ncnn-conv-emformer-transducer-multilingual-2023-06-26.tar.bz2`
- **大小**: 约50MB
- **语言**: 中英文混合
- **特点**: 支持多语言识别

### 3. 解压模型文件

下载完成后，将压缩文件解压到当前目录（`F:\git\mp42txt`）。

例如，解压中文模型后，目录结构应该是：
```
F:\git\mp42txt\
├── sherpa-ncnn-conv-emformer-transducer-2023-06-26\
│   ├── tokens.txt
│   ├── encoder.ncnn.param
│   ├── encoder.ncnn.bin
│   ├── decoder.ncnn.param
│   ├── decoder.ncnn.bin
│   ├── joiner.ncnn.param
│   ├── joiner.ncnn.bin
│   └── test_wavs\
└── 其他文件...
```

### 4. 验证模型安装

下载并解压模型后，运行以下命令验证：

```bash
# 检查配置状态
python sherpa_ncnn_video_to_text.py --status

# 列出可用模型
python sherpa_ncnn_video_to_text.py --list-models
```

## 快速测试

### 准备测试视频
将一个视频文件（如MP4、AVI等）放到当前目录，或使用现有的测试文件。

### 运行转换
```bash
# 转换视频文件
python sherpa_ncnn_video_to_text.py "你的视频文件.mp4"
```

## 故障排除

### 问题1: 模型文件下载失败
- 检查网络连接
- 尝试使用不同的浏览器
- 如果下载速度慢，可以尝试使用下载工具

### 问题2: 解压失败
- 确保下载的文件完整
- 尝试使用不同的解压工具（如7-Zip、WinRAR等）
- 确保有足够的磁盘空间

### 问题3: 模型文件不完整
- 重新下载模型文件
- 检查解压后的目录是否包含所有必需文件

### 问题4: 程序找不到模型
- 确保模型文件解压到正确的目录
- 检查文件路径是否正确
- 运行状态检查命令查看详细信息

## 获取帮助

如果遇到问题：
1. 运行 `python sherpa_ncnn_video_to_text.py --status` 查看详细状态
2. 运行 `python setup_wizard.py` 重新运行设置向导
3. 查看README_CONFIG.md获取完整使用说明

---

**下一步：下载模型文件后，您就可以开始使用sherpa-ncnn进行视频转文本了！**