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
- **真实元数据获取 (oEmbed + yt-dlp)**
- **字幕/转录文本提取**
- **指标数据获取 (views, likes, comments)**

当前仓库已完成真实解析链路，可获取完整的视频元数据、字幕和指标。

## 当前优先级

✅ 所有优先级已完成：
1. parser 契约 ✅
2. Python 技术架构 ✅
3. provider 分层 ✅
4. 文档体系 ✅
5. 真实元数据与 transcript 主链路 ✅

## 当前工程工作

### 第一阶段：文档与契约冻结 ✅ 已完成

### 第二阶段：Python 服务骨架 ✅ 已完成

### 第三阶段：真实解析链路 ✅ 已完成

目标：

1. 接入真实 metadata provider ✅
2. 接入 transcript provider ✅
3. 接入基础 metrics ✅
4. 补 fixtures 回归测试 ✅

已完成内容：

- `app/youtube/providers/base.py` - Provider 基类
- `app/youtube/providers/oembed_provider.py` - oEmbed Provider (主链路)
- `app/youtube/providers/yt_dlp_provider.py` - yt-dlp Provider (兜底+字幕)
- `app/youtube/providers/orchestrator.py` - Provider 编排器
- `app/youtube/normalization/metadata_normalizer.py` - 元数据标准化
- `app/youtube/normalization/transcript_normalizer.py` - 字幕标准化
- 18 个契约测试全部通过

## 下一步目标（可选增强）

1. 缓存机制 - 对元数据做短 TTL 缓存
2. 更多 Provider - YouTube Data API v3 作为补充
3. 指标监控 - Provider 成功率、响应时间监控
4. 集成测试 - 更多真实样本测试

## 当前暂不纳入范围

- 搜索
- 批量频道抓取
- 下载视频
- 下载音频
- AI 分析
- 前端后台
