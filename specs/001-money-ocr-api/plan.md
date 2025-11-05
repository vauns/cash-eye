# Implementation Plan: 金额识别OCR服务

**Branch**: `001-money-ocr-api` | **Date**: 2025-11-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-money-ocr-api/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

构建一个基于PP-OCRv5的金额识别HTTP API服务,提供单张和批量图片识别能力,返回纯数字格式的金额。服务采用Python开发,CPU运行,通过Docker容器化部署,支持JPEG/PNG/BMP/TIFF格式图片(最大10MB),提供健康检查接口。核心需求:识别准确率>95%,响应时间<3秒,支持10个并发请求。

**关键澄清** (2025-11-05会话):
- OCR引擎: 使用PaddleOCR v3.3.1 (2025-10-29发布,基于PP-OCRv5模型)
- 安全策略: 无需API认证(内网部署,网络层隔离)
- 扩展策略: 单实例部署,不考虑水平扩展
- 数据处理: 仅内存处理,图片不落盘
- 质量控制: 置信度<0.8时返回警告但继续返回结果

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**:
- FastAPI (Web框架)
- PaddleOCR v3.3.1 (PP-OCRv5引擎,2025-10-29发布)
- Pillow (图片处理)
- Uvicorn (ASGI服务器)
- structlog (结构化日志)
**Storage**: N/A (无状态服务,图片仅内存处理不落盘)
**Testing**: pytest, pytest-asyncio, httpx (API测试客户端)
**Target Platform**: Linux容器环境 (Docker)
**Project Type**: single (单体API服务)
**Performance Goals**:
- 单张图片识别响应时间 <3秒
- 支持至少10个并发请求(单实例)
- 识别准确率 >95%
**Constraints**:
- CPU运行(不使用GPU)
- 内存: 7天运行后不超过启动时150%
- 图片大小: 最大10MB
- 启动时间: <30秒
- 数据隐私: 图片仅内存处理,不落盘
**Scale/Scope**:
- 小规模微服务
- 单一职责(金额识别)
- 单实例部署,无水平扩展需求
- ~500-1000行代码(预估)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**状态**: ✅ PASS (无项目宪法文件,跳过检查)

**说明**: 项目根目录的`.specify/memory/constitution.md`为模板文件,尚未定义具体的项目原则和约束。本次规划基于行业最佳实践进行:
- 简单优先: 单体服务,无不必要的抽象层
- 测试驱动: 覆盖核心识别逻辑和API端点
- 可观测性: 结构化日志,健康检查端点
- 数据隐私: 图片仅内存处理,不落盘保证隐私

## Project Structure

### Documentation (this feature)

```text
specs/001-money-ocr-api/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── openapi.yaml     # OpenAPI 3.0规范
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
money-ocr-api/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API路由定义
│   │   └── schemas.py          # 请求/响应数据模型(Pydantic)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理(环境变量)
│   │   └── logging.py          # 日志配置(structlog)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py      # OCR识别核心服务
│   │   └── image_processor.py  # 图片预处理
│   └── utils/
│       ├── __init__.py
│       └── validators.py       # 输入验证
├── tests/
│   ├── unit/
│   │   ├── test_ocr_service.py
│   │   └── test_image_processor.py
│   ├── integration/
│   │   └── test_api_endpoints.py
│   └── fixtures/
│       └── sample_images/      # 测试图片样本
├── Dockerfile
├── docker-compose.yml           # 本地开发环境
├── requirements.txt
├── requirements-dev.txt         # 开发依赖
├── main.py                      # 应用入口
└── README.md
```

**Structure Decision**: 采用单体项目结构(Option 1)。理由:
1. **简单性**: 服务职责单一(金额识别),无需微服务拆分
2. **快速部署**: 单个Docker镜像包含所有依赖
3. **易维护**: 代码量小(<1000行),单一代码库便于管理
4. **符合约束**: 无状态服务,单实例部署,不需要复杂架构

## Complexity Tracking

N/A - 无宪法违规,无需复杂性辩护。

---

## Phase 0: Research (已完成)

✅ **状态**: 完成

**输出**: [research.md](./research.md)

**关键决策**:
1. Web框架: FastAPI (异步、性能优势、自动文档)
2. OCR引擎: PaddleOCR v3.3.1 (PP-OCRv5模型,2025-10-29发布)
3. 图片处理: Pillow (轻量、支持所需格式)
4. 金额提取: 正则表达式+规则引擎
5. 日志: structlog结构化日志
6. 部署: Docker多阶段构建
7. 安全: 无API认证,依赖网络层隔离
8. 数据处理: 仅内存处理,图片不落盘

---

## Phase 1: Design & Contracts (已完成)

✅ **状态**: 完成

**输出**:
- [data-model.md](./data-model.md) - API数据模型和内部实体定义
- [contracts/openapi.yaml](./contracts/openapi.yaml) - OpenAPI 3.0规范
- [quickstart.md](./quickstart.md) - 快速开始指南
- CLAUDE.md - 代理上下文文件(已更新)

**数据模型**:
- RecognitionRequest: 单张识别请求
- BatchRecognitionRequest: 批量识别请求
- RecognitionResponse: 识别响应(含置信度、处理时间、warnings)
- ErrorResponse: 统一错误格式(7种错误码)
- HealthCheckResponse: 健康检查响应

**API端点**:
1. `POST /api/v1/recognize` - 单张图片识别
2. `POST /api/v1/recognize/batch` - 批量图片识别
3. `GET /api/v1/health` - 健康检查

**关键设计决策**:
- 置信度<0.8时添加警告但仍返回结果(FR-015)
- 图片仅内存处理不落盘(FR-014)
- 无API认证机制(AS-004)
- 单实例部署无扩展考虑(AS-005)

---

## Constitution Check (Phase 1后重新评估)

✅ **状态**: PASS

**评估结果**:
- ✅ **简单性**: 单体架构,无不必要抽象,代码结构清晰
- ✅ **可测试性**: 设计支持单元测试(services)和集成测试(API)
- ✅ **可观测性**: 结构化日志、健康检查端点、响应时间指标
- ✅ **API优先**: OpenAPI规范完整,支持自动文档生成
- ✅ **错误处理**: 统一错误响应格式,明确错误码体系
- ✅ **数据隐私**: 图片仅内存处理,不落盘,符合隐私保护要求

**无额外复杂性引入**,所有设计决策符合行业最佳实践和澄清结果。

---

## 下一步: Phase 2 (任务生成)

Phase 2由`/speckit.tasks`命令执行,将基于本计划生成:
- `tasks.md`: 具体实施任务清单(依赖排序)

**当前规划状态**: 已完成Phase 0和Phase 1,准备进入任务生成阶段。
