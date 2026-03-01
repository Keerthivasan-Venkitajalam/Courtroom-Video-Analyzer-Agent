"""
indexer.py
Manages real-time video stream ingestion into VideoDB / Twelve Labs,
and configures TurboPuffer hybrid search for textual conversational memory.
"""
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

# Note: These imports will be available after installing dependencies
# from videodb import connect, SceneExtractionType
# from vision_agents.plugins import turbopuffer

from backend.core.logging_config import get_logger
from backend.core.constants import (
    VIDEODB_API_KEY,
    TURBOPUFFER_API_KEY,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    PEGASUS_LEGAL_PROMPT,
    RRF_ALPHA,
    RRF_BM25_WEIGHT,
    RRF_VECTOR_WEIGHT,
    get_unified_timestamp_us,
)
from backend.core.timestamp_sync import TimestampSynchronizer

logger = get_logger(__name__)


@dataclass
class VideoMatch:
    """Represents a video search result with a playback URL."""
    start_time: float
    end_time: float
    description: str
    stream_url: str  # HLS manifest URL


@dataclass
class TranscriptSegment:
    """Represents a single diarised transcript segment."""
    segment_id: str
    text: str
    speaker: str
    start_timestamp_us: int
    end_timestamp_us: int
    confidence: float


class CourtroomIndexer:
    """
    Manages real-time video and transcript indexing.

    Integrates:
    - Twelve Labs Pegasus 1.2 for deep video understanding
    - TurboPuffer for hybrid (BM25 + vector) transcript search
    """

    def __init__(self, stream_url: str, session_id: str) -> None:
        """
        Args:
            stream_url: Live stream URL (e.g., RTSP).
            session_id: Unique session identifier used as namespace keys.
        """
        self.stream_url = stream_url
        self.session_id = session_id
        self.rt_stream = None
        self.scene_index_id: Optional[str] = None

        self.timestamp_sync = TimestampSynchronizer()

        # TODO: Initialise after videodb installation
        # self.vdb = connect(api_key=VIDEODB_API_KEY)

        # TODO: Initialise TurboPuffer hybrid search
        # Configured with alpha=0.7 (70% BM25 / 30% vector) to prioritise
        # exact legal terminology matching.
        # self.memory_rag = turbopuffer.TurboPufferRAG(
        #     namespace=f"court-session-{session_id}",
        #     chunk_size=CHUNK_SIZE,
        #     chunk_overlap=CHUNK_OVERLAP,
        #     search_mode="hybrid",
        #     rrf_alpha=RRF_ALPHA,
        # )

        logger.info(
            "CourtroomIndexer initialised | session=%s stream=%s timestamp_sync=enabled",
            session_id,
            stream_url,
        )

    # ------------------------------------------------------------------
    # Indexing lifecycle
    # ------------------------------------------------------------------

    async def start_live_indexing(self) -> bool:
        """
        Connect to the live stream and start asynchronous Twelve Labs Pegasus 1.2 indexing.

        Workflow:
        1. Establish VideoDB connection
        2. Create live stream object from the RTSP URL
        3. Begin async scene indexing with Pegasus 1.2

        Returns:
            True if indexing started successfully, False otherwise.
        """
        try:
            logger.info(
                "Connecting to live RTStream | url=%s session=%s",
                self.stream_url,
                self.session_id,
            )

            # TODO: Implement after videodb installation
            # self.vdb = connect(api_key=VIDEODB_API_KEY)
            # self.rt_stream = self.vdb.create_live_stream(
            #     stream_url=self.stream_url,
            #     name=f"Courtroom_{self.session_id}",
            # )
            # self.scene_index = self.rt_stream.index_scenes(
            #     prompt=PEGASUS_LEGAL_PROMPT,
            #     model_name="pegasus-1.2",
            #     extraction_type=SceneExtractionType.TEMPORAL,
            #     name=f"Court_Index_{self.session_id}",
            # )
            # self.scene_index_id = self.scene_index.id

            # Placeholder
            self.scene_index_id = f"mock_index_{self.session_id}"

            logger.info(
                "Pegasus 1.2 indexing started | index_id=%s model=twelve_labs/pegasus-1.2",
                self.scene_index_id,
            )
            return True

        except Exception:
            logger.exception("Failed to start live indexing")
            return False

    # ------------------------------------------------------------------
    # Transcript ingestion
    # ------------------------------------------------------------------

    async def add_transcript_chunk(
        self, text: str, speaker: str, timestamp: float
    ) -> bool:
        """
        Push a diarised transcript chunk into TurboPuffer.

        Args:
            text: Transcript text.
            speaker: Speaker role label (e.g., "Judge").
            timestamp: Timestamp in seconds from session start.

        Returns:
            True if successfully stored.
        """
        try:
            timestamp_us = int(timestamp * 1_000_000)
            synced_ts = self.timestamp_sync.sync_component("turbopuffer", timestamp_us)

            document = f"[{synced_ts}] {speaker}: {text}"

            # TODO: Implement after turbopuffer installation
            # await self.memory_rag.add_documents([document])

            logger.debug(
                "Transcript chunk added | speaker=%s time=%.2fs",
                speaker,
                synced_ts / 1_000_000,
            )
            return True

        except Exception:
            logger.exception("Failed to add transcript chunk")
            return False

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    async def query_video_moments(
        self, natural_language_query: str
    ) -> List[VideoMatch]:
        """
        Query the Twelve Labs index for semantic video moments.

        Returns a list of VideoMatch objects ordered by relevance, each
        containing exact timestamps and an HLS manifest URL for instant playback.
        """
        try:
            logger.info("Querying video moments | query='%s'", natural_language_query)

            # TODO: Implement after videodb installation
            # results = self.vdb.search(
            #     index_id=self.scene_index_id,
            #     query=natural_language_query,
            #     search_type="semantic",
            #     options={"threshold": 0.7, "max_results": 5},
            # )
            # formatted_results = [
            #     VideoMatch(
            #         start_time=res.start,
            #         end_time=res.end,
            #         description=res.text,
            #         stream_url=self._generate_hls_url(res.start, res.end),
            #     )
            #     for res in results
            # ]

            formatted_results = self._generate_mock_results(natural_language_query)

            if formatted_results:
                logger.info("Video query returned %d result(s)", len(formatted_results))
            else:
                logger.warning("Video query returned no results | query='%s'", natural_language_query)

            return formatted_results

        except Exception:
            logger.exception("Error querying video moments")
            return []

    async def query_transcript(
        self, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Execute a hybrid BM25 + vector search across all ingested transcript data.

        Args:
            query: Natural language search query.
            top_k: Maximum number of results to return.

        Returns:
            Ranked list of transcript result dicts with speaker, text, and scores.
        """
        try:
            logger.info("Querying transcript | query='%s' top_k=%d", query, top_k)

            # TODO: Implement after turbopuffer installation
            # results = await self.memory_rag.search(
            #     query=query,
            #     top_k=top_k,
            #     mode="hybrid",
            # )
            # formatted_results = [
            #     {
            #         "rank": i + 1,
            #         "text": r.text,
            #         "speaker": r.metadata.get("speaker_role", "Unknown"),
            #         "timestamp_us": r.metadata.get("timestamp_us", 0),
            #         "relevance_score": r.score,
            #         "bm25_score": r.bm25_score,
            #         "vector_score": r.vector_score,
            #     }
            #     for i, r in enumerate(results)
            # ]

            formatted_results = self._generate_mock_transcript_results(query, top_k)

            if formatted_results:
                logger.info("Transcript query returned %d result(s)", len(formatted_results))
            else:
                logger.warning("Transcript query returned no results | query='%s'", query)

            return formatted_results

        except Exception:
            logger.exception("Error querying transcript")
            return []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _generate_hls_url(self, start_time: float, end_time: float) -> str:
        """Build a placeholder HLS manifest URL for a video segment."""
        return (
            f"https://stream.videodb.io/{self.session_id}/"
            f"clip_{int(start_time)}_{int(end_time)}.m3u8"
        )

    def _generate_mock_results(self, query: str) -> List[VideoMatch]:
        """Return hard-coded mock video results keyed on common courtroom keywords."""
        mock_data: Dict[str, List[VideoMatch]] = {
            "witness testimony": [
                VideoMatch(120.5, 185.3, "Witness provides testimony about events on March 15th", self._generate_hls_url(120.5, 185.3)),
                VideoMatch(420.1, 495.7, "Cross-examination of witness regarding timeline", self._generate_hls_url(420.1, 495.7)),
            ],
            "objection": [
                VideoMatch(245.2, 258.9, "Defense attorney raises objection, sustained by judge", self._generate_hls_url(245.2, 258.9)),
            ],
            "evidence": [
                VideoMatch(310.4, 345.8, "Prosecution presents physical evidence exhibit A", self._generate_hls_url(310.4, 345.8)),
            ],
        }
        query_lower = query.lower()
        for keyword, results in mock_data.items():
            if keyword in query_lower:
                return results
        return []

    def _generate_mock_transcript_results(
        self, query: str, top_k: int
    ) -> List[Dict[str, Any]]:
        """Return keyword-matched mock transcript results."""
        mock_transcripts = [
            {"text": "[00:02:15] Judge: This court is now in session. Please be seated.",            "speaker": "Judge",       "timestamp_us": 135_000_000, "keywords": ["court", "session", "judge"]},
            {"text": "[00:03:42] Prosecution: Your Honor, the prosecution calls its first witness.", "speaker": "Prosecution", "timestamp_us": 222_000_000, "keywords": ["prosecution", "witness", "first"]},
            {"text": "[00:05:18] Witness: I was present at the scene on March 15th at 9 PM.",       "speaker": "Witness",      "timestamp_us": 318_000_000, "keywords": ["witness", "scene", "march", "present"]},
            {"text": "[00:07:45] Defense: Objection, Your Honor. Leading the witness.",              "speaker": "Defense",      "timestamp_us": 465_000_000, "keywords": ["objection", "defense", "leading"]},
            {"text": "[00:08:02] Judge: Sustained. Counsel, please rephrase your question.",         "speaker": "Judge",        "timestamp_us": 482_000_000, "keywords": ["sustained", "judge", "rephrase"]},
            {"text": "[00:10:30] Witness: The defendant was wearing a blue jacket that evening.",    "speaker": "Witness",      "timestamp_us": 630_000_000, "keywords": ["defendant", "witness", "jacket", "blue"]},
            {"text": "[00:12:15] Prosecution: Can you describe what happened next?",                 "speaker": "Prosecution",  "timestamp_us": 735_000_000, "keywords": ["prosecution", "describe", "happened"]},
            {"text": "[00:14:50] Witness: I heard a loud noise and saw someone running away.",       "speaker": "Witness",      "timestamp_us": 890_000_000, "keywords": ["witness", "noise", "running", "saw"]},
        ]

        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored: List[Dict[str, Any]] = []
        for t in mock_transcripts:
            matches = sum(1 for kw in t["keywords"] if kw in query_lower)
            if matches > 0:
                score = matches / len(query_words) if query_words else 0.0
                scored.append({
                    "rank": 0,
                    "text": t["text"],
                    "speaker": t["speaker"],
                    "timestamp_us": t["timestamp_us"],
                    "relevance_score": score,
                    "bm25_score": score * 0.6,
                    "vector_score": score * 0.4,
                })

        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        top = scored[:top_k]
        for i, r in enumerate(top, 1):
            r["rank"] = i
        return top


if __name__ == "__main__":
    from backend.core.logging_config import configure_logging
    configure_logging()

    async def _test() -> None:
        indexer = CourtroomIndexer(
            stream_url="rtsp://localhost:8554/courtcam",
            session_id="test-session",
        )
        await indexer.start_live_indexing()
        results = await indexer.query_video_moments("witness testimony")
        logger.info("Video results: %d", len(results))

    asyncio.run(_test())
