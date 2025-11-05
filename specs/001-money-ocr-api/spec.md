# Feature Specification: 金额识别OCR服务

**Feature Branch**: `001-money-ocr-api`
**Created**: 2025-11-05
**Status**: Draft
**Input**: User description: "要做一个OCR识别服务,提供API给业务使用,主要是识别图片中的金额,返回金额给业务,图片中只有金额,技术选型选择PP-OCRv5(PaddleOCR),不需要AI功能、不需要GPU加速,使用python即可,最好做成docker快速让业务接入"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - 基础金额识别 (Priority: P1)

业务系统需要识别用户上传的图片中的金额数字,例如发票、收据、转账记录截图等。业务系统通过HTTP API上传图片,获取识别出的金额结果。

**Why this priority**: 这是服务的核心功能,是最小可用产品(MVP)。没有这个功能,整个服务就无法为业务系统提供价值。

**Independent Test**: 可以通过上传一张包含金额的图片到API端点,验证是否能够返回正确的金额数值来独立测试此功能。

**Acceptance Scenarios**:

1. **Given** 业务系统有一张包含清晰金额"1234.56"的图片, **When** 通过API上传该图片, **Then** 系统返回识别结果"1234.56"
2. **Given** 业务系统有一张包含整数金额"5000"的图片, **When** 通过API上传该图片, **Then** 系统返回识别结果"5000"
3. **Given** 业务系统上传一张不包含任何文字的空白图片, **When** API处理该请求, **Then** 系统返回明确的"未识别到金额"提示
4. **Given** 业务系统上传图片请求时网络中断, **When** 请求失败, **Then** 系统返回标准的HTTP错误码和错误信息

---

### User Story 2 - 批量金额识别 (Priority: P2)

业务系统需要同时识别多张图片中的金额,例如批量处理用户提交的多张发票。业务系统通过一次API调用上传多张图片,获取每张图片对应的金额结果。

**Why this priority**: 提升业务系统处理效率,减少API调用次数。但不是初始MVP必需的功能,可以先通过多次单张识别实现相同效果。

**Independent Test**: 可以通过一次上传3张不同金额的图片,验证返回结果是否包含3个对应的金额识别结果来独立测试。

**Acceptance Scenarios**:

1. **Given** 业务系统有3张包含不同金额的图片, **When** 通过一次API调用上传这3张图片, **Then** 系统返回包含3个金额识别结果的响应,每个结果对应一张图片
2. **Given** 业务系统上传的批量图片中有1张识别失败, **When** 处理完成后, **Then** 系统返回部分成功的结果,明确标识哪些图片识别成功、哪些失败

---

### User Story 3 - 服务健康监控 (Priority: P2)

运维人员需要监控OCR服务的运行状态,了解服务是否正常运行、识别成功率、响应时间等指标,以便及时发现和处理问题。

**Why this priority**: 对于生产环境的稳定运行非常重要,但不影响核心业务功能的可用性。可以在MVP之后添加。

**Independent Test**: 可以通过访问健康检查端点,验证是否返回服务状态信息(如运行时间、版本号、服务状态)来独立测试。

**Acceptance Scenarios**:

1. **Given** OCR服务正在运行, **When** 运维人员访问健康检查端点, **Then** 系统返回服务状态为"正常"及基本信息
2. **Given** OCR服务的核心组件(如OCR引擎)异常, **When** 访问健康检查端点, **Then** 系统返回服务状态为"异常"及错误详情

---

### User Story 4 - 容器化快速部署 (Priority: P1)

业务团队需要快速在自己的环境中部署OCR服务,不需要关心复杂的依赖安装和环境配置。通过Docker镜像,业务团队可以一键启动服务。

**Why this priority**: 直接影响业务接入速度和部署成本,是用户描述中明确要求的"快速让业务接入"的关键。

**Independent Test**: 可以通过在一台只安装了Docker的干净机器上,使用docker run命令启动服务,并成功调用API识别金额来验证。

**Acceptance Scenarios**:

1. **Given** 业务团队有一台安装了Docker的服务器, **When** 执行docker run命令启动OCR服务, **Then** 服务在30秒内启动完成并可接受API请求
2. **Given** 业务团队需要自定义服务端口, **When** 通过Docker环境变量指定端口, **Then** 服务使用指定端口启动
3. **Given** 服务容器异常退出, **When** Docker重启容器, **Then** 服务能够自动恢复正常运行

---

### Edge Cases

- 图片格式不支持时(如非主流的图片格式)如何处理? → 返回错误码UNSUPPORTED_FORMAT
- 图片文件损坏或不完整时如何响应? → 返回错误码INVALID_IMAGE
- 图片中同时包含多个金额数字时,如何确定返回哪个金额? → 返回第一个识别到的金额(已明确)
- 图片中金额带有货币符号(如¥、$)或千分位分隔符(如1,234.56)时如何处理? → 自动去除符号,返回纯数字(已明确)
- 图片尺寸过大(如超过10MB)时是否需要限制? → 拒绝请求,返回错误码FILE_TOO_LARGE(已明确)
- 并发请求超过10个时服务如何保证稳定性? → 单实例部署,假设不会超过10个并发(已明确)
- 图片中金额模糊不清或部分遮挡时如何处理? → 尽力识别,如置信度<0.8则添加警告信息
- 识别结果置信度<0.8时如何处理? → 仍返回识别结果,但在响应的warnings字段中添加"置信度较低,建议人工复核"

## Requirements *(mandatory)*

### Technical Constraints

基于用户明确要求,本项目必须遵循以下技术约束:

- **TC-001**: 必须使用PaddleOCR v3.3.1 (2025-10-29发布)作为OCR识别引擎,基于PP-OCRv5模型
- **TC-002**: 必须使用Python语言开发
- **TC-003**: 不使用GPU加速,仅使用CPU运行
- **TC-004**: 必须提供Docker容器化部署方式

### Assumptions

- **AS-001**: 图片中仅包含金额数字,不包含其他复杂内容
- **AS-002**: 业务系统具备发送HTTP请求的能力
- **AS-003**: 部署环境已安装Docker运行时
- **AS-004**: 服务部署在受信任的内网环境,API无需认证机制(通过网络层隔离保证安全)
- **AS-005**: 服务采用单实例部署,并发请求量不会超过10个,无需考虑水平扩展和负载均衡

### Functional Requirements

- **FR-001**: 系统必须提供HTTP API接口接收业务系统上传的图片
- **FR-002**: 系统必须支持常见图片格式(JPEG、PNG、BMP、TIFF)
- **FR-003**: 系统必须准确识别图片中的金额数字
- **FR-004**: 系统必须返回识别出的金额数值,采用标准数字格式(支持整数和小数)
- **FR-005**: 系统必须在图片无法识别时返回明确的错误信息和原因
- **FR-006**: 系统必须记录每次识别请求的日志,包括请求时间、图片信息、识别结果
- **FR-007**: 系统必须支持同时处理多张图片的批量识别请求
- **FR-008**: 系统必须提供健康检查接口供监控使用
- **FR-009**: 系统必须提供容器化部署方式,包含所有运行依赖
- **FR-010**: 系统必须支持通过环境变量配置服务参数(如端口号、日志级别)
- **FR-011**: 系统必须限制单次上传图片的文件大小上限为10MB
- **FR-012**: 系统必须处理图片中包含货币符号和千分位分隔符的场景,识别时自动去除这些符号,只返回纯数字格式(如"1234.56")
- **FR-013**: 当图片中包含多个金额数字时,系统必须返回第一个识别到的金额
- **FR-014**: 系统必须在内存中处理图片,处理完成后立即释放,不得将图片保存到磁盘
- **FR-015**: 当OCR识别置信度低于0.8时,系统必须在响应的warnings字段中添加"置信度较低,建议人工复核"警告,但仍返回识别结果

### Key Entities

- **识别请求(Recognition Request)**: 业务系统发起的单次或批量图片识别请求,包含图片数据、请求时间、请求来源标识
- **图片(Image)**: 需要识别的图片文件,包含图片格式、大小、内容类型
- **识别结果(Recognition Result)**: OCR处理后返回的结果,包含识别出的金额、置信度、处理时间、状态(成功/失败)
- **错误信息(Error Info)**: 识别失败时的详细信息,包含错误码、错误描述、失败原因

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 单张清晰图片的金额识别准确率达到95%以上
- **SC-002**: 单张图片识别响应时间在3秒内(不含网络传输时间)
- **SC-003**: 服务能够支持至少10个并发识别请求而不出现性能下降
- **SC-004**: 业务团队能够在10分钟内完成服务的Docker部署并成功调用API
- **SC-005**: 服务在运行期间的可用性达到99.9%(排除计划维护时间)
- **SC-006**: 识别失败时,90%的情况能够返回清晰可理解的错误原因
- **SC-007**: 服务在连续运行7天后,内存占用不超过初始启动时的150%

## Clarifications

### Session 2025-11-05

- Q: OCR引擎版本应该使用PP-OCRv4 (稳定版)还是PP-OCRv5 (最新版)? → A: 使用PP-OCRv5 (如果已正式发布)
- **确认**: 使用PaddleOCR v3.3.1 (2025-10-29发布,基于PP-OCRv5模型)
- Q: API是否需要访问控制机制(如API Key、JWT令牌等)? → A: 不需要认证
- Q: 如果并发请求超过10个,服务应该如何扩展? → A: 不考虑扩展
- Q: 上传的图片处理后是否需要临时保存到磁盘? → A: 仅内存处理不落盘
- Q: 当OCR置信度低于多少时应该给出警告?识别结果是否仍返回? → A: 0.8以下警告,继续返回
