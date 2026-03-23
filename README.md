# youtube-parser

`youtube-parser` 是 `linker-platform` 中的 YouTube 能力服务仓库。

当前状态：

- 仓库目录已经规范到 `parsers/youtube-parser`
- 当前代码主体仍然是一个 Next.js 原型项目
- 目前还没有完全对齐 `linker-content` 的统一 parser 契约
- 下一阶段需要把它逐步收敛成真正的 YouTube 解析服务

## 当前目标

这一版先完成两件事：

1. 把项目收敛成正式 Git 仓库
2. 补齐基础工程文件，方便后续继续演进为能力服务

## 推荐目录

```text
youtube-parser/
├── app/
├── components/
├── docs/
├── deploy/
├── scripts/
├── public/
├── static/
├── .env.example
├── .gitignore
├── Dockerfile
├── compose.yaml
└── README.md
```

## 本地开发

```bash
npm install
npm run dev
```

默认端口：`3000`

## 容器启动

```bash
docker compose up -d
```

## 当前注意事项

- 当前项目名已经统一为 `youtube-parser`
- 当前仓库名和目录名使用 `kebab-case`
- Python 模块名或语言内部命名如果后续出现，可以再按语言习惯处理
- 当前仓库还不应直接视为正式生产 parser，后续仍需要补统一接口、健康检查和解析 API
```
