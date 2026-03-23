export interface ParsedMediaItem {
  url: string;
  mimeType: string | null;
  width: number | null;
  height: number | null;
  durationMs: number | null;
}

export interface ParsedWarningPayload {
  code: string;
  message: string;
}

export interface ParsedContentPayload {
  platform: string;
  sourceType: string;
  externalId: string | null;
  canonicalUrl: string;
  title: string;
  summary: string | null;
  author: {
    externalAuthorId: string | null;
    name: string | null;
    handle: string | null;
    profileUrl: string | null;
    avatarUrl: string | null;
  };
  publishedAt: string | null;
  language: string | null;
  content: {
    rawText: string | null;
    transcript: string | null;
    segments: Array<{
      text: string;
      startMs: number | null;
      endMs: number | null;
      speaker: string | null;
    }>;
  };
  metrics: {
    views: number | null;
    likes: number | null;
    comments: number | null;
    shares: number | null;
    favorites: number | null;
  };
  tags: string[];
  media: {
    covers: ParsedMediaItem[];
    images: ParsedMediaItem[];
    videos: ParsedMediaItem[];
    audios: ParsedMediaItem[];
  };
  rawPayload: Record<string, unknown>;
  warnings: ParsedWarningPayload[];
}

export interface ParseYoutubeInput {
  sourceText?: string;
  sourceUrl?: string;
  languageHint?: string;
}

export interface ParseYoutubeResult {
  payload: ParsedContentPayload;
}

const YOUTUBE_HOSTS = new Set([
  "youtube.com",
  "www.youtube.com",
  "m.youtube.com",
  "youtu.be",
  "www.youtu.be"
]);

function normalizeUrlCandidate(rawValue: string) {
  try {
    const url = new URL(rawValue.trim());
    return url;
  } catch {
    return null;
  }
}

function extractUrlFromText(sourceText: string) {
  const match = sourceText.match(/https?:\/\/[^\s]+/i);
  return match?.[0] ?? null;
}

function resolveVideoId(url: URL) {
  const host = url.hostname.toLowerCase();
  if (!YOUTUBE_HOSTS.has(host)) {
    return null;
  }

  if (host.includes("youtu.be")) {
    const candidate = url.pathname.split("/").filter(Boolean)[0] ?? null;
    return candidate;
  }

  if (url.pathname === "/watch") {
    return url.searchParams.get("v");
  }

  const pathParts = url.pathname.split("/").filter(Boolean);
  if (pathParts.length >= 2 && ["shorts", "live", "embed"].includes(pathParts[0])) {
    return pathParts[1];
  }

  return null;
}

function canonicalizeYoutubeUrl(videoId: string) {
  return `https://www.youtube.com/watch?v=${videoId}`;
}

function cleanSourceText(sourceText?: string, sourceUrl?: string) {
  if (!sourceText) {
    return null;
  }

  let cleaned = sourceText;
  if (sourceUrl) {
    cleaned = cleaned.replace(sourceUrl, " ");
  }

  cleaned = cleaned.replace(/https?:\/\/[^\s]+/gi, " ");
  cleaned = cleaned.replace(/\s+/g, " ").trim();
  return cleaned || null;
}

function deriveTitle(cleanedText: string | null, videoId: string) {
  if (cleanedText && cleanedText.length >= 6 && cleanedText.length <= 140) {
    return cleanedText;
  }
  return `YouTube Video ${videoId}`;
}

export function parseYoutubeSource(input: ParseYoutubeInput): ParseYoutubeResult {
  const sourceUrl = input.sourceUrl?.trim() || extractUrlFromText(input.sourceText ?? "") || null;
  if (!sourceUrl) {
    throw new Error("MISSING_SOURCE");
  }

  const parsedUrl = normalizeUrlCandidate(sourceUrl);
  if (!parsedUrl) {
    throw new Error("INVALID_URL");
  }

  const videoId = resolveVideoId(parsedUrl);
  if (!videoId) {
    throw new Error("UNSUPPORTED_URL");
  }

  const canonicalUrl = canonicalizeYoutubeUrl(videoId);
  const cleanedText = cleanSourceText(input.sourceText, sourceUrl);

  // 当前先保证最小可导入结构稳定，复杂元数据后续再接真实解析链路。
  const payload: ParsedContentPayload = {
    platform: "youtube",
    sourceType: "video",
    externalId: videoId,
    canonicalUrl,
    title: deriveTitle(cleanedText, videoId),
    summary: cleanedText,
    author: {
      externalAuthorId: null,
      name: null,
      handle: null,
      profileUrl: null,
      avatarUrl: null
    },
    publishedAt: null,
    language: input.languageHint ?? null,
    content: {
      rawText: cleanedText ?? canonicalUrl,
      transcript: null,
      segments: []
    },
    metrics: {
      views: null,
      likes: null,
      comments: null,
      shares: null,
      favorites: null
    },
    tags: [],
    media: {
      covers: [
        {
          url: `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`,
          mimeType: "image/jpeg",
          width: null,
          height: null,
          durationMs: null
        }
      ],
      images: [],
      videos: [],
      audios: []
    },
    rawPayload: {
      matchedSourceUrl: sourceUrl,
      extractedFromShareText: Boolean(input.sourceText && !input.sourceUrl),
      parserStage: "minimal-canonicalization"
    },
    warnings: [
      {
        code: "PARTIAL_PARSE",
        message: "当前仅完成 YouTube URL 规范化与最小元数据映射，未抓取真实标题、转录和指标。"
      }
    ]
  };

  return { payload };
}
