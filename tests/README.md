# 测试文档 (Test Documentation)

## 概述 (Overview)

本目录包含 cash-eye 项目的完整测试套件，涵盖单元测试和集成测试。

## 测试结构 (Test Structure)

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

## 快速开始 (Quick Start)

### 1. 安装依赖 (Install Dependencies)

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 2. 生成测试图片 (Generate Test Images)

```bash
cd tests/fixtures
python generate_test_images.py
```

### 3. 运行所有测试 (Run All Tests)

```bash
# 从项目根目录运行
pytest tests/ -v

# 或按照 CLAUDE.md 的指引
cd src
pytest ../tests/ -v
```

### 4. 运行特定测试 (Run Specific Tests)

```bash
# 只运行单元测试
pytest tests/unit/ -v

# 只运行集成测试
pytest tests/integration/ -v

# 运行特定文件
pytest tests/unit/test_ocr_service.py -v

# 运行特定测试函数
pytest tests/unit/test_ocr_service.py::test_recognize_amount_basic -v
```

## 测试覆盖 (Test Coverage)

### 单元测试 (Unit Tests)

#### test_image_processor.py
- ✅ RGB 图片预处理
- ✅ 灰度图转 RGB
- ✅ 大图片压缩（>2048px）
- ✅ 无效图片错误处理

#### test_ocr_service.py
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

### 集成测试 (Integration Tests)

#### test_api.py
- ✅ 健康检查端点 (`GET /api/v1/health`)
- ✅ 单张图片识别 (`POST /api/v1/recognize`)
  - 成功场景
  - 不同图片格式（JPEG, PNG, BMP）
  - 无文件上传
  - 不支持的格式
  - 各种金额格式
  - 低置信度图片
  - 无文本图片
  - 响应时间
  - 置信度范围验证
- ✅ 批量图片识别 (`POST /api/v1/recognize/batch`)
  - 多图片批量
  - 单图片批量
  - 空批量
- ✅ CORS 头检查
- ✅ 性能测试

## 测试图片说明 (Test Images Description)

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

## 测试命令选项 (Test Command Options)

```bash
# 显示详细输出
pytest tests/ -v

# 显示打印语句
pytest tests/ -v -s

# 运行并显示覆盖率
pytest tests/ --cov=src --cov-report=html

# 只运行失败的测试
pytest tests/ --lf

# 并行运行测试（需要 pytest-xdist）
pytest tests/ -n auto

# 生成 JUnit XML 报告
pytest tests/ --junitxml=test-results.xml

# 停在第一个失败
pytest tests/ -x

# 显示最慢的 10 个测试
pytest tests/ --durations=10
```

## 持续集成 (CI/CD)

测试可以集成到 CI/CD 流水线中：

```yaml
# GitHub Actions 示例
- name: Run tests
  run: |
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    cd tests/fixtures && python generate_test_images.py
    cd ../..
    pytest tests/ -v --junitxml=test-results.xml
```

## 编写新测试 (Writing New Tests)

### 单元测试示例

```python
import pytest
from services.ocr_service import OCRService

def test_my_feature():
    service = OCRService()
    result = service.my_method()
    assert result is not None
```

### 集成测试示例

```python
from fastapi.testclient import TestClient
from main import app

def test_my_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/my-endpoint")
    assert response.status_code == 200
```

## 常见问题 (FAQ)

### Q: 测试图片在哪里？
A: 运行 `python tests/fixtures/generate_test_images.py` 生成。

### Q: 测试失败怎么办？
A:
1. 确保已安装所有依赖
2. 确保测试图片已生成
3. 检查 PaddleOCR 模型是否正确下载
4. 查看详细错误信息

### Q: 如何跳过慢速测试？
A: 使用 pytest markers:
```bash
pytest tests/ -v -m "not slow"
```

### Q: 如何调试单个测试？
A: 使用 `pytest` 的调试选项：
```bash
pytest tests/unit/test_ocr_service.py::test_name -v -s --pdb
```

## 性能基准 (Performance Benchmarks)

- 单次 OCR 识别: < 5000ms
- API 响应时间: < 10s (包括模型加载)
- 置信度范围: 0.0 - 1.0

## 注意事项 (Notes)

1. **首次运行**: PaddleOCR 首次运行会下载模型，可能需要较长时间
2. **性能测试**: 性能测试的阈值设置较宽松，以适应不同硬件环境
3. **OCR 准确性**: OCR 结果可能因图片质量而异，测试主要验证功能而非精确结果
4. **测试图片**: 测试图片是程序生成的，与真实场景可能有差异

## 贡献指南 (Contributing)

添加新功能时，请：
1. 添加相应的单元测试
2. 如涉及 API 变更，添加集成测试
3. 确保所有测试通过
4. 更新本文档

## 相关文档 (Related Documentation)

- [项目 README](/README.md)
- [开发指南](/CLAUDE.md)
- [API 文档](http://localhost:8000/docs)
