# youtube-parser 契约对齐说明

## 目的

本文档用于把 `youtube-parser` 需要遵守的统一 parser 契约明确写入本仓库，作为实现、联调和契约测试的直接依据。

本仓库的契约来源是：

- `linker-content/docs/architecture/parser-contract.md`
- `linker-content/docs/architecture/parser-openapi.md`

本文档不重新发明一套新契约，而是把通用契约收敛为 `youtube-parser` 的具体实现约束。

## 契约目标

- `youtube-parser` 对 `linker-content` 只暴露统一 parser 接口
- `youtube-parser` 内部可以自由调整 provider、抓取策略和缓存方式
- 外部调用方不需要了解 YouTube 平台私有字段才能完成最小导入
- 契约优先保证“稳定导入”和“可追溯排障”

## 固定接口

`youtube-parser` 必须提供以下接口：

- `GET /api/v1/health`
- `GET /api/v1/capabilities`
- `POST /api/v1/parse`

当前不要求提供：

- 批量解析接口
- 异步回调接口
- 独立鉴权网关接口

## 统一响应包裹

所有接口统一返回 `ApiEnvelope<T>`：

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "requestId": "req_123",
    "parserVersion": "1.0.0"
  }
}
```

失败时：

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "PARSER_TIMEOUT",
    "message": "Parser request timed out",
    "retryable": true
  },
  "meta": {
    "requestId": "req_123",
    "parserVersion": "1.0.0"
  }
}
```

### 契约约束

- `requestId` 由调用方传入时优先透传；缺失时由服务端生成
- `parserVersion` 必须对应当前服务版本
- `success=false` 时，`data` 必须为 `null`
- `success=true` 时，`error` 必须为 `null`

## `GET /api/v1/health`

### 用途

用于探活和可用性探测。

### 返回体

建议至少返回：

```json
{
  "status": "UP"
}
```

### youtube-parser 实现要求

- 只检查服务自身是否可用
- 不要求在 `health` 中探测所有上游 provider
- 如果需要表达降级，可扩展 `DEGRADED`，但不能破坏现有字段结构

## `GET /api/v1/capabilities`

### 用途

声明 `youtube-parser` 当前支持的来源类型和能力范围。

### 最小返回结构

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

### youtube-parser 实现要求

- `platform` 固定为 `youtube`
- `supportedSourceTypes` 第一版至少包含 `video` 和 `share_text`
- `features` 应返回当前真实能力，不长期保留过时占位值
- 若 transcript 或 metrics 受运行环境限制，应反映当前可用性

## `POST /api/v1/parse`

### 请求体

`youtube-parser` 必须接受统一的 `ParserParseRequest`：

```json
{
  "requestId": "req_123",
  "input": {
    "sourceText": "看看这个视频 https://youtu.be/abc123",
    "sourceUrl": "https://www.youtube.com/watch?v=abc123",
    "platformHint": "youtube"
  },
  "options": {
    "fetchTranscript": true,
    "fetchMedia": true,
    "fetchMetrics": true,
    "deepAnalysis": false,
    "languageHint": "zh-CN"
  }
}
```

### 输入规则

- `sourceText` 和 `sourceUrl` 至少提供一个
- 允许从 `sourceText` 中提取 URL
- `platformHint` 只作为提示，不作为唯一判断依据
- 若两者都为空，返回 `INVALID_INPUT`

## 统一返回体

`data` 必须映射到统一 `ParsedContentPayload`。

### youtube-parser 的最小字段要求

```json
{
  "platform": "youtube",
  "sourceType": "video",
  "externalId": "abc123",
  "canonicalUrl": "https://www.youtube.com/watch?v=abc123",
  "title": "真实视频标题",
  "summary": "视频简介摘要或核心说明",
  "author": {
    "externalAuthorId": "channel_123",
    "name": "频道名称",
    "handle": "@channel",
    "profileUrl": "https://www.youtube.com/@channel",
    "avatarUrl": "https://..."
  },
  "publishedAt": "2026-03-01T10:00:00Z",
  "language": "zh-CN",
  "content": {
    "rawText": "简介和可阅读文本",
    "transcript": "完整字幕文本",
    "segments": [
      {
        "text": "第一句字幕",
        "startMs": 0,
        "endMs": 1800,
        "speaker": null
      }
    ]
  },
  "metrics": {
    "views": 120000,
    "likes": 2300,
    "comments": 180,
    "shares": null,
    "favorites": null
  },
  "tags": ["ai", "workflow"],
  "media": {
    "covers": [],
    "images": [],
    "videos": [],
    "audios": []
  },
  "rawPayload": {},
  "warnings": []
}
```

### 字段约束

- `platform` 必须固定为 `youtube`
- `sourceType` 第一版固定为 `video`
- `externalId` 优先使用稳定的 YouTube `videoId`
- `canonicalUrl` 必须统一输出为 `https://www.youtube.com/watch?v=<videoId>`
- `title` 应为真实标题；只有在上游彻底失效时才允许失败，而不是长期占位
- `summary` 可来自简介摘要，但不能长期只回传分享文本
- `author` 应尽可能填充频道相关字段
- `content.rawText` 应优先承载简介和可阅读文本，不应仅回传 URL
- `content.transcript` 缺失时允许为 `null`
- `segments` 缺失时允许为空数组
- `rawPayload` 应保留足够排障信息，但不能替代结构化字段
- `warnings` 用于表示“可解析但不完整”的情况

## YouTube 平台特化约束

### URL 支持范围

第一版至少支持：

- `https://www.youtube.com/watch?v=...`
- `https://youtu.be/...`
- `https://www.youtube.com/shorts/...`
- `https://www.youtube.com/live/...`

不支持的链接必须明确返回 `UNSUPPORTED_URL`。

### canonicalUrl 统一规则

无论输入是 `watch / youtu.be / shorts / live`，最终统一输出：

```text
https://www.youtube.com/watch?v=<videoId>
```

### transcript 规则

- `fetchTranscript=true` 时应尽量拉取字幕
- 若字幕缺失，但元数据完整，允许成功返回并附加 warning
- 若字幕可用，应同时填充 `content.transcript` 和 `content.segments`
- 不应因为字幕缺失把整次元数据解析标记为失败

### metrics 规则

- `fetchMetrics=true` 时尽量返回 `views / likes / comments`
- 无法获取时允许为 `null`
- 指标缺失时优先通过 warning 暴露，而不是直接失败

### media 规则

- `covers` 至少应包含可用缩略图
- `images` 第一版允许为空
- `videos / audios` 第一版不要求返回下载地址

## 统一错误码

`youtube-parser` 至少需要对齐以下错误码：

- `UNSUPPORTED_URL`
- `INVALID_INPUT`
- `AUTH_REQUIRED`
- `RATE_LIMITED`
- `UPSTREAM_CHANGED`
- `PARSER_TIMEOUT`
- `INTERNAL_ERROR`

### 建议映射

- 输入缺失或 JSON 非法：`INVALID_INPUT`
- 不是 YouTube 视频链接：`UNSUPPORTED_URL`
- 视频受限、需要登录或地区限制：`AUTH_REQUIRED`
- 上游限流：`RATE_LIMITED`
- 页面结构变化、关键字段完全取不到：`UPSTREAM_CHANGED`
- 上游超时：`PARSER_TIMEOUT`
- 未预期异常：`INTERNAL_ERROR`

## warning 建议

`youtube-parser` 建议补充以下 warning 语义：

- `TRANSCRIPT_UNAVAILABLE`
- `METRICS_UNAVAILABLE`
- `DESCRIPTION_PARTIAL`
- `AUTHOR_PARTIAL`

warning 不应替代错误码；它只用于表示“成功但不完整”。

## 原始数据保留规则

`rawPayload` 建议保留：

- `matchedSourceUrl`
- `resolvedVideoId`
- `metadataProvider`
- `transcriptProvider`
- provider 原始关键字段快照

`rawPayload` 不建议保留：

- 过大的整页 HTML 全量文本
- 敏感 cookie
- 与主系统无关的调试垃圾数据

## 状态码建议

- `200`：解析成功
- `400`：输入错误或不支持的 URL
- `401`：需要登录或受权限限制
- `429`：被上游限流
- `500`：内部错误或无法归类的上游问题

说明：

- 如果要更精细区分 `UPSTREAM_CHANGED`，仍可先返回 `500`
- 关键是 envelope 中的 `error.code` 要稳定

## 契约测试建议

本仓库后续至少应覆盖：

1. `GET /api/v1/health`
2. `GET /api/v1/capabilities`
3. `POST /api/v1/parse` 成功解析 `watch`
4. `POST /api/v1/parse` 成功解析 `youtu.be`
5. `POST /api/v1/parse` 成功解析 `shorts`
6. `POST /api/v1/parse` 成功解析分享文本
7. `POST /api/v1/parse` 返回 `INVALID_INPUT`
8. `POST /api/v1/parse` 返回 `UNSUPPORTED_URL`
9. `POST /api/v1/parse` 字幕缺失但成功返回 warning
10. `POST /api/v1/parse` 上游结构变化时返回明确错误码

## 与重设计文档的关系

如果想看 `youtube-parser` 的功能范围、技术架构和迁移路径，请同时参考：

- `docs/redesign.md`

如果想看统一契约的上游来源，请参考：

- `linker-content/docs/architecture/parser-contract.md`
- `linker-content/docs/architecture/parser-openapi.md`
