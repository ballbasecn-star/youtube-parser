# 第三阶段：真实解析链路技术设计

## 一、概述

本文档描述 `youtube-parser` 第三阶段「真实解析链路」的技术实现方案，目标是接入真实数据源，实现完整的视频元数据、字幕和指标解析能力。

### 当前状态

- ✅ URL 规范化与 videoId 提取
- ✅ FastAPI 服务骨架
- ✅ 统一契约 schema
- ⏳ 真实元数据获取
- ⏳ 字幕/转录文本获取
- ⏳ 指标数据获取

### 目标

1. 接入真实 metadata provider
2. 接入 transcript provider
3. 接入基础 metrics
4. 补 fixtures 回归测试

---

## 二、整体架构

### 2.1 分层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                         │
│              app/api/v1/parse.py                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Application Layer                                │
│              ParseYoutubeService                                 │
│         (编排解析流程、协调 Provider、聚合结果)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Provider Layer                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │ OEmbedProvider  │ │ YtDlpProvider   │ │TranscriptProvider│   │
│  │   (主链路)       │ │   (兜底链路)     │ │   (字幕)         │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Normalization Layer                            │
│         (标准化数据格式、清洗、验证)                               │
│    app/youtube/normalization/                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Mapper Layer                                │
│           (映射到 ParsedContentPayload)                          │
│    app/youtube/mapper/parsed_content_mapper.py                   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
POST /api/v1/parse
       │
       ▼
┌─────────────────┐
│ URL Normalizer  │ ─── 提取 videoId，生成 canonicalUrl
└─────────────────┘
       │
       ▼
┌─────────────────┐     成功      ┌─────────────────┐
│ OEmbed Provider │ ────────────▶ │ 使用 oEmbed 数据 │
└─────────────────┘               └─────────────────┘
       │
       │ 失败/字段不全
       ▼
┌─────────────────┐     成功      ┌─────────────────┐
│ YtDlp Provider  │ ────────────▶ │ 使用 yt-dlp 数据 │
└─────────────────┘               └─────────────────┘
       │
       │ 失败
       ▼
┌─────────────────┐
│ 返回错误/Warning │
└─────────────────┘
       │
       ▼ (并行)
┌─────────────────┐
│TranscriptProvider│ ─── 获取字幕（失败不阻断主流程）
└─────────────────┘
       │
       ▼
┌─────────────────┐
│   Normalization │ ─── 标准化字段格式
└─────────────────┘
       │
       ▼
┌─────────────────┐
│     Mapper      │ ─── 映射到 ParsedContentPayload
└─────────────────┘
       │
       ▼
┌─────────────────┐
│  ApiEnvelope    │ ─── 统一响应包裹
└─────────────────┘
```

---

## 三、Provider 技术选型

### 3.1 Metadata Provider 选型对比

| 方案 | 优点 | 缺点 | 支持字段 | 推荐度 |
|------|------|------|----------|--------|
| **oEmbed API** | 官方接口、稳定、免费、无需认证 | 字段有限 | title, author_name, author_url, thumbnail_url | ⭐⭐⭐⭐ 主链路 |
| **yt-dlp** | 功能全面、元数据完整、字幕支持 | 较慢、需外部依赖 | 全部字段 | ⭐⭐⭐⭐ 兜底链路 |
| **YouTube Data API v3** | 官方、完整 | 需要 API Key、配额限制 | 全部字段 | ⭐⭐ 可选 |
| **页面 JSON 解析** | 无需额外依赖 | 脆弱、结构易变 | 大部分 | ⭐ 不推荐 |

### 3.2 oEmbed API 详细说明

**端点**：
```
GET https://www.youtube.com/oembed?url={VIDEO_URL}&format=json
```

**特点**：
- ✅ 完全免费
- ✅ 无需 API Key
- ✅ 无需认证
- ✅ 无明确配额限制
- ✅ 响应快速

**返回示例**：
```json
{
  "title": "Rick Astley - Never Gonna Give You Up",
  "author_name": "Rick Astley",
  "author_url": "https://www.youtube.com/@RickAstleyYT",
  "type": "video",
  "height": 113,
  "width": 200,
  "version": "1.0",
  "provider_name": "YouTube",
  "provider_url": "https://www.youtube.com/",
  "thumbnail_height": 360,
  "thumbnail_width": 480,
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
  "html": "<iframe>...</iframe>"
}
```

**字段映射**：
| oEmbed 字段 | 契约字段 | 备注 |
|-------------|----------|------|
| title | title | ✅ |
| author_name | author.name | ✅ |
| author_url | author.profileUrl | ✅ |
| thumbnail_url | media.covers[].url | ✅ |
| - | description | ❌ 无 |
| - | author.externalAuthorId | ❌ 无 channel_id |
| - | metrics.views | ❌ 无 |

### 3.3 yt-dlp 详细说明

**安装**：
```bash
pip install yt-dlp
```

**Python API 用法**：
```python
import yt_dlp

ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'writesubtitles': True,       # 下载字幕
    'writeautomaticsub': True,    # 自动生成的字幕
    'subtitleslangs': ['zh-Hans', 'zh-Hant', 'en'],
    'skip_download': True,        # 不下载视频文件
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(video_url, download=False)
```

**info 字典包含字段**：
| 字段 | 类型 | 说明 |
|------|------|------|
| title | str | 视频标题 |
| description | str | 视频简介 |
| uploader | str | 上传者名称 |
| channel_id | str | 频道 ID |
| channel_url | str | 频道 URL |
| view_count | int | 播放量 |
| like_count | int | 点赞数 |
| comment_count | int | 评论数 |
| thumbnail | str | 缩略图 URL |
| thumbnails | list | 缩略图列表 |
| duration | int | 时长（秒） |
| upload_date | str | 上传日期 (YYYYMMDD) |
| tags | list | 标签列表 |
| subtitles | dict | 手动字幕 |
| automatic_captions | dict | 自动字幕 |

### 3.4 Transcript Provider 选型

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **yt-dlp** | 功能完整、支持自动字幕、稳定 | 较慢 | ⭐⭐⭐⭐⭐ 推荐 |
| **youtube-transcript-api** | 轻量、快速 | 有时被限流 | ⭐⭐⭐ 备选 |

**推荐**：复用 yt-dlp，与 Metadata Provider 共享同一个 info 对象

### 3.5 最终选型

```
┌─────────────────────────────────────────────────────────┐
│                    Metadata Provider                     │
├─────────────────────────────────────────────────────────┤
│  主链路: oEmbed (快速、稳定、免费)                         │
│  兜底链路: yt-dlp (完整、功能全)                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Transcript Provider                    │
├─────────────────────────────────────────────────────────┤
│  主链路: yt-dlp (与 metadata 共享 info)                   │
│  备选: youtube-transcript-api                           │
└─────────────────────────────────────────────────────────┘
```

---

## 四、接口设计

### 4.1 Provider 基类

```python
# app/youtube/providers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderResult:
    """Provider 返回结果"""

    success: bool
    data: dict[str, Any] | None
    error: str | None = None
    source: str = ""  # 数据来源标识
    fields: list[str] = field(default_factory=list)  # 成功获取的字段


class BaseProvider(ABC):
    """Provider 抽象基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider 名称，用于日志和追踪"""
        pass

    @property
    @abstractmethod
    def supported_fields(self) -> list[str]:
        """该 Provider 支持的字段列表"""
        pass

    @abstractmethod
    async def fetch(self, video_id: str) -> ProviderResult:
        """
        获取数据

        Args:
            video_id: YouTube 视频 ID

        Returns:
            ProviderResult 包含获取结果
        """
        pass

    def supports_field(self, field: str) -> bool:
        """检查是否支持指定字段"""
        return field in self.supported_fields
```

### 4.2 OEmbed Provider

```python
# app/youtube/providers/oembed_provider.py
import httpx
from app.youtube.providers.base import BaseProvider, ProviderResult


class OEmbedProvider(BaseProvider):
    """oEmbed 元数据 Provider

    使用 YouTube oEmbed API 获取基础元数据。
    优点：免费、无需认证、响应快速。
    限制：无 description、无 metrics、无 channel_id。
    """

    name = "oembed"
    OEMBED_URL = "https://www.youtube.com/oembed"

    @property
    def supported_fields(self) -> list[str]:
        return [
            "title",
            "author_name",
            "author_url",
            "thumbnail_url",
        ]

    async def fetch(self, video_id: str) -> ProviderResult:
        url = f"https://www.youtube.com/watch?v={video_id}"
        params = {"url": url, "format": "json"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.OEMBED_URL,
                    params=params,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return ProviderResult(
                        success=True,
                        data=data,
                        source=self.name,
                        fields=self.supported_fields,
                    )

                return ProviderResult(
                    success=False,
                    data=None,
                    error=f"oEmbed request failed with status {response.status_code}",
                    source=self.name,
                )

        except httpx.TimeoutException:
            return ProviderResult(
                success=False,
                data=None,
                error="oEmbed request timed out",
                source=self.name,
            )
        except Exception as e:
            return ProviderResult(
                success=False,
                data=None,
                error=str(e),
                source=self.name,
            )
```

### 4.3 YtDlp Provider

```python
# app/youtube/providers/yt_dlp_provider.py
import yt_dlp
from app.youtube.providers.base import BaseProvider, ProviderResult


class YtDlpProvider(BaseProvider):
    """yt-dlp 元数据和字幕 Provider

    使用 yt-dlp 库获取完整的视频信息。
    优点：字段完整、支持字幕。
    限制：较慢、需要外部依赖。
    """

    name = "yt_dlp"

    @property
    def supported_fields(self) -> list[str]:
        return [
            "title",
            "description",
            "uploader",
            "channel_id",
            "channel_url",
            "view_count",
            "like_count",
            "comment_count",
            "thumbnail",
            "thumbnails",
            "duration",
            "upload_date",
            "tags",
            "subtitles",
            "automatic_captions",
        ]

    async def fetch(self, video_id: str) -> ProviderResult:
        url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["zh-Hans", "zh-Hant", "en", "zh"],
            "skip_download": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if info:
                    return ProviderResult(
                        success=True,
                        data=info,
                        source=self.name,
                        fields=self._get_available_fields(info),
                    )

                return ProviderResult(
                    success=False,
                    data=None,
                    error="yt-dlp returned no data",
                    source=self.name,
                )

        except yt_dlp.utils.DownloadError as e:
            return ProviderResult(
                success=False,
                data=None,
                error=f"Video unavailable: {e}",
                source=self.name,
            )
        except Exception as e:
            return ProviderResult(
                success=False,
                data=None,
                error=str(e),
                source=self.name,
            )

    def _get_available_fields(self, info: dict) -> list[str]:
        """获取实际可用的字段列表"""
        return [f for f in self.supported_fields if info.get(f) is not None]
```

### 4.4 Provider 编排器

```python
# app/youtube/providers/metadata_provider_orchestrator.py
import structlog
from app.youtube.providers.base import ProviderResult
from app.youtube.providers.oembed_provider import OEmbedProvider
from app.youtube.providers.yt_dlp_provider import YtDlpProvider

logger = structlog.get_logger(__name__)


class MetadataProviderOrchestrator:
    """元数据 Provider 编排器

    负责协调多个 Provider，实现主链路和兜底链路的降级逻辑。
    """

    def __init__(self):
        self.oembed_provider = OEmbedProvider()
        self.ytdlp_provider = YtDlpProvider()
        # Provider 链：优先级从高到低
        self.providers = [
            self.oembed_provider,   # 主链路
            self.ytdlp_provider,    # 兜底链路
        ]

    async def fetch_metadata(self, video_id: str) -> tuple[ProviderResult, str]:
        """
        获取元数据，按优先级尝试各 Provider

        Args:
            video_id: YouTube 视频 ID

        Returns:
            (ProviderResult, used_provider_name)
        """
        errors = []

        for provider in self.providers:
            logger.info(
                "trying_provider",
                provider=provider.name,
                video_id=video_id,
            )

            result = await provider.fetch(video_id)

            if result.success:
                logger.info(
                    "provider_success",
                    provider=provider.name,
                    video_id=video_id,
                    fields=result.fields,
                )
                return result, provider.name

            errors.append(f"{provider.name}: {result.error}")
            logger.warning(
                "provider_failed",
                provider=provider.name,
                error=result.error,
            )

        # 所有 Provider 都失败
        error_msg = "; ".join(errors)
        logger.error("all_providers_failed", errors=error_msg)

        return ProviderResult(
            success=False,
            data=None,
            error=error_msg,
            source="orchestrator",
        ), "none"
```

---

## 五、降级策略

### 5.1 Metadata 降级规则

```
┌─────────────┐
│   oEmbed    │ ──成功──→ 使用 oEmbed 数据（快速响应）
└─────────────┘            需要补充：description, metrics
      │
      │ 失败 / 字段不全
      ▼
┌─────────────┐
│   yt-dlp    │ ──成功──→ 使用 yt-dlp 数据（完整）
└─────────────┘
      │
      │ 失败
      ▼
┌─────────────────────────────────────┐
│ 返回错误或部分数据 + warnings         │
│ 错误码: UPSTREAM_CHANGED             │
└─────────────────────────────────────┘
```

### 5.2 Transcript 独立处理

```
字幕获取是独立流程，不影响整体解析成功：

成功 → 填充 transcript 和 segments
失败 → 添加 warning: TRANSCRIPT_UNAVAILABLE
       transcript 字段为 null
       不阻断主流程
```

### 5.3 字段补全策略

当 oEmbed 成功但字段不全时：

| 缺失字段 | 补全策略 |
|----------|----------|
| description | 调用 yt-dlp 补全 |
| metrics (views/likes/comments) | 调用 yt-dlp 补全 |
| channel_id | 调用 yt-dlp 补全 |

**优化**：可以先返回 oEmbed 数据，同时后台触发 yt-dlp 补全（可选）

---

## 六、Normalizer 设计

### 6.1 Metadata Normalizer

```python
# app/youtube/normalization/metadata_normalizer.py
from datetime import datetime
from app.youtube.domain.models import YoutubeVideo, YoutubeChannel, YoutubeThumbnail


class MetadataNormalizer:
    """元数据标准化器"""

    @staticmethod
    def normalize_oembed(data: dict, video_id: str) -> YoutubeVideo:
        """标准化 oEmbed 数据"""
        return YoutubeVideo(
            video_id=video_id,
            canonical_url=f"https://www.youtube.com/watch?v={video_id}",
            title=data.get("title"),
            description=None,  # oEmbed 无此字段
            channel=YoutubeChannel(
                name=data.get("author_name"),
                profile_url=data.get("author_url"),
            ),
            thumbnails=[
                YoutubeThumbnail(
                    url=data.get("thumbnail_url"),
                    width=data.get("thumbnail_width"),
                    height=data.get("thumbnail_height"),
                )
            ],
        )

    @staticmethod
    def normalize_ytdlp(data: dict, video_id: str) -> YoutubeVideo:
        """标准化 yt-dlp 数据"""
        # 解析上传日期
        published_at = None
        if data.get("upload_date"):
            try:
                published_at = datetime.strptime(
                    data["upload_date"], "%Y%m%d"
                )
            except ValueError:
                pass

        return YoutubeVideo(
            video_id=video_id,
            canonical_url=f"https://www.youtube.com/watch?v={video_id}",
            title=data.get("title"),
            description=data.get("description"),
            published_at=published_at,
            duration_seconds=data.get("duration"),
            tags=data.get("tags", []),
            channel=YoutubeChannel(
                channel_id=data.get("channel_id"),
                name=data.get("uploader"),
                profile_url=data.get("channel_url"),
            ),
            thumbnails=[
                YoutubeThumbnail(
                    url=t.get("url"),
                    width=t.get("width"),
                    height=t.get("height"),
                )
                for t in data.get("thumbnails", [])
            ],
            raw_data={
                "source": "yt_dlp",
                "view_count": data.get("view_count"),
                "like_count": data.get("like_count"),
                "comment_count": data.get("comment_count"),
            },
        )
```

### 6.2 Transcript Normalizer

```python
# app/youtube/normalization/transcript_normalizer.py
import re
from app.youtube.domain.models import YoutubeTranscript, YoutubeTranscriptSegment


class TranscriptNormalizer:
    """字幕标准化器"""

    @staticmethod
    def normalize_ytdlp_subtitles(
        subtitles: dict,
        language_preference: list[str] = None,
    ) -> YoutubeTranscript | None:
        """
        标准化 yt-dlp 字幕数据

        Args:
            subtitles: yt-dlp 返回的字幕字典
            language_preference: 语言偏好列表，如 ["zh-Hans", "en"]

        Returns:
            标准化的 YoutubeTranscript 或 None
        """
        if not subtitles:
            return None

        # 选择字幕语言
        lang_preference = language_preference or ["zh-Hans", "zh-Hant", "en", "zh"]
        selected_lang = None
        selected_subs = None

        for lang in lang_preference:
            if lang in subtitles:
                selected_lang = lang
                selected_subs = subtitles[lang]
                break

        if not selected_subs:
            # 使用第一个可用语言
            selected_lang = list(subtitles.keys())[0]
            selected_subs = subtitles[selected_lang]

        # 解析字幕内容
        segments = []
        full_text = []

        for sub in selected_subs:
            text = sub.get("text", "").strip()
            if not text:
                continue

            start = sub.get("start", 0)
            duration = sub.get("duration", 0)

            segments.append(YoutubeTranscriptSegment(
                text=text,
                start_ms=int(start * 1000),
                end_ms=int((start + duration) * 1000),
            ))
            full_text.append(text)

        return YoutubeTranscript(
            text=" ".join(full_text),
            segments=segments,
            language=selected_lang,
            is_auto_generated=selected_lang.startswith("a-"),
        )
```

---

## 七、错误处理

### 7.1 错误码映射

| 场景 | 错误码 | HTTP 状态 |
|------|--------|-----------|
| 视频 ID 无效 | INVALID_INPUT | 400 |
| 非法 YouTube URL | UNSUPPORTED_URL | 400 |
| 视频不存在/私密 | UPSTREAM_CHANGED | 500 |
| 需要登录/地区限制 | AUTH_REQUIRED | 401 |
| 上游限流 | RATE_LIMITED | 429 |
| 上游超时 | PARSER_TIMEOUT | 504 |
| 内部错误 | INTERNAL_ERROR | 500 |

### 7.2 Warning 规则

| Warning | 条件 |
|---------|------|
| TRANSCRIPT_UNAVAILABLE | 字幕获取失败 |
| METRICS_UNAVAILABLE | 指标数据缺失 |
| DESCRIPTION_PARTIAL | 简介不完整 |
| AUTHOR_PARTIAL | 作者信息不完整 |

---

## 八、依赖变更

### 8.1 pyproject.toml 更新

```toml
dependencies = [
    # ... existing
    "yt-dlp>=2025.1.0",
]
```

### 8.2 可选依赖

```toml
[project.optional-dependencies]
dev = [
    # ... existing
]
transcript-backup = [
    "youtube-transcript-api>=0.6.0",  # 备选字幕方案
]
```

---

## 九、测试策略

### 9.1 单元测试

- Provider 接口测试
- Normalizer 转换测试
- 降级逻辑测试

### 9.2 集成测试

- 真实视频解析测试
- 私密视频处理测试
- 字幕缺失处理测试

### 9.3 Fixtures 样本

| 视频 ID | 类型 | 用途 |
|---------|------|------|
| dQw4w9WgXcQ | 普通视频 | 基础解析测试 |
| (shorts ID) | Shorts | shorts 格式测试 |
| (无字幕视频) | 无字幕 | 字幕缺失场景 |
| (私密视频) | 私密 | 权限错误场景 |

---

## 十、实现计划

| 步骤 | 内容 | 优先级 |
|------|------|--------|
| 1 | 实现 BaseProvider 和 ProviderResult | P0 |
| 2 | 实现 OEmbedProvider | P0 |
| 3 | 实现 YtDlpProvider | P0 |
| 4 | 实现 MetadataProviderOrchestrator | P0 |
| 5 | 实现 MetadataNormalizer | P0 |
| 6 | 实现 TranscriptNormalizer | P1 |
| 7 | 更新 ParseYoutubeService 集成 Provider | P0 |
| 8 | 补充 fixtures 测试样本 | P1 |
| 9 | 更新 capabilities 端点 | P2 |
| 10 | 补充集成测试 | P1 |

---

## 十一、风险与对策

| 风险 | 可能性 | 影响 | 对策 |
|------|--------|------|------|
| yt-dlp 被限流 | 中 | 高 | oEmbed 主链路 + 重试机制 |
| 字幕不可用 | 高 | 低 | 独立处理，返回 warning |
| 页面结构变化 | 低 | 高 | oEmbed + yt-dlp 双保险 |
| 性能问题 | 中 | 中 | 缓存机制（后续） |
| oEmbed 接口变更 | 低 | 高 | yt-dlp 兜底 |

---

## 十二、后续优化方向

1. **缓存机制**：对元数据做短 TTL 缓存
2. **异步处理**：大量请求时异步队列处理
3. **更多 Provider**：接入 YouTube Data API v3 作为补充
4. **指标监控**：Provider 成功率、响应时间监控
5. **智能降级**：根据历史成功率动态选择 Provider

---

## 更新记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2025-03-27 | v1.0 | 初版设计 |