# ADR 0001：使用 Python + FastAPI 作为 youtube-parser 长期技术形态

## 状态

已采纳

## 背景

当前 `youtube-parser` 以 Next.js 最小 API 项目存在，已经可以承载统一契约的 demo，但长期存在以下问题：

- 页面壳与 parser 服务定位不匹配
- 解析链路、provider 和契约测试不易清晰分层
- 后续字幕、页面解析和兜底 provider 的扩展更适合 Python 生态

## 决策

`youtube-parser` 的长期技术形态收敛为：

- Python 3.12+
- FastAPI
- Pydantic v2
- httpx
- pytest

## 理由

- 更符合采集适配器服务的能力型定位
- 更适合 HTML 解析、字幕处理和 provider 组合
- 对契约测试、fixtures 回归和错误隔离更友好
- 能降低前端框架壳带来的额外复杂度

## 影响

正面影响：

- 服务边界更清晰
- 目录结构更贴合 parser 特性
- 便于扩展 provider 和测试体系

负面影响：

- 需要从现有 Next.js 代码迁移
- 发布脚本和容器镜像需要重新对齐 Python 运行时

## 后续动作

1. 先补齐文档和契约
2. 建立 Python 最小服务壳
3. 逐步迁移解析逻辑和发布脚本
