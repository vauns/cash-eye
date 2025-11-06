# 更新日志

本项目的所有重要变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 性能监控仪表板
- 多语言金额识别支持
- 批处理优化

## [1.0.0] - 2025-11-06

### 新增
- ✨ 基于 PaddleOCR v3.3.1 (PP-OCRv5) 的金额识别功能
- ✨ RESTful API 接口（单张和批量识别）
- ✨ Docker 容器化部署支持
- ✨ 离线环境部署方案
- ✨ 结构化日志输出（structlog）
- ✨ 健康检查接口
- ✨ 完整的单元测试和集成测试
- 📝 完整的项目文档

### API 端点
- `GET /api/v1/health` - 健康检查
- `POST /api/v1/recognize` - 单张图片识别
- `POST /api/v1/recognize/batch` - 批量图片识别

### 支持的功能
- 支持 JPEG、PNG、BMP、TIFF 格式
- 支持多种货币符号（¥、￥、$）
- 支持千位分隔符（1,234.56）
- 返回置信度和处理时间
- 文件大小限制（10MB）
- 请求超时控制

### 文档
- README.md - 项目概览
- docs/getting-started.md - 快速开始指南
- docs/api-usage.md - API 使用文档
- docs/deployment.md - 部署指南
- docs/testing.md - 测试指南
- docs/performance.md - 性能优化
- docs/troubleshooting.md - 问题排查
- CONTRIBUTING.md - 贡献指南
- CHANGELOG.md - 更新日志

### 技术栈
- Python 3.10+
- FastAPI 0.104+
- PaddleOCR 3.3.1
- Pillow 10.0+
- Uvicorn 0.24+
- structlog 23.1+

### 部署方式
- Docker 部署
- Docker Compose 部署
- 离线镜像部署
- 本地开发部署

## [0.2.0] - 2025-11-05

### 新增
- 🚀 离线部署支持
- 📦 模型打包脚本
- 🐳 Docker 离线构建支持（已合并到主 Dockerfile）
- 📝 离线部署文档

### 改进
- ⚡ 优化模型加载速度
- 🔧 改进环境变量配置
- 📊 增强日志输出

### 修复
- 🐛 修复大文件上传超时问题
- 🐛 修复 PaddleOCR 参数兼容性问题

## [0.1.0] - 2025-11-04

### 新增
- 🎉 项目初始化
- 🔨 基础 OCR 服务实现
- 🌐 基础 API 接口
- 🐳 Docker 支持
- 🧪 基础测试框架

### 功能
- 单张图片识别
- 基本的错误处理
- 简单的日志记录

---

## 版本说明

### 版本格式

版本号格式：`主版本号.次版本号.修订号`

- **主版本号**：不兼容的 API 变更
- **次版本号**：向后兼容的功能新增
- **修订号**：向后兼容的问题修复

### 变更类型

- `新增` - 新功能
- `改进` - 现有功能的改进
- `修复` - Bug 修复
- `移除` - 移除的功能
- `弃用` - 即将移除的功能
- `安全` - 安全相关的修复

## 致谢

感谢所有为本项目做出贡献的开发者！

[Unreleased]: https://github.com/your-org/cash-eye/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/cash-eye/releases/tag/v1.0.0
[0.2.0]: https://github.com/your-org/cash-eye/releases/tag/v0.2.0
[0.1.0]: https://github.com/your-org/cash-eye/releases/tag/v0.1.0
