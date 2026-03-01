"""
tests/unit/test_frame_processing.py
Unit tests for CourtroomProcessor frame processing.
"""
import pytest

from backend.processing.processor import CourtroomProcessor


class TestCourtroomProcessor:

    def test_initialises_with_correct_fps(self):
        processor = CourtroomProcessor(fps=5)
        assert processor.fps == 5

    async def test_process_frame_returns_state_dict(self):
        processor = CourtroomProcessor(fps=5)
        result = await processor.process_frame(None, 0.0)
        assert isinstance(result, dict)
        assert "timestamp" in result
        assert "entities_visible" in result
        assert "inferred_speaker" in result
        assert "frame_number" in result
        assert "consistent" in result

    async def test_frame_counter_increments(self):
        processor = CourtroomProcessor(fps=5)
        for i in range(3):
            result = await processor.process_frame(None, i * 0.2)
            assert result["frame_number"] == i + 1

    async def test_process_frame_does_not_raise(self):
        """Frame processing must not raise even with None frame data."""
        processor = CourtroomProcessor(fps=5)
        result = await processor.process_frame(None, 1.0)
        assert "error" not in result

    async def test_get_stats_after_frames(self):
        processor = CourtroomProcessor(fps=5)
        for i in range(5):
            await processor.process_frame(None, i * 0.2)
        stats = processor.get_stats()
        assert stats["total_frames"] == 5
        assert stats["fps"] == 5
        assert isinstance(stats["speaker_changes"], int)

    async def test_audio_chunk_returns_none_in_placeholder_mode(self):
        processor = CourtroomProcessor(fps=5)
        text, speaker = await processor.process_audio_chunk(b"hello world")
        # Placeholder implementation should return (None, None)
        assert text is None
        assert speaker is None

    def test_get_speaker_history_initially_empty(self):
        processor = CourtroomProcessor(fps=5)
        assert processor.get_speaker_history() == []
