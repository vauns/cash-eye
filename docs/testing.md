# 测试指南

本文档介绍如何运行和编写 Cash Eye 项目的测试。

## 目录

- [测试概览](#测试概览)
- [快速开始](#快速开始)
- [测试结构](#测试结构)
- [运行测试](#运行测试)
- [测试覆盖](#测试覆盖)
- [编写测试](#编写测试)
- [测试环境配置](#测试环境配置)
- [持续集成](#持续集成)

## 测试概览

项目包含完整的测试套件，涵盖：

- **单元测试**: 测试独立模块和函数
- **集成测试**: 测试 API 接口和组件交互
- **性能测试**: 验证响应时间和资源使用

**测试框架**: pytest

## 快速开始

### 1. 安装依赖

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装测试依赖
pip install -r requirements-dev.txt
```

### 2. 生成测试图片

```bash
cd tests/fixtures
python generate_test_images.py
cd ../..
```

### 3. 运行所有测试

```bash
pytest tests/ -v
```

## 测试结构

```
tests/
├── unit/                          # 单元测试
│   ├── test_image_processor.py   # 图片预处理测试
│   └── test_ocr_service.py       # OCR 服务测试
├── integration/                   # 集成测试
│   └── test_api.py               # API 端点测试
├── fixtures/                      # 测试数据
│   ├── images/                   # 测试图片
│   └── generate_test_images.py  # 图片生成脚本
└── conftest.py                   # Pytest 配置
```

## 运行测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行特定类型的测试

```bash
# 只运行单元测试
pytest tests/unit/ -v

# 只运行集成测试
pytest tests/integration/ -v
```

### 运行特定文件

```bash
# 运行 OCR 服务测试
pytest tests/unit/test_ocr_service.py -v

# 运行 API 测试
pytest tests/integration/test_api.py -v
```

### 运行特定测试函数

```bash
pytest tests/unit/test_ocr_service.py::test_recognize_amount_basic -v
```

### 显示详细输出

```bash
# 显示 print 语句
pytest tests/ -v -s

# 显示完整错误信息
pytest tests/ -v --tb=long
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看报告
open htmlcov/index.html
```

### 其他有用选项

```bash
# 并行运行测试（需要 pytest-xdist）
pytest tests/ -n auto

# 只运行失败的测试
pytest tests/ --lf

# 停在第一个失败
pytest tests/ -x

# 显示最慢的 10 个测试
pytest tests/ --durations=10

# 生成 JUnit XML 报告
pytest tests/ --junitxml=test-results.xml
```

## 测试覆盖

### 单元测试

#### test_image_processor.py

测试图片预处理功能：

- ✅ RGB 图片预处理
- ✅ 灰度图转 RGB
- ✅ 大图片压缩（>2048px）
- ✅ 无效图片错误处理

```bash
pytest tests/unit/test_image_processor.py -v
```

#### test_ocr_service.py

测试 OCR 服务核心功能：

- ✅ OCR 服务初始化
- ✅ 基础金额识别
- ✅ 货币符号处理（¥, $, ￥）
- ✅ 千位分隔符（1,234.56）
- ✅ 不同图片格式（JPEG, PNG, BMP）
- ✅ 低质量/模糊图片
- ✅ 无文本图片
- ✅ 无效路径错误处理
- ✅ 返回值结构验证
- ✅ 小数位处理
- ✅ 大额数字
- ✅ 性能测试

```bash
pytest tests/unit/test_ocr_service.py -v
```

### 集成测试

#### test_api.py

测试 API 端点：

**健康检查:**
- ✅ GET `/api/v1/health`

**单张图片识别:**
- ✅ POST `/api/v1/recognize` - 成功场景
- ✅ 不同图片格式（JPEG, PNG, BMP）
- ✅ 无文件上传错误
- ✅ 不支持的格式错误
- ✅ 各种金额格式
- ✅ 低置信度图片
- ✅ 无文本图片
- ✅ 响应时间验证
- ✅ 置信度范围验证

**批量图片识别:**
- ✅ POST `/api/v1/recognize/batch` - 多图片
- ✅ 单图片批量
- ✅ 空批量

**其他:**
- ✅ CORS 头检查
- ✅ 性能测试

```bash
pytest tests/integration/test_api.py -v
```

### 测试图片说明

| 文件名 | 内容 | 用途 |
|--------|------|------|
| `amount_100.jpg` | ¥100.00 | 基础测试 |
| `amount_1234.jpg` | ¥1234.56 | 多位数 |
| `amount_dollar_99.jpg` | $99.99 | 美元符号 |
| `amount_yuan_888.jpg` | ￥888.88 | 人民币符号 |
| `amount_comma_1234.jpg` | 1,234.56 | 千位分隔符 |
| `amount_50.jpg` | 50.00 | 简单数字 |
| `amount_0_01.jpg` | 0.01 | 小数测试 |
| `amount_large.jpg` | 999999.99 | 大额数字 |
| `amount_blurry.jpg` | ¥123.45 (模糊) | 低质量图片 |
| `no_text.jpg` | (空白) | 无文本场景 |
| `amount_200.png` | ¥200.00 | PNG 格式 |
| `amount_300.bmp` | ¥300.00 | BMP 格式 |

## 编写测试

### 单元测试示例

```python
# tests/unit/test_my_module.py
import pytest
from src.services.my_service import MyService

def test_basic_functionality():
    """测试基本功能"""
    service = MyService()
    result = service.process("input")
    assert result is not None
    assert result == "expected_output"

def test_error_handling():
    """测试错误处理"""
    service = MyService()
    with pytest.raises(ValueError):
        service.process(None)

@pytest.mark.parametrize("input,expected", [
    ("input1", "output1"),
    ("input2", "output2"),
    ("input3", "output3"),
])
def test_multiple_inputs(input, expected):
    """参数化测试"""
    service = MyService()
    result = service.process(input)
    assert result == expected
```

### 集成测试示例

```python
# tests/integration/test_my_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_my_endpoint():
    """测试 API 端点"""
    response = client.post(
        "/api/v1/my-endpoint",
        json={"key": "value"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_error_response():
    """测试错误响应"""
    response = client.post(
        "/api/v1/my-endpoint",
        json={}  # 缺少必需字段
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
```

### 使用 Fixtures

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_image():
    """提供测试图片"""
    return "tests/fixtures/images/amount_100.jpg"

@pytest.fixture
def ocr_service():
    """提供 OCR 服务实例"""
    from src.services.ocr_service import OCRService
    return OCRService()

# 使用 fixture
def test_with_fixture(ocr_service, sample_image):
    result = ocr_service.recognize(sample_image)
    assert result is not None
```

## 测试环境配置

### PaddleOCR 模型下载

首次运行测试时，PaddleOCR 会下载模型文件（约 150MB）。

**如果遇到下载失败：**

#### 方案 1: 配置网络访问

确保可以访问以下平台之一：
- HuggingFace (https://huggingface.co)
- ModelScope (https://modelscope.cn)
- AIStudio (https://aistudio.baidu.com)
- BOS (https://paddle-model-ecology.bj.bcebos.com)

#### 方案 2: 手动下载模型

```bash
# 下载模型到本地
python scripts/download_models.py --model-dir ~/.paddleocr

# 或使用准备脚本
bash scripts/prepare_offline_deployment.sh
```

#### 方案 3: 使用 Mock（CI/CD 环境）

```python
from unittest.mock import Mock, patch

@patch('services.ocr_service.PaddleOCR')
def test_with_mock(mock_paddle_ocr):
    """使用 Mock 跳过模型加载"""
    mock_instance = Mock()
    mock_instance.ocr.return_value = [[
        [[[0, 0], [100, 0], [100, 50], [0, 50]],
         ('¥100.00', 0.95)]
    ]]
    mock_paddle_ocr.return_value = mock_instance

    # 运行测试...
```

### 测试分类

可以使用 pytest markers 对测试进行分类：

```python
# 标记慢速测试
@pytest.mark.slow
def test_slow_operation():
    pass

# 标记需要网络的测试
@pytest.mark.network
def test_with_network():
    pass

# 运行时跳过慢速测试
# pytest tests/ -v -m "not slow"
```

## 持续集成

### GitHub Actions 示例

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Generate test images
      run: |
        cd tests/fixtures
        python generate_test_images.py
        cd ../..

    - name: Run tests
      run: |
        pytest tests/ -v --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### GitLab CI 示例

```yaml
# .gitlab-ci.yml
test:
  image: python:3.10
  before_script:
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
    - cd tests/fixtures && python generate_test_images.py && cd ../..
  script:
    - pytest tests/ -v --cov=src --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## 故障排查

### 常见问题

**Q: ImportError: No module named 'paddle'**

A: 安装 PaddleOCR：
```bash
pip install paddleocr
```

**Q: 模型下载失败**

A: 参考 [测试环境配置](#测试环境配置) 中的解决方案。

**Q: 测试图片不存在**

A: 运行图片生成脚本：
```bash
cd tests/fixtures
python generate_test_images.py
```

**Q: 测试超时**

A: 增加超时时间或检查网络连接：
```bash
pytest tests/ -v --timeout=60
```

## 性能基准

- **单次 OCR 识别**: < 5000ms
- **API 响应时间**: < 10s (包括模型加载)
- **置信度范围**: 0.0 - 1.0

## 最佳实践

1. **运行前生成测试图片**: 确保测试数据完整
2. **使用虚拟环境**: 隔离依赖
3. **定期运行测试**: 在每次提交前运行
4. **关注覆盖率**: 保持高测试覆盖率
5. **编写清晰的测试**: 测试名称要描述性强
6. **使用 fixtures**: 复用测试数据和配置
7. **Mock 外部依赖**: 提高测试速度和可靠性

## 下一步

- 📖 查看 [API 使用文档](./api-usage.md) 了解 API 详情
- 🚀 阅读 [部署指南](./deployment.md) 了解部署方式
- ⚡ 参考 [性能优化](./performance.md) 提升性能

---

[返回文档首页](./README.md)
