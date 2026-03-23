# youtube-parser

`youtube-parser` 是 `linker-platform` 中的 YouTube 能力服务仓库。

当前仓库已经收敛为一个符合统一 parser 契约第一版的最小服务：

- `GET /api/v1/health`
- `GET /api/v1/capabilities`
- `POST /api/v1/parse`

## 当前能力范围

当前版本先保证“稳定导入”而不是“深度抓取”：

- 支持从 `sourceUrl` 或 `sourceText` 中提取 YouTube URL
- 支持 `watch`、`youtu.be`、`shorts`、`live` 等常见 YouTube 视频链接
- 返回稳定的 `canonicalUrl`
- 返回 `externalId`
- 返回最小可导入的标准 `ParsedContentPayload`

当前还没有接入：

- 真实标题抓取
- 真实作者信息抓取
- 转录抓取
- 指标抓取
- 深度分析

## 当前目录

```text
youtube-parser/
├── app/
│   ├── api/v1/health/
│   ├── api/v1/capabilities/
│   ├── api/v1/parse/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── lib/
│   ├── parser-contract.ts
│   └── youtube-parse.ts
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

## 契约说明

统一契约来源：

- `linker-content/docs/architecture/parser-contract.md`
- `linker-content/docs/architecture/parser-openapi.md`

## 下一步建议

1. 补真实 YouTube 页面或 API 解析链路
2. 把当前占位 `title/summary` 替换成真实内容
3. 补作者、媒体、字幕和指标抓取
4. 与 `linker-content` 的 `ParserPort` 做真实联调
