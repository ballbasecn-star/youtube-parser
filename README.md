# youtube-parser

`youtube-parser` 是 `linker-platform` 中的 YouTube 能力服务仓库。

当前仓库已经清理掉与 parser 项目无关的个人网站内容、展示素材和无关文档，收敛为一个面向后续统一 parser 契约的最小服务骨架。

## 当前保留内容

- Next.js 运行骨架
- 首页占位说明页
- `GET /api/v1/health`
- `GET /api/v1/capabilities`
- Docker / compose / scripts 基础文件

## 当前目录

```text
youtube-parser/
├── app/
│   ├── api/v1/health/
│   ├── api/v1/capabilities/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── deploy/
├── docs/
├── scripts/
├── .env.example
├── .gitignore
├── Dockerfile
├── compose.yaml
├── package.json
└── README.md
```

## 本地开发

```bash
npm install
npm run dev
```

默认端口：`3000`

## 下一步建议

1. 补齐统一 parser 契约对应的 `POST /api/v1/parse`
2. 明确 YouTube 解析输入模型与输出 DTO
3. 接入真实解析链路，而不是只保留占位接口
4. 再把它接回 `linker-content` 的统一 parser 调度流程
