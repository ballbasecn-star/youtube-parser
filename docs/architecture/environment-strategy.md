# 环境与配置策略

## 目的

本文档定义 `youtube-parser` 在本地、测试和生产环境下的配置隔离与运行原则。

## 环境划分

当前建议至少区分：

- `local`
- `test`
- `prod`

## 配置原则

- 通过环境变量管理配置
- 不把敏感配置写死在代码中
- 不同环境允许使用不同 provider 开关和超时设置
- 统一契约接口路径在所有环境中保持一致

## 当前关键配置项建议

- `YOUTUBE_PARSER_HOST`
- `YOUTUBE_PARSER_PORT`
- `YOUTUBE_PARSER_LOG_LEVEL`
- `YOUTUBE_PARSER_REQUEST_TIMEOUT_MS`
- `YOUTUBE_PARSER_TRANSCRIPT_TIMEOUT_MS`
- `YOUTUBE_PARSER_ENABLE_TRANSCRIPT`
- `YOUTUBE_PARSER_ENABLE_METRICS`
- `YOUTUBE_PARSER_ENABLE_FALLBACK_PROVIDER`

## 各环境目标

### local

- 方便单机开发与手动调试
- 可启用更详细日志
- 可使用本地 fixtures 做回归验证

### test

- 用于契约测试和集成测试
- 配置应尽量可复现
- 不依赖生产密钥

### prod

- 面向 `linker-content` 稳定提供 API
- 关闭不必要调试输出
- 保证超时、重试和失败缓存策略明确

## 何时更新本文档

当以下内容变化时必须更新：

- 环境划分变化
- 核心环境变量变化
- provider 开关策略变化
- 部署方式变化
