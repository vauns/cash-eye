# 测试环境配置指南

## 问题：OCR 模型下载失败

当你运行 OCR 相关测试时，可能会遇到以下错误：

```
No available model hosting platforms detected. Please check your network connection.
```

这是因为 PaddleOCR 在首次运行时需要从以下平台之一下载模型：
- HuggingFace (https://huggingface.co)
- ModelScope (https://modelscope.cn)
- AIStudio (https://aistudio.baidu.com)
- BOS (https://paddle-model-ecology.bj.bcebos.com)

## 解决方案

### 方案 1: 配置网络访问（推荐）

确保你的测试环境可以访问上述模型托管平台之一。

### 方案 2: 手动下载模型

1. 从以下位置之一手动下载 PaddleOCR 模型：
   - ModelScope: https://modelscope.cn/models
   - AIStudio: https://aistudio.baidu.com

2. 将模型放置到 PaddleOCR 的缓存目录：
   ```
   ~/.paddlex/  # Linux/Mac
   ```

3. 模型文件包括：
   - PP-OCRv5 文本检测模型
   - PP-OCRv5 文本识别模型
   - PP-LCNet 文本方向分类模型

### 方案 3: 使用 Mock 进行单元测试

对于 CI/CD 环境或无网络环境，可以修改测试使用 Mock：

```python
from unittest.mock import Mock, patch

@patch('services.ocr_service.PaddleOCR')
def test_with_mock(mock_paddle_ocr):
    mock_instance = Mock()
    mock_instance.ocr.return_value = [[
        [[[0, 0], [100, 0], [100, 50], [0, 50]],
         ('¥100.00', 0.95)]
    ]]
    mock_paddle_ocr.return_value = mock_instance

    # 运行测试
    service = OCRService()
    # ...
```

## 当前测试状态

### ✅ 可以运行的测试（不需要 OCR 模型）

```bash
# 图片预处理测试
pytest tests/unit/test_image_processor.py -v
```

**测试结果：**
- ✅ 4/4 个测试通过
- RGB 图片预处理
- 灰度图转换
- 大图片压缩
- 无效图片错误处理

### ⚠️ 需要模型的测试

```bash
# OCR 服务测试（需要下载模型）
pytest tests/unit/test_ocr_service.py -v

# API 集成测试（需要下载模型）
pytest tests/integration/test_api.py -v
```

这些测试需要：
1. PaddlePaddle 已安装 ✅ (已完成)
2. 网络连接可访问模型托管平台 ❌ (当前环境受限)
3. 或者已手动下载模型文件

## 完整的测试步骤（有网络环境）

```bash
# 1. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install paddlepaddle  # 如未自动安装

# 2. 生成测试图片
cd tests/fixtures
python generate_test_images.py
cd ../..

# 3. 运行所有测试
pytest tests/ -v

# 或分别运行
pytest tests/unit/test_image_processor.py -v  # 无需模型
pytest tests/unit/test_ocr_service.py -v      # 需要模型
pytest tests/integration/test_api.py -v       # 需要模型
```

## 测试覆盖范围

### 图片预处理 (test_image_processor.py) - ✅ 全部通过
- RGB 格式转换
- 灰度图处理
- 大图压缩 (>2048px)
- 错误处理

### OCR 服务 (test_ocr_service.py) - ⏳ 等待模型下载
- OCR 引擎初始化
- 基础金额识别
- 货币符号处理（¥, $, ￥）
- 千位分隔符支持
- 多种图片格式（JPEG, PNG, BMP）
- 低质量图片处理
- 无文本图片处理
- 错误处理
- 性能测试

### API 集成测试 (test_api.py) - ⏳ 等待模型下载
- 健康检查端点
- 单张图片识别
- 批量图片识别
- 文件格式验证
- 错误处理
- CORS 头验证
- 性能测试

## 快速验证测试代码

如果暂时无法下载模型，可以先验证测试代码本身是否正确：

```bash
# 检查测试文件语法
python -m py_compile tests/unit/test_ocr_service.py
python -m py_compile tests/integration/test_api.py

# 收集测试用例（不运行）
pytest tests/ --collect-only

# 运行不需要模型的测试
pytest tests/unit/test_image_processor.py -v
```

## 故障排除

### 问题：ImportError: No module named 'paddle'
**解决：**
```bash
pip install paddlepaddle
```

### 问题：ValueError: Unknown argument: use_gpu
**解决：** 已修复。PaddleOCR 3.3.1+ 不再支持 `use_gpu` 参数。

### 问题：ValueError: Unknown argument: show_log
**解决：** 已修复。PaddleOCR 3.3.1+ 不再支持 `show_log` 参数。

### 问题：TestClient 初始化错误
**状态：** 可能是 httpx/starlette 版本兼容性问题，需进一步调查。

## 建议

### 对于本地开发
- 确保网络连接，让 PaddleOCR 自动下载模型
- 首次运行会较慢（下载模型），之后会使用缓存

### 对于 CI/CD
- 考虑使用 Docker 镜像预装模型
- 或使用 Mock 进行单元测试
- 集成测试可以在有网络的环境中运行

### 对于离线环境
- 提前在有网络的机器上运行一次，模型会缓存到 `~/.paddlex/`
- 将整个 `~/.paddlex/` 目录打包，复制到离线环境

## 相关文档

- [PaddleOCR 文档](https://github.com/PaddlePaddle/PaddleOCR)
- [测试 README](./README.md)
- [项目 README](../README.md)

## 总结

✅ **测试代码已全部编写完成**
✅ **测试图片已生成**
✅ **图片处理测试全部通过**
✅ **PaddlePaddle 已安装**
⏳ **OCR/API 测试等待模型下载**

一旦网络环境允许下载模型，所有测试应该可以正常运行。
