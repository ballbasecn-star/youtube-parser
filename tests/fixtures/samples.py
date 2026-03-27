"""Test fixtures for YouTube parser.

This module contains sample YouTube video data for regression testing.
"""

# Sample YouTube video IDs for testing
SAMPLE_VIDEO_IDS = {
    "rickroll": "dQw4w9WgXcQ",
    "short_sample": "abc123xyz",
    "live_sample": "testLive123",
}

# Sample URLs for different YouTube URL formats
SAMPLE_URLS = {
    "watch": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "watch_mobile": "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
    "short_link": "https://youtu.be/dQw4w9WgXcQ",
    "shorts": "https://www.youtube.com/shorts/abc123xyz",
    "live": "https://www.youtube.com/live/testLive123",
    "embed": "https://www.youtube.com/embed/dQw4w9WgXcQ",
}

# Non-YouTube URLs for testing unsupported URL handling
NON_YOUTUBE_URLS = [
    "https://vimeo.com/123456",
    "https://www.bilibili.com/video/BV123456",
    "https://www.tiktok.com/@user/video/123456",
    "https://twitter.com/user/status/123456",
]