# 文档总览

`docs/` 目录用于沉淀 `youtube-parser` 的长期事实来源、架构约束和迭代计划。

目标不是把 parser 写成一堆零散脚本，而是把它维护成一个对 `linker-content` 稳定可用、边界清晰、可演进的能力服务。

## 推荐阅读顺序

开始工作时，优先按下面顺序读取最小文档集合：

1. `docs/roadmap/current.md`
2. `docs/product/prd.md`
3. `docs/architecture/overview.md`
4. `docs/modules/parsing-pipeline.md`
5. `docs/parser-contract.md`
6. 如涉及长期技术决策，再看 `docs/architecture/decisions/`

除非被阻塞，不要一次性加载整个 `docs/` 目录。

## 目录结构

```text
docs/
├── architecture/
│   ├── decisions/
│   ├── environment-strategy.md
│   ├── overview.md
│   ├── project-structure.md
│   └── provider-strategy.md
├── modules/
│   ├── parsing-pipeline.md
│   └── phase3-provider-implementation.md
├── operations/
│   ├── deployment.md
│   └── development-workflow.md
├── product/
│   └── prd.md
├── roadmap/
│   └── current.md
├── parser-contract.md
└── redesign.md
```

## 文档角色说明

- `product/prd.md`：定义 `youtube-parser` 的目标、范围、非目标和成功标准
- `architecture/overview.md`：定义服务边界、核心数据流和技术形态
- `architecture/provider-strategy.md`：定义元数据、字幕和兜底 provider 的职责与优先级
- `architecture/project-structure.md`：定义 Python 服务的推荐目录结构和分层边界
- `architecture/environment-strategy.md`：定义本地、测试和生产环境的配置隔离原则
- `architecture/decisions/*.md`：记录长期技术决策
- `modules/parsing-pipeline.md`：定义解析链路的输入、输出和阶段职责
- `modules/phase3-provider-implementation.md`：第三阶段真实解析链路的详细技术设计
- `roadmap/current.md`：记录当前阶段目标和下一步工作
- `operations/development-workflow.md`：定义开发、验证和提交流程
- `operations/deployment.md`：定义部署拓扑和发布约束
- `parser-contract.md`：明确对齐 `linker-content` 统一 parser 契约的本仓库实现要求
- `redesign.md`：记录当前这轮重设计的背景、目标和迁移方向

## 当前已补齐

- `parser-contract.md`
- `redesign.md`
- `product/prd.md`
- `architecture/overview.md`
- `architecture/provider-strategy.md`
- `architecture/project-structure.md`
- `architecture/environment-strategy.md`
- `architecture/decisions/0001-use-python-fastapi-for-parser-service.md`
- `modules/parsing-pipeline.md`
- `modules/phase3-provider-implementation.md`
- `roadmap/current.md`
- `operations/development-workflow.md`
- `operations/deployment.md`

## 何时更新文档

当以下内容变化时必须更新文档：

- parser 的产品范围变化
- 输入输出契约变化
- provider 策略变化
- 目录结构或技术栈变化
- 部署方式变化
- 默认降级和错误处理策略变化
