"""Transcript normalization module.

Normalizes raw transcript data into standardized domain models.
"""

from app.youtube.domain.models import YoutubeTranscript, YoutubeTranscriptSegment


class TranscriptNormalizer:
    """Normalizes transcript data from various sources.

    Converts raw subtitle data into standardized YoutubeTranscript
    domain models.
    """

    @staticmethod
    def normalize_from_provider(
        result: "TranscriptResult",
    ) -> YoutubeTranscript | None:
        """Normalize transcript from provider result.

        Args:
            result: TranscriptResult from provider

        Returns:
            YoutubeTranscript or None if result is not successful
        """
        if not result.success:
            return None

        # Convert segments to domain model
        segments = [
            YoutubeTranscriptSegment(
                text=seg.get("text", ""),
                start_ms=seg.get("start_ms", 0),
                end_ms=seg.get("end_ms", 0),
                speaker=seg.get("speaker"),
            )
            for seg in result.segments
        ]

        return YoutubeTranscript(
            text=result.text or "",
            segments=segments,
            language=result.language,
            is_auto_generated=result.is_auto_generated,
        )

    @staticmethod
    def normalize_from_ytdlp_data(
        data: dict, language_preference: list[str] | None = None
    ) -> YoutubeTranscript | None:
        """Normalize transcript from yt-dlp data.

        Args:
            data: yt-dlp info dict containing subtitles
            language_preference: Preferred languages for transcript

        Returns:
            YoutubeTranscript or None if no subtitles available
        """
        langs = language_preference or ["zh-Hans", "zh-Hant", "en", "zh"]

        subtitles = data.get("subtitles", {})
        auto_captions = data.get("automatic_captions", {})

        # Find best subtitle track
        selected_subs = None
        selected_lang = None
        is_auto = False

        # Try manual subtitles first
        for lang in langs:
            if lang in subtitles and subtitles[lang]:
                selected_subs = subtitles[lang]
                selected_lang = lang
                is_auto = False
                break

        # Fall back to auto captions
        if not selected_subs:
            for lang in langs:
                if lang in auto_captions and auto_captions[lang]:
                    selected_subs = auto_captions[lang]
                    selected_lang = lang
                    is_auto = True
                    break

        # Fall back to any available
        if not selected_subs:
            if subtitles:
                selected_lang = list(subtitles.keys())[0]
                selected_subs = subtitles[selected_lang]
                is_auto = False
            elif auto_captions:
                selected_lang = list(auto_captions.keys())[0]
                selected_subs = auto_captions[selected_lang]
                is_auto = True

        if not selected_subs:
            return None

        # Parse subtitle data
        segments = []
        full_text_parts = []

        for sub in selected_subs:
            text = sub.get("text", "").strip()
            if not text:
                continue

            start = sub.get("start", 0)
            duration = sub.get("duration", 0)

            segments.append(
                YoutubeTranscriptSegment(
                    text=text,
                    start_ms=int(start * 1000),
                    end_ms=int((start + duration) * 1000),
                    speaker=None,
                )
            )
            full_text_parts.append(text)

        return YoutubeTranscript(
            text=" ".join(full_text_parts),
            segments=segments,
            language=selected_lang,
            is_auto_generated=is_auto,
        )