"""
tests/unit/test_video_query.py
Unit tests for CourtroomIndexer video moment query logic.
"""
import pytest

from backend.indexing.indexer import CourtroomIndexer, VideoMatch


@pytest.fixture
async def indexer():
    idx = CourtroomIndexer(stream_url="rtsp://localhost:8554/courtcam", session_id="unit-test")
    await idx.start_live_indexing()
    return idx


class TestVideoQuery:

    async def test_query_returns_list(self, indexer):
        results = await indexer.query_video_moments("witness testimony")
        assert isinstance(results, list)

    async def test_keyword_match_witness_testimony(self, indexer):
        results = await indexer.query_video_moments("witness testimony")
        assert len(results) > 0

    async def test_result_is_video_match(self, indexer):
        results = await indexer.query_video_moments("evidence")
        for r in results:
            assert isinstance(r, VideoMatch)

    async def test_hls_url_format(self, indexer):
        results = await indexer.query_video_moments("objection")
        for r in results:
            assert r.stream_url.startswith("https://"), f"Expected HTTPS URL, got: {r.stream_url}"
            assert r.stream_url.endswith(".m3u8"), f"Expected HLS URL ending in .m3u8, got: {r.stream_url}"

    async def test_timestamps_are_valid(self, indexer):
        results = await indexer.query_video_moments("witness testimony")
        for r in results:
            assert r.start_time >= 0
            assert r.end_time > r.start_time, "End time must be after start time"

    async def test_no_match_returns_empty(self, indexer):
        results = await indexer.query_video_moments("xyznomatch12345")
        assert results == []
