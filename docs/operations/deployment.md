# 部署说明

## 目的

本文档定义 `youtube-parser` 的部署形态、运行约束和发布后验证要求。

## 当前推荐部署形态

当前推荐采用：

- `youtube-parser` 作为独立能力服务部署
- 通过内网地址被 `linker-content` 调用
- 不直接作为公网主入口

## 部署原则

- 对外只暴露统一 parser API
- 服务应支持独立升级和独立回滚
- 部署方式不应改变契约路径
- 发布后必须验证 `health / capabilities / parse`

## 当前发布方式

当前仓库已有：

- Dockerfile
- `compose.yaml`
- `deploy/compose.prod.yaml`
- 构建、导出和发布脚本

后续在 Python 迁移完成后，需要同步把镜像和启动命令切换到 Python 运行时。

## 发布后最小验证

至少验证：

- `GET /api/v1/health`
- `GET /api/v1/capabilities`
- 一条真实或 fixture 级的 `POST /api/v1/parse`

## 回滚原则

- 优先通过旧镜像 tag 回滚
- 回滚后仍需重新验证三类基础接口

## 何时更新本文档

当以下内容变化时必须更新：

- 部署拓扑变化
- 镜像构建方式变化
- 环境变量变化
- 发布验证流程变化
