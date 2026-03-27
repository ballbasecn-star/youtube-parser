# 产品需求总览

## 产品摘要

`youtube-parser` 是 `linker-platform` 中面向 YouTube 来源的能力服务。

它的核心目标不是做成面向人的 YouTube 工具站，也不是做频道抓取平台，而是为 `linker-content` 提供稳定、统一、可追溯的 YouTube 内容解析能力。

在整体系统中：

- `linker-content` 是唯一主系统
- `youtube-parser` 是 YouTube 采集适配器
- `linker-script` 是分析与生成引擎

当前技术方向收敛为：

- Python
- FastAPI
- Pydantic
- httpx
- pytest

## 目标用户

- `linker-content` 后端的 `ParserPort`
- 维护 `youtube-parser` 的工程协作者
- 需要排查 YouTube 导入稳定性的开发与运维人员

## 核心任务

1. 识别并规范化 YouTube 视频链接
2. 获取稳定的 `videoId` 与 `canonicalUrl`
3. 解析视频基础元数据
4. 尽量解析 transcript 与基础指标
5. 输出统一 `ParsedContentPayload`
6. 在不完整场景下给出明确 warning 或错误码

## 当前范围

### 当前已在范围内

- `GET /api/v1/health`
- `GET /api/v1/capabilities`
- `POST /api/v1/parse`
- `watch / youtu.be / shorts / live` 链接识别
- 分享文本中的 URL 提取
- `externalId` 和 `canonicalUrl` 规范化
- 统一 envelope 返回
- 统一错误码

### 当前第一阶段目标范围

- 真实标题解析
- 真实作者与频道信息解析
- 真实发布时间解析
- 缩略图解析
- 基础简介和 `rawText` 解析
- transcript 解析与 `segments` 标准化
- 播放量、点赞数、评论数等基础指标解析

## 第一版非目标

当前阶段明确不做：

- 批量抓取整个频道
- 独立搜索能力
- 视频下载
- 音频下载
- 复杂账号体系
- 面向用户的前端后台
- AI 摘要、改写或分析

## 成功标准

如果第一版满足以下条件，就算成功：

1. `linker-content` 可通过统一契约稳定调用 `youtube-parser`
2. 对常见 YouTube 视频链接能稳定返回 `videoId` 和 `canonicalUrl`
3. 对大多数公开视频能稳定返回真实标题和作者信息
4. transcript 缺失时不会伪装成完整成功，也不会把整个解析链路拖垮
5. 出错时能返回明确错误码，便于主系统映射和排障
6. 服务可在本地和生产环境以一致方式部署和验证

## 产品原则

- 优先保证稳定导入，而不是深度抓取
- 优先保证统一契约，而不是平台私有字段堆积
- 优先保证明确错误和 warning，而不是模糊成功
- 优先做可维护的 provider 分层，而不是把解析逻辑塞进路由
- parser 只负责采集适配，不接管主业务状态
