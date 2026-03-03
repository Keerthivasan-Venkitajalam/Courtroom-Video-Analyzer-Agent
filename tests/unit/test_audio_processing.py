"""
tests/unit/test_audio_processing.py
Unit tests for CourtroomProcessor audio chunk processing.
"""
import pytest

from backend.processing.processor import CourtroomProcessor


class TestAudioProcessing:

    async def test_returns_tuple(self):
        processor = CourtroomProcessor(fps=5)
        result = await processor.process_audio_chunk(b"hello")
        assert isinstance(result, tuple)
        assert len(result) == 2

    async def test_silence_returns_none_none(self):
        """Silent audio (null bytes) must not produce a spurious transcript."""
        processor = CourtroomProcessor(fps=5)
        silence = b"\x00" * 2048
        text, speaker = await processor.process_audio_chunk(silence)
        assert text is None
        assert speaker is None

    async def test_does_not_raise_on_empty_bytes(self):
        processor = CourtroomProcessor(fps=5)
        text, speaker = await processor.process_audio_chunk(b"")
        # Should return (None, None), not raise
        assert text is None
        assert speaker is None

    async def test_speaker_state_unchanged_after_placeholder(self):
        """In placeholder mode the speaker state should remain 'Unknown'."""
        processor = CourtroomProcessor(fps=5)
        assert processor.current_speaker == "Unknown"
        await processor.process_audio_chunk(b"some audio")
        assert processor.current_speaker == "Unknown"

    def test_speaker_role_mapping(self):
        processor = CourtroomProcessor(fps=5)
        assert processor._map_speaker_id_to_role(0) == "Judge"
        assert processor._map_speaker_id_to_role(1) == "Witness"
        assert processor._map_speaker_id_to_role(2) == "Prosecution"
        assert processor._map_speaker_id_to_role(3) == "Defense"
        assert processor._map_speaker_id_to_role(99) == "Speaker_99"
