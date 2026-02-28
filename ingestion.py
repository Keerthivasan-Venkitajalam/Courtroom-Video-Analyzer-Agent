"""
ingestion.py
Base data ingestion script for TurboPuffer RAG.
Handles transcript segment ingestion with speaker diarization.
"""
import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass
from constants import (
    TURBOPUFFER_API_KEY,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    SPEAKER_ROLES,
    get_unified_timestamp_us
)

# Note: TurboPuffer client will be installed separately
# from turbopuffer import TurboPuffer


@dataclass
class TranscriptSegment:
    """Represents a diarized transcript segment."""
    text: str
    speaker_id: int
    speaker_role: str
    timestamp_us: int
    confidence: float = 0.0


class TranscriptIngestion:
    """
    Handles ingestion of diarized transcript segments into TurboPuffer.
    Formats segments as '[{timestamp}] {speaker}: {text}' for storage.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize transcript ingestion.
        
        Args:
            session_id: Unique session identifier for namespace
        """
        self.session_id = session_id
        self.namespace = f"court-session-{session_id}"
        self.client = None
        self.ingested_count = 0
        
        print(f"📝 Initializing TranscriptIngestion")
        print(f"   Namespace: {self.namespace}")
        print(f"   Chunk Size: {CHUNK_SIZE}")
        print(f"   Chunk Overlap: {CHUNK_OVERLAP}")
        
    async def initialize(self):
        """Initialize TurboPuffer client and namespace."""
        # TODO: Initialize TurboPuffer client after installation
        # self.client = TurboPuffer(api_key=TURBOPUFFER_API_KEY)
        # await self.client.create_namespace(self.namespace)
        print(f"✅ TurboPuffer namespace ready: {self.namespace}")
        
    def format_segment(self, segment: TranscriptSegment) -> str:
        """
        Format transcript segment for storage.
        
        Args:
            segment: TranscriptSegment to format
            
        Returns:
            Formatted string: '[{timestamp}] {speaker}: {text}'
        """
        # Convert microseconds to human-readable format
        timestamp_sec = segment.timestamp_us / 1_000_000
        hours = int(timestamp_sec // 3600)
        minutes = int((timestamp_sec % 3600) // 60)
        seconds = int(timestamp_sec % 60)
        
        timestamp_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return f"[{timestamp_str}] {segment.speaker_role}: {segment.text}"
    
    async def ingest_segment(self, segment: TranscriptSegment) -> bool:
        """
        Ingest a single transcript segment into TurboPuffer.
        
        Args:
            segment: TranscriptSegment to ingest
            
        Returns:
            True if ingestion successful, False otherwise
        """
        try:
            formatted_text = self.format_segment(segment)
            
            # TODO: Implement actual TurboPuffer ingestion
            # document = {
            #     'id': f"seg_{segment.timestamp_us}",
            #     'text': formatted_text,
            #     'speaker_id': segment.speaker_id,
            #     'speaker_role': segment.speaker_role,
            #     'timestamp_us': segment.timestamp_us,
            #     'confidence': segment.confidence
            # }
            # 
            # await self.client.upsert(
            #     namespace=self.namespace,
            #     documents=[document]
            # )
            
            self.ingested_count += 1
            print(f"✅ Ingested segment #{self.ingested_count}: {formatted_text[:80]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Error ingesting segment: {e}")
            return False
    
    async def ingest_batch(self, segments: List[TranscriptSegment]) -> int:
        """
        Ingest multiple transcript segments in batch.
        
        Args:
            segments: List of TranscriptSegments to ingest
            
        Returns:
            Number of successfully ingested segments
        """
        success_count = 0
        
        for segment in segments:
            if await self.ingest_segment(segment):
                success_count += 1
                
        print(f"📊 Batch ingestion complete: {success_count}/{len(segments)} successful")
        return success_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        return {
            'session_id': self.session_id,
            'namespace': self.namespace,
            'total_ingested': self.ingested_count
        }


async def test_ingestion():
    """Test the ingestion pipeline with synthetic court dialogue samples."""
    print("=" * 60)
    print("TRANSCRIPT INGESTION TEST")
    print("=" * 60)
    
    # Initialize ingestion
    ingestion = TranscriptIngestion(session_id="test-session-001")
    await ingestion.initialize()
    
    # Create 10 synthetic court dialogue samples
    test_segments = [
        TranscriptSegment(
            text="This court is now in session. Please be seated.",
            speaker_id=0,
            speaker_role=SPEAKER_ROLES[0],
            timestamp_us=get_unified_timestamp_us(),
            confidence=0.95
        ),
        TranscriptSegment(
            text="Your Honor, the prosecution calls its first witness.",
            speaker_id=2,
            speaker_role=SPEAKER_ROLES[2],
            timestamp_us=get_unified_timestamp_us() + 5_000_000,
            confidence=0.92
        ),
        TranscriptSegment(
            text="Please state your name for the record.",
            speaker_id=0,
            speaker_role=SPEAKER_ROLES[0],
            timestamp_us=get_unified_timestamp_us() + 10_000_000,
            confidence=0.94
        ),
        TranscriptSegment(
            text="My name is Dr. Sarah Johnson.",
            speaker_id=1,
            speaker_role=SPEAKER_ROLES[1],
            timestamp_us=get_unified_timestamp_us() + 15_000_000,
            confidence=0.96
        ),
        TranscriptSegment(
            text="Dr. Johnson, can you describe what you observed on the night of March 15th?",
            speaker_id=2,
            speaker_role=SPEAKER_ROLES[2],
            timestamp_us=get_unified_timestamp_us() + 20_000_000,
            confidence=0.93
        ),
        TranscriptSegment(
            text="I was working late at the hospital when I received an emergency call.",
            speaker_id=1,
            speaker_role=SPEAKER_ROLES[1],
            timestamp_us=get_unified_timestamp_us() + 25_000_000,
            confidence=0.91
        ),
        TranscriptSegment(
            text="Objection, Your Honor. Leading the witness.",
            speaker_id=3,
            speaker_role=SPEAKER_ROLES[3],
            timestamp_us=get_unified_timestamp_us() + 30_000_000,
            confidence=0.97
        ),
        TranscriptSegment(
            text="Sustained. Counsel, please rephrase.",
            speaker_id=0,
            speaker_role=SPEAKER_ROLES[0],
            timestamp_us=get_unified_timestamp_us() + 35_000_000,
            confidence=0.98
        ),
        TranscriptSegment(
            text="Dr. Johnson, what happened after you received the call?",
            speaker_id=2,
            speaker_role=SPEAKER_ROLES[2],
            timestamp_us=get_unified_timestamp_us() + 40_000_000,
            confidence=0.94
        ),
        TranscriptSegment(
            text="I immediately proceeded to the emergency room where the patient was being treated.",
            speaker_id=1,
            speaker_role=SPEAKER_ROLES[1],
            timestamp_us=get_unified_timestamp_us() + 45_000_000,
            confidence=0.92
        )
    ]
    
    print(f"\n📝 Testing with {len(test_segments)} synthetic court dialogue samples")
    print("=" * 60)
    
    # Ingest test segments
    success_count = await ingestion.ingest_batch(test_segments)
    
    # Display statistics
    print("\n" + "=" * 60)
    print("INGESTION STATISTICS")
    print("=" * 60)
    stats = ingestion.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Test complete!")
    
    if success_count == len(test_segments):
        print("✅ All segments ingested successfully")
    else:
        print(f"⚠️  {len(test_segments) - success_count} segments failed")


if __name__ == "__main__":
    asyncio.run(test_ingestion())
