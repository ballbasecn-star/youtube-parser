# 项目结构与分层规范

## 目的

本文档定义 `youtube-parser` 在 Python 重构方向下推荐采用的目录结构和代码分层。

## 总体原则

- API 层只负责协议适配
- 服务层负责解析流程编排
- provider 层负责上游访问
- normalization 层负责清洗和标准化
- mapper 层负责输出统一 parser 契约
- 测试和 fixtures 必须作为一等目录存在

## 推荐目录结构

```text
youtube-parser/
├── app/
│   ├── main.py
│   ├── bootstrap.py
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
│   │   ├── domain/
│   │   ├── providers/
│   │   ├── normalization/
│   │   └── mapper/
│   └── shared/
├── tests/
│   ├── contract/
│   ├── integration/
│   └── fixtures/
├── docs/
├── deploy/
├── scripts/
├── pyproject.toml
└── README.md
```

## 分层职责

### `app/api/v1`

负责：

- HTTP 路由
- 请求校验入口
- 响应状态码
- envelope 输出

不负责：

- 具体解析逻辑
- 平台字段清洗

### `app/contract`

负责：

- `ApiEnvelope`
- 请求与响应 schema
- 统一错误码

### `app/youtube/application`

负责：

- 解析链路编排
- provider 调用顺序
- 降级与失败聚合

### `app/youtube/providers`

负责：

- 访问上游
- 封装上游返回差异

### `app/youtube/normalization`

负责：

- 标准化文本、时间、字幕段和指标字段

### `app/youtube/mapper`

负责：

- 映射为统一 `ParsedContentPayload`

### `tests`

负责：

- 契约测试
- provider 集成测试
- 固定样本回归测试

## 当前迁移约束

- 当前仓库仍存在 Next.js 文件，重构期间允许并存
- 新增实现默认向 Python 目录结构收敛
- 不建议继续向 `app/api` 的旧 Next.js 路由里堆新逻辑

## 何时更新本文档

当以下内容变化时必须更新：

- Python 项目目录结构变化
- 分层职责变化
- 测试目录规划变化
