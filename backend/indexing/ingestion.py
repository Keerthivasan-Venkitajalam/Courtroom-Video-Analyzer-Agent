"""
ingestion.py
Transcript segment ingestion into TurboPuffer RAG.
Handles diarised transcript segments with speaker role metadata.
"""
import asyncio
from typing import Any, Dict, List
from dataclasses import dataclass, field

from backend.core.logging_config import get_logger
from backend.core.constants import (
    TURBOPUFFER_API_KEY,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    SPEAKER_ROLES,
    get_unified_timestamp_us,
)

# Note: TurboPuffer client will be installed separately
# from turbopuffer import TurboPuffer

logger = get_logger(__name__)


@dataclass
class TranscriptSegment:
    """Represents a single diarised transcript segment."""
    text: str
    speaker_id: int
    speaker_role: str
    timestamp_us: int
    confidence: float = 0.0


class TranscriptIngestion:
    """
    Ingests diarised transcript segments into TurboPuffer.

    Segments are stored as '[HH:MM:SS] SpeakerRole: text' strings,
    enabling both keyword and semantic search via TurboPuffer's hybrid engine.
    """

    def __init__(self, session_id: str) -> None:
        """
        Args:
            session_id: Unique session identifier used as TurboPuffer namespace.
        """
        self.session_id = session_id
        self.namespace = f"court-session-{session_id}"
        self.client = None
        self.ingested_count: int = 0

        logger.info(
            "TranscriptIngestion initialised | namespace=%s chunk_size=%d chunk_overlap=%d",
            self.namespace,
            CHUNK_SIZE,
            CHUNK_OVERLAP,
        )

    async def initialize(self) -> None:
        """Initialise the TurboPuffer client and create the namespace."""
        # TODO: Implement after turbopuffer installation
        # self.client = TurboPuffer(api_key=TURBOPUFFER_API_KEY)
        # await self.client.create_namespace(self.namespace)
        logger.info("TurboPuffer namespace ready | namespace=%s", self.namespace)

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def format_segment(self, segment: TranscriptSegment) -> str:
        """
        Format a segment for storage and retrieval.

        Returns '[HH:MM:SS] SpeakerRole: text'.
        """
        total_sec = segment.timestamp_us / 1_000_000
        h = int(total_sec // 3600)
        m = int((total_sec % 3600) // 60)
        s = int(total_sec % 60)
        return f"[{h:02d}:{m:02d}:{s:02d}] {segment.speaker_role}: {segment.text}"

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    async def ingest_segment(self, segment: TranscriptSegment) -> bool:
        """
        Ingest a single transcript segment into TurboPuffer.

        Returns True if successful.
        """
        try:
            formatted = self.format_segment(segment)

            # TODO: Implement actual TurboPuffer upsert
            # document = {
            #     "id": f"seg_{segment.timestamp_us}",
            #     "text": formatted,
            #     "speaker_id": segment.speaker_id,
            #     "speaker_role": segment.speaker_role,
            #     "timestamp_us": segment.timestamp_us,
            #     "confidence": segment.confidence,
            # }
            # await self.client.upsert(namespace=self.namespace, documents=[document])

            self.ingested_count += 1
            logger.debug(
                "Ingested segment #%d | speaker=%s confidence=%.2f",
                self.ingested_count,
                segment.speaker_role,
                segment.confidence,
            )
            return True

        except Exception:
            logger.exception("Failed to ingest transcript segment")
            return False

    async def ingest_batch(self, segments: List[TranscriptSegment]) -> int:
        """
        Ingest multiple transcript segments in sequence.

        Returns the number of successfully ingested segments.
        """
        success_count = sum(
            1 for ok in [await self.ingest_segment(s) for s in segments] if ok
        )
        logger.info(
            "Batch ingestion complete | success=%d total=%d",
            success_count,
            len(segments),
        )
        return success_count

    def get_stats(self) -> Dict[str, Any]:
        """Return ingestion statistics."""
        return {
            "session_id": self.session_id,
            "namespace": self.namespace,
            "total_ingested": self.ingested_count,
        }


if __name__ == "__main__":
    from backend.core.logging_config import configure_logging
    configure_logging()

    async def _test() -> None:
        ingestion = TranscriptIngestion(session_id="test-session-001")
        await ingestion.initialize()

        segments = [
            TranscriptSegment(
                text="This court is now in session. Please be seated.",
                speaker_id=0,
                speaker_role=SPEAKER_ROLES[0],
                timestamp_us=get_unified_timestamp_us(),
                confidence=0.95,
            ),
            TranscriptSegment(
                text="Your Honor, the prosecution calls its first witness.",
                speaker_id=2,
                speaker_role=SPEAKER_ROLES[2],
                timestamp_us=get_unified_timestamp_us() + 5_000_000,
                confidence=0.92,
            ),
        ]

        await ingestion.ingest_batch(segments)
        logger.info("Stats: %s", ingestion.get_stats())

    asyncio.run(_test())
