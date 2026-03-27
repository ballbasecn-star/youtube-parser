# 架构总览

## 系统目标

`youtube-parser` 围绕“稳定输出统一 YouTube 解析结果”组织。

后续新增能力应优先复用统一 parser 契约和内部 provider 分层，而不是继续把平台特例直接堆在 API 路由里。

## 当前阶段说明

当前仓库已经有最小 API 壳，但仍处在从 demo 向正式能力服务收敛的阶段。

当前已经具备：

- `health / capabilities / parse` 三个基础接口
- YouTube 常见链接识别
- `videoId` 提取
- `canonicalUrl` 规范化
- 统一 envelope 输出

当前正在推进的主线是：

- 从 Next.js 最小 demo 收敛为 Python + FastAPI 的能力服务
- 建立 `route -> service -> providers -> normalization -> mapper` 的清晰分层
- 补齐真实元数据、字幕和基础指标解析
- 让 `youtube-parser` 对 `linker-content` 的契约输出可长期稳定维护

## 服务边界

`youtube-parser` 负责：

- 识别和解析 YouTube 视频来源
- 封装 YouTube 平台差异
- 输出统一 `ParsedContentPayload`
- 提供 `health / capabilities / parse`
- 通过 warning 和错误码表达不完整与失败场景

`youtube-parser` 不负责：

- 主系统状态流转
- 主库写入
- 创作项目管理
- 笔记和资产管理
- 直接调用 `linker-script`
- 页面级阅读展示

## 核心数据流

1. `linker-content` 调用 `POST /api/v1/parse`
2. 路由层接收 `ParserParseRequest`
3. URL 规范化层解析 `videoId` 与 `canonicalUrl`
4. 元数据 provider 拉取标题、作者、发布时间、缩略图、简介
5. transcript provider 拉取字幕与分段
6. metrics provider 拉取播放、点赞、评论等基础指标
7. normalization 层清洗和统一各 provider 返回
8. mapper 层映射为统一 `ParsedContentPayload`
9. API 层返回 `ApiEnvelope`

## 推荐技术形态

- 语言：Python 3.12+
- Web 框架：FastAPI
- 数据校验：Pydantic v2
- HTTP 客户端：httpx
- 测试：pytest
- 运行：uvicorn

## 设计规则

- 对外只暴露统一 parser 契约
- 不把 provider 的私有响应直接透传给调用方
- transcript 缺失优先返回 warning，不伪失败
- 只有在最小结构无法成立时才返回失败
- `rawPayload` 只保留必要排障信息
- 解析链路应支持多 provider 降级
- API 路由不承载解析主逻辑

## 关联文档

- `docs/parser-contract.md`
- `docs/redesign.md`
- `docs/architecture/provider-strategy.md`
- `docs/modules/parsing-pipeline.md`
