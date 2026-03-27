# Provider 策略

## 目的

本文档定义 `youtube-parser` 内部各类 provider 的职责、优先级和降级策略，避免把上游平台耦合直接写进主流程。

## provider 分层原则

- 每类 provider 只负责一种上游数据来源
- provider 只负责获取和初步封装数据，不直接拼最终 `ParsedContentPayload`
- provider 之间允许降级，但降级顺序必须清晰
- 上游变化优先在 provider 层隔离，不把细节泄漏到 route

## 当前建议的 provider 类型

### 1. URL Normalizer

负责：

- 判断是否为支持的 YouTube 视频链接
- 提取 `videoId`
- 统一生成 `canonicalUrl`

### 2. Metadata Provider

负责：

- 标题
- 频道信息
- 发布时间
- 缩略图
- 简介
- 标签
- 基础指标

当前建议优先级：

1. 官方或稳定的结构化元数据来源
2. 页面内嵌 JSON
3. 兜底 provider

### 3. Transcript Provider

负责：

- transcript 文本
- transcript segments
- 语言识别或字幕来源说明

### 4. Metrics Provider

负责：

- `views`
- `likes`
- `comments`

说明：

- 第一版可以与 Metadata Provider 合并
- 只有在实现复杂度明显上升后，再拆成独立 provider

## provider 降级规则

### 元数据

- 主 provider 成功：直接进入 normalization
- 主 provider 失败但可重试：记录 warning，并尝试兜底 provider
- 主 provider 和兜底 provider 都失败：若连标题都无法获得，则返回 `UPSTREAM_CHANGED` 或 `INTERNAL_ERROR`

### transcript

- transcript 成功：填充 `transcript` 和 `segments`
- transcript 缺失：返回 warning `TRANSCRIPT_UNAVAILABLE`
- 不因 transcript 缺失直接让整次解析失败

### metrics

- metrics 成功：填充结构化字段
- metrics 缺失：字段允许为 `null`，并返回 warning

## provider 选择原则

- 优先稳定性，再考虑字段覆盖率
- 优先结构化数据源，再考虑 HTML 字符串解析
- 优先显式错误，再避免伪成功
- provider 的异常要映射成统一内部错误语义

## 何时更新本文档

当以下内容变化时必须更新：

- provider 类型变化
- 主链路和兜底链路变化
- transcript 或 metrics 的处理策略变化
- 默认 warning 策略变化
