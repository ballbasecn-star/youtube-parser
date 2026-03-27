# 当前路线图

## 当前状态

当前仓库已经完成：

- 最小 API 壳初始化
- 统一 parser 契约 envelope 接入
- `health / capabilities / parse` 三个接口建立
- YouTube 常见链接识别
- `videoId` 提取与 `canonicalUrl` 规范化
- 初步文档体系建立
- **Python + FastAPI 服务骨架**
- **Pydantic v2 schema 和统一错误码**
- **契约测试覆盖**

当前仓库已从 Next.js demo 阶段迁移到 Python 能力服务骨架阶段。

## 当前优先级

当前优先级不是扩更多能力，而是先把以下内容固定下来：

1. parser 契约 ✅
2. Python 技术架构 ✅
3. provider 分层
4. 文档体系 ✅
5. 真实元数据与 transcript 主链路

## 当前工程工作

### 第一阶段：文档与契约冻结 ✅ 已完成

当前目标：

1. 建立 `docs/` 分层结构
2. 明确 `youtube-parser` 的产品边界和非目标
3. 明确统一 parser 契约在本仓库内的实现要求
4. 明确 Python 技术架构和目录结构

当前已完成：

1. 已建立 `product / architecture / modules / roadmap / operations` 基础文档结构
2. 已补齐 `parser-contract.md`
3. 已补齐 `redesign.md`
4. 已补齐 Python + FastAPI 的重设计方向

### 第二阶段：Python 服务骨架 ✅ 已完成

目标：

1. 建立 FastAPI 最小服务壳 ✅
2. 建立 `health / capabilities / parse` 三个接口 ✅
3. 建立 Pydantic schema 和统一错误码 ✅
4. 补契约测试 ✅

已完成内容：

- `app/main.py` - FastAPI 入口
- `app/bootstrap.py` - 应用初始化
- `app/api/v1/` - health, capabilities, parse 三个路由
- `app/contract/` - envelope, schemas, error_codes
- `app/youtube/` - domain, application, normalization, mapper
- `app/shared/` - settings, logging, http_client
- `tests/contract/` - 17 个契约测试用例

### 第三阶段：真实解析链路 🔜 下一步

当前目标：

1. 接入真实 metadata provider
2. 接入 transcript provider
3. 接入基础 metrics
4. 补 fixtures 回归测试

## 下一步目标

1. ~~建立 Python 项目骨架~~ ✅
2. ~~将现有契约落成 Pydantic schema~~ ✅
3. 确定 metadata provider 主链路和兜底链路
4. 设计 transcript provider 接入方式
5. 建立第一批真实样本 fixture

## 当前暂不纳入范围

- 搜索
- 批量频道抓取
- 下载视频
- 下载音频
- AI 分析
- 前端后台
