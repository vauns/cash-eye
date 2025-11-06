# 贡献指南

感谢你对 Cash Eye 项目的关注！我们欢迎任何形式的贡献。

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [测试要求](#测试要求)
- [文档贡献](#文档贡献)

## 行为准则

参与本项目的所有贡献者都应遵守以下原则：

- 尊重不同的观点和经验
- 接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

## 如何贡献

### 报告 Bug

发现 Bug？请在 [Issues](https://github.com/your-org/cash-eye/issues) 页面提交报告，包含：

- **标题**: 简洁描述问题
- **环境信息**: 操作系统、Python 版本、Docker 版本等
- **复现步骤**: 详细的复现步骤
- **期望行为**: 你期望的正确行为
- **实际行为**: 实际发生的情况
- **日志/截图**: 相关的错误日志或截图

**Bug 报告模板**:
```markdown
## 环境信息
- OS: Ubuntu 20.04
- Python: 3.10.0
- Docker: 20.10.12
- Cash Eye: 1.0.0

## 复现步骤
1. 启动服务
2. 上传大于 10MB 的图片
3. 观察错误

## 期望行为
应该返回文件过大的错误提示

## 实际行为
服务崩溃

## 错误日志
```
[ERROR] ...
```
```

### 提出新功能

想要新功能？请先：

1. 在 [Issues](https://github.com/your-org/cash-eye/issues) 中搜索是否已有相关讨论
2. 如果没有，创建新的 Issue，说明：
   - 功能描述
   - 使用场景
   - 预期收益
   - 可能的实现方案

### 提交代码

1. **Fork 仓库**
2. **创建分支**: `git checkout -b feature/amazing-feature`
3. **开发功能**: 编写代码和测试
4. **提交更改**: `git commit -m 'Add amazing feature'`
5. **推送分支**: `git push origin feature/amazing-feature`
6. **创建 PR**: 开启 Pull Request

## 开发流程

### 1. 环境准备

```bash
# 克隆你的 fork
git clone https://github.com/YOUR_USERNAME/cash-eye.git
cd cash-eye

# 添加上游仓库
git remote add upstream https://github.com/your-org/cash-eye.git

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. 创建分支

分支命名规范：

- `feature/xxx` - 新功能
- `bugfix/xxx` - Bug 修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试相关

```bash
git checkout -b feature/add-currency-support
```

### 3. 开发

#### 代码开发

```bash
# 启动服务（开发模式）
python -m uvicorn main:app --reload

# 在另一个终端测试
curl http://localhost:8000/api/v1/health
```

#### 运行测试

```bash
# 生成测试图片
cd tests/fixtures
python generate_test_images.py
cd ../..

# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/unit/test_ocr_service.py -v

# 检查覆盖率
pytest tests/ --cov=src --cov-report=html
```

#### 代码检查

```bash
# 代码格式化
black src/ tests/

# 导入排序
isort src/ tests/

# 代码检查
flake8 src/ tests/
pylint src/

# 类型检查（如果使用 mypy）
mypy src/
```

### 4. 提交代码

#### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

**示例**:
```bash
feat(api): add support for TIFF format

- Add TIFF to supported formats list
- Update file validation logic
- Add tests for TIFF upload

Closes #123
```

#### 提交前检查

```bash
# 1. 确保所有测试通过
pytest tests/ -v

# 2. 代码格式化
black src/ tests/
isort src/ tests/

# 3. 代码检查
flake8 src/

# 4. 提交
git add .
git commit -m "feat(api): add support for TIFF format"
```

### 5. 创建 Pull Request

#### 推送到你的 Fork

```bash
git push origin feature/add-currency-support
```

#### 创建 PR

访问 GitHub 仓库，点击 "New Pull Request"，填写：

- **标题**: 清晰描述变更
- **描述**: 详细说明变更内容，包括：
  - 变更内容
  - 相关 Issue
  - 测试方法
  - 截图（如果适用）

**PR 模板**:
```markdown
## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能优化
- [ ] 重构

## 变更内容
简要描述你的变更...

## 相关 Issue
Closes #123

## 测试方法
1. 运行 `pytest tests/`
2. 手动测试：...

## 检查清单
- [ ] 代码通过所有测试
- [ ] 添加了新的测试
- [ ] 更新了文档
- [ ] 遵循代码规范
```

## 代码规范

### Python 代码风格

遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范：

```python
# 好的例子 ✅
def recognize_amount(image_path: str) -> Dict[str, Any]:
    """
    识别图片中的金额

    Args:
        image_path: 图片路径

    Returns:
        包含金额和置信度的字典
    """
    result = ocr_service.process(image_path)
    return {
        "amount": result.amount,
        "confidence": result.confidence
    }

# 不好的例子 ❌
def recognizeAmount(imagePath):
    result=ocrService.process(imagePath)
    return {"amount":result.amount,"confidence":result.confidence}
```

### 命名规范

- **变量/函数**: `snake_case`
- **类**: `PascalCase`
- **常量**: `UPPER_SNAKE_CASE`
- **私有成员**: `_leading_underscore`

```python
# 变量和函数
image_path = "test.jpg"
def process_image(image_path):
    pass

# 类
class OCRService:
    pass

# 常量
MAX_FILE_SIZE = 10 * 1024 * 1024

# 私有成员
class MyClass:
    def __init__(self):
        self._private_var = None
```

### 文档字符串

使用 Google 风格的 docstring：

```python
def recognize_amount(
    image_path: str,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    识别图片中的金额信息

    Args:
        image_path: 图片文件路径
        timeout: 超时时间（秒），默认 10

    Returns:
        包含以下键的字典：
        - amount: 识别到的金额
        - confidence: 置信度 (0-1)
        - processing_time_ms: 处理时间（毫秒）

    Raises:
        FileNotFoundError: 图片文件不存在
        OCRError: OCR 识别失败

    Example:
        >>> result = recognize_amount("invoice.jpg")
        >>> print(result["amount"])
        "1234.56"
    """
    pass
```

### 类型注解

使用类型注解提高代码可读性：

```python
from typing import Dict, List, Optional, Any

def process_batch(
    images: List[str],
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    pass
```

## 测试要求

### 测试覆盖率

- 新功能必须包含测试
- 目标覆盖率：≥ 80%
- 关键功能：100%

### 编写测试

```python
import pytest
from src.services.ocr_service import OCRService

def test_recognize_amount_basic():
    """测试基本金额识别"""
    service = OCRService()
    result = service.recognize("tests/fixtures/images/amount_100.jpg")

    assert result is not None
    assert result["amount"] == "100.00"
    assert result["confidence"] > 0.8

def test_recognize_amount_invalid_path():
    """测试无效路径"""
    service = OCRService()

    with pytest.raises(FileNotFoundError):
        service.recognize("nonexistent.jpg")
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/unit/test_ocr_service.py::test_recognize_amount_basic -v

# 检查覆盖率
pytest tests/ --cov=src --cov-report=term-missing
```

## 文档贡献

### 文档类型

- **README**: 项目概览
- **docs/**: 详细文档
- **API 文档**: 代码注释自动生成
- **CHANGELOG**: 版本更新记录

### 文档风格

- 使用 Markdown 格式
- 简洁清晰
- 包含示例代码
- 保持更新

### 更新文档

修改代码时，确保更新相关文档：

1. 代码注释和 docstring
2. README（如果影响使用）
3. docs/ 中的相关文档
4. CHANGELOG（记录变更）

## 代码审查

### 审查清单

PR 提交后，维护者会审查：

- [ ] 代码质量
- [ ] 测试覆盖
- [ ] 文档完整性
- [ ] 性能影响
- [ ] 向后兼容性

### 响应审查意见

- 及时回复审查意见
- 根据反馈修改代码
- 通过评论讨论不明确的地方

## 发布流程

（仅维护者）

1. 更新版本号
2. 更新 CHANGELOG
3. 创建 Git tag
4. 构建 Docker 镜像
5. 发布到 GitHub Releases

## 获取帮助

需要帮助？

- 💬 在 Issue 中提问
- 📧 发送邮件至 dev@example.com
- 📖 查看 [文档](./docs)

## 致谢

感谢所有贡献者！

- 查看 [贡献者列表](https://github.com/your-org/cash-eye/graphs/contributors)
- 你的名字也可以出现在这里！

---

再次感谢你的贡献！🎉
