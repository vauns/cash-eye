# Tests

Cash Eye 项目测试套件。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. 生成测试图片
cd tests/fixtures
python generate_test_images.py
cd ../..

# 3. 运行所有测试
pytest tests/ -v
```

## 测试结构

```
tests/
├── unit/                          # 单元测试
│   ├── test_image_processor.py   # 图片预处理
│   └── test_ocr_service.py       # OCR 服务
├── integration/                   # 集成测试
│   └── test_api.py               # API 接口
├── fixtures/                      # 测试数据
└── conftest.py                   # 配置
```

## 常用命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v

# 查看覆盖率
pytest tests/ --cov=src --cov-report=html
```

## 详细文档

完整的测试指南请查看 [测试文档](../docs/testing.md)，包括：

- 测试环境配置
- 编写新测试
- 测试覆盖率要求
- CI/CD 集成
- 故障排查

## 注意事项

⚠️ 首次运行时 PaddleOCR 会下载模型（约 150MB）。如果网络受限，请参考 [测试文档 - 环境配置](../docs/testing.md#测试环境配置)。

---

[查看完整测试文档](../docs/testing.md) | [返回项目主页](../README.md)
