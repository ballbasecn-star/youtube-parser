# youtube-parser 功能与技术架构重设计草案

## 目的

本文档用于重新定义 `youtube-parser` 的能力范围、产品边界和技术架构，作为后续重构和迭代的统一依据。

当前目标不是把 `youtube-parser` 做成 YouTube 全功能抓取平台，而是把它收敛成一个：

- 对 `linker-content` 友好
- 对 YouTube 平台差异有明确封装
- 对失败和限流有清晰降级
- 能稳定产出统一 parser 契约的能力服务

本次重设计所依赖的契约约束，已经同步落在：

- `docs/parser-contract.md`

## 当前现状判断

当前仓库已经具备统一 parser 契约的最小 API 壳：

- `GET /api/v1/health`
- `GET /api/v1/capabilities`
- `POST /api/v1/parse`

但当前核心问题也很明确：

- 实际只完成了 YouTube URL 识别与 `canonicalUrl` 规范化
- `title / author / transcript / metrics` 仍是占位或空值
- `rawPayload` 仍不足以支撑后续问题排查和映射演进
- 当前服务以 Next.js App Router 搭建，技术形态偏“页面应用”，不够贴合 parser 的服务定位

因此，这次重设计的核心不是“再补几个字段”，而是把它从“最小 demo”收敛成“稳定能力服务”。

## 在系统中的职责边界

`youtube-parser` 的职责：

- 识别和解析 YouTube 来源内容
- 将 YouTube 平台差异封装在本服务内部
- 对外返回统一 `ParsedContentPayload`
- 提供健康检查、能力声明和明确错误码
- 在必要时保留调试和排障需要的原始平台数据

`youtube-parser` 不负责：

- 主系统内容状态流转
- 主数据库写入
- 创作项目管理
- 笔记、资产和发布记录管理
- 直接调用 `linker-script`
- 页面级阅读排版或站内 UI 渲染

## 功能设计

### 核心目标

`youtube-parser` 第一优先级是稳定支持 `linker-content` 导入 YouTube 视频，而不是追求平台数据全覆盖。

### 第一阶段必须稳定支持的能力

1. 输入识别与 URL 规范化

- 支持 `watch`
- 支持 `youtu.be`
- 支持 `shorts`
- 支持 `live`
- 支持分享文本中提取 URL
- 统一输出稳定 `externalId`
- 统一输出稳定 `canonicalUrl`

2. 视频基础元数据解析

- 真实标题
- 真实作者名称
- 频道 ID
- 频道主页 URL
- 发布时间
- 缩略图
- 基础简介文本
- 标签或关键词

3. 视频文本内容解析

- 视频简介中的主要文本
- 字幕文本
- 字幕分段 `segments`
- 当字幕缺失时，明确给出 warning，而不是伪成功

4. 基础指标解析

- 播放量
- 点赞数
- 评论数

5. 统一错误与降级

- 不支持的链接明确返回 `UNSUPPORTED_URL`
- 目标内容不可见明确返回 `AUTH_REQUIRED` 或 `UPSTREAM_CHANGED`
- 字幕缺失不应让整次解析失败，但必须返回 warning
- 元数据完全不可获取时才返回失败

### 第二阶段可增强的能力

- 多语言字幕优选与回退
- 频道级更多作者信息
- Shorts / Live 的细分内容类型增强
- 章节信息解析
- 置顶评论或高价值评论摘要
- 缩略图和字幕缓存

### 当前明确不纳入范围

- 批量抓取整个频道
- 独立的搜索能力
- 下载视频文件
- 下载音频文件
- 对字幕做 AI 分析或摘要
- 独立前端后台

## 推荐的解析策略

YouTube 解析建议采用“多层降级策略”，而不是单一来源强依赖。

### L1：URL 规范化层

负责：

- 识别是否为支持的 YouTube 视频链接
- 解析 `videoId`
- 输出 `canonicalUrl`

### L2：基础元数据层

负责：

- 获取标题、作者、发布时间、缩略图、简介、基础指标

建议来源优先级：

1. 官方可稳定访问的 oEmbed / 页面元数据
2. 页面内嵌 JSON
3. 其他兜底解析方式

要求：

- 至少有一条主链路和一条兜底链路
- 不能把单一 HTML 选择器作为唯一依赖

### L3：字幕层

负责：

- 获取 transcript
- 标准化 `segments`
- 输出语言信息和字幕来源

要求：

- 字幕失败应独立处理，不拖垮基础元数据解析
- 字幕为空时要明确标记 warning
- 字幕成功与否要能在 `capabilities` 和日志里区分

### L4：标准化映射层

负责：

- 将多来源结果装配为统一 `ParsedContentPayload`
- 统一错误码
- 统一 warning
- 保留必要的 `rawPayload`

## 技术架构设计

## 技术选型建议

当前建议从 **Next.js API 项目** 收敛为 **Python 能力服务**。

推荐形态：

- 语言：Python 3.12+
- Web 框架：FastAPI
- 模型校验：Pydantic v2
- HTTP 客户端：httpx
- 运行：uvicorn
- 日志：structlog 或标准 logging + JSON formatter
- 测试：pytest

### 为什么建议改为 Python

- parser 本质上是采集和解析服务，Python 在抓取、HTML 解析、字幕处理和测试样本组织上更自然
- 后续如果要接入 `yt-dlp`、页面解析、字幕提取或更多兜底链路，Python 生态更成熟
- parser 没有真实前端页面需求，继续保留 Next.js 会让技术形态失焦
- 用 Python 可以把服务边界收敛得更纯粹：API、provider、解析和映射

### 为什么不建议继续把 Next.js 作为长期形态

- parser 不是面向用户的 Web 产品
- 当前没有持续存在的页面需求，`app/page.tsx` 等 UI 壳是额外负担
- App Router 适合页面和 API 混合应用，但不适合长期承载纯解析服务
- 后续要做 provider 分层、契约测试、抓取兜底和样本回归时，纯 Python 服务更清晰

## 推荐目录结构

```text
youtube-parser/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── health.py
│   │       ├── capabilities.py
│   │       └── parse.py
│   ├── contract/
│   │   ├── envelope.py
│   │   ├── schemas.py
│   │   └── error_codes.py
│   ├── youtube/
│   │   ├── application/
│   │   │   └── parse_youtube_service.py
│   │   ├── domain/
│   │   │   ├── models.py
│   │   │   └── value_objects.py
│   │   ├── providers/
│   │   │   ├── oembed_provider.py
│   │   │   ├── watch_page_provider.py
│   │   │   ├── transcript_provider.py
│   │   │   └── yt_dlp_provider.py
│   │   ├── normalization/
│   │   │   ├── url_normalizer.py
│   │   │   ├── metadata_normalizer.py
│   │   │   └── transcript_normalizer.py
│   │   └── mapper/
│   │       └── parsed_content_mapper.py
│   ├── shared/
│   │   ├── http_client.py
│   │   ├── logging.py
│   │   └── settings.py
│   └── bootstrap.py
├── tests/
│   ├── contract/
│   ├── integration/
│   └── fixtures/
├── docs/
├── scripts/
├── deploy/
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 模块职责

### api routes

只负责：

- HTTP 入参接收
- requestId 透传
- 响应状态码
- envelope 输出

不负责：

- YouTube 解析逻辑
- 平台映射逻辑

### application

负责：

- 编排整个解析流程
- 调用 provider
- 做多层降级与错误聚合

### providers

负责：

- 访问具体上游数据源
- 封装外部响应差异

不负责：

- 直接拼 `ParsedContentPayload`

### normalization

负责：

- 清洗元数据
- 统一文本与时间格式
- 统一 transcript segment 结构

### mapper

负责：

- 将 YouTube 内部模型映射到统一 parser 契约

## 关键数据流

```text
POST /api/v1/parse
  -> parse route
  -> ParseYoutubeService
  -> URL Normalizer
  -> Metadata Providers (主链路 + 兜底链路)
  -> Transcript Provider
  -> Normalizers
  -> ParsedContentMapper
  -> ApiEnvelope<ParsedContentPayload>
```

## 错误处理策略

建议把错误分成四类：

1. 输入错误

- `INVALID_INPUT`
- `UNSUPPORTED_URL`

2. 上游访问错误

- `AUTH_REQUIRED`
- `RATE_LIMITED`
- `PARSER_TIMEOUT`

3. 上游结构变化错误

- `UPSTREAM_CHANGED`

4. 服务内部错误

- `INTERNAL_ERROR`

同时建议保留 warning，不把所有不完整结果都升级成失败：

- `TRANSCRIPT_UNAVAILABLE`
- `METRICS_UNAVAILABLE`
- `DESCRIPTION_PARTIAL`

## 能力声明建议

当前重设计后，`GET /api/v1/capabilities` 建议逐步对齐为：

```json
{
  "platform": "youtube",
  "supportedSourceTypes": ["video", "share_text"],
  "features": {
    "transcript": true,
    "images": true,
    "metrics": true,
    "authorProfile": true,
    "deepAnalysis": false,
    "batchParse": false,
    "asyncParse": false
  }
}
```

说明：

- 如果某个能力依赖外部条件，应在运行时返回真实可用状态
- 不要长期把已实现能力继续标记为 `false`

## 缓存与限流建议

第一版可以允许轻量缓存，但不应把缓存做成主流程前提。

建议：

- 对 `videoId` 维度的元数据做短 TTL 内存缓存
- 对字幕做独立缓存
- 对失败结果做短 TTL 失败缓存，避免短时间重复打爆上游

不建议第一版就做：

- 重型数据库缓存
- 分布式队列
- 复杂任务编排

## 可观测性要求

至少补齐：

- `requestId`
- `videoId`
- provider 命中链路
- 上游耗时
- transcript 是否可用
- warning 列表
- 错误码

日志要求：

- 不记录完整敏感 cookie
- 避免把超大原始页面内容直接打进日志
- 原始平台数据如需保留，应进入 `rawPayload` 或调试快照，而不是日志洪泛

## 测试策略

至少覆盖：

1. URL 规范化单测

- `watch`
- `youtu.be`
- `shorts`
- `live`
- 分享文本提取

2. 契约测试

- health
- capabilities
- parse success
- parse invalid input
- parse unsupported url

3. 集成测试

- provider 正常返回
- provider 超时
- transcript 缺失
- 页面结构变化时返回明确错误

4. 固定样本回归测试

- 至少准备几条真实视频 fixture
- 覆盖普通视频、shorts、字幕缺失、简介较长等情况

## 迁移策略建议

建议采用“小步迁移”，不要一次性大改。

### M1

- 保留现有统一契约接口定义
- 在 Python 侧先重建 `health / capabilities / parse` 最小服务壳
- 补 URL 规范化与契约测试

### M2

- 接入真实元数据 provider
- 把当前最小 demo 的逻辑迁移到 `application / providers / mapper`

### M3

- 接入 transcript provider
- 补 warning、错误码和 fixtures 回归测试

### M4

- 下线 Next.js 页面壳
- 完成 Docker、compose、发布脚本与 Python 服务对齐

说明：

- 如果团队当前更重视快速收敛，可以直接新建 Python 服务并并行替换
- 如果团队更重视平滑切换，也可以先保留仓库名不变，只把内部实现迁移为 Python

## 当前建议结论

我建议把 `youtube-parser` 的重设计定为：

1. 功能上，从“URL 规范化 demo”升级为“稳定导入型 YouTube 解析服务”
2. 架构上，采用“API route -> service -> providers -> normalization -> mapper”的清晰分层
3. 技术上，收敛为 Python + FastAPI 的纯能力服务
4. 节奏上，先保证真实标题、作者、简介、字幕、指标和错误码，再考虑高级能力

这条路线能保证：

- 不和 `linker-content` 的主系统职责重叠
- 不把 parser 做成过重的平台工具
- 又足够支撑 `linker-content` 的统一阅读和后续创作链路
