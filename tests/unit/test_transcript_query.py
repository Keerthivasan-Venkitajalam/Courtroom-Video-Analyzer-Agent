"""
tests/unit/test_transcript_query.py
Unit tests for CourtroomIndexer transcript query logic.
"""
import pytest

from backend.indexing.indexer import CourtroomIndexer


@pytest.fixture
async def indexer():
    idx = CourtroomIndexer(stream_url="rtsp://localhost:8554/courtcam", session_id="unit-test")
    await idx.start_live_indexing()
    return idx


class TestTranscriptQuery:

    async def test_query_returns_list(self, indexer):
        results = await indexer.query_transcript("objection", top_k=5)
        assert isinstance(results, list)

    async def test_keyword_matching_objection(self, indexer):
        results = await indexer.query_transcript("objection", top_k=5)
        assert len(results) > 0, "Expected at least one result for 'objection'"

    async def test_result_has_required_fields(self, indexer):
        results = await indexer.query_transcript("witness", top_k=3)
        for r in results:
            assert "rank" in r
            assert "text" in r
            assert "speaker" in r
            assert "timestamp_us" in r
            assert "relevance_score" in r

    async def test_top_k_respected(self, indexer):
        results = await indexer.query_transcript("judge witness prosecution", top_k=2)
        assert len(results) <= 2

    async def test_results_sorted_by_relevance(self, indexer):
        results = await indexer.query_transcript("witness testimony", top_k=5)
        scores = [r["relevance_score"] for r in results]
        assert scores == sorted(scores, reverse=True), "Results should be sorted by descending relevance"

    async def test_no_match_returns_empty(self, indexer):
        results = await indexer.query_transcript("xyznomatch12345", top_k=5)
        assert results == []

    async def test_ranks_start_at_one(self, indexer):
        results = await indexer.query_transcript("judge", top_k=5)
        if results:
            assert results[0]["rank"] == 1
