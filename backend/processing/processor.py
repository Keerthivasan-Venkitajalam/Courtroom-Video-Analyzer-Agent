"""
processor.py
Vision Agents video processors for live courtroom streams.
Handles local frame-by-frame analysis (face detection) and the Deepgram
STT diarisation pipeline for real-time memory ingestion.
"""
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import time

# Note: These imports will be available after installing vision-agents
# from vision_agents.plugins import deepgram
# from vision_agents.processor import VideoProcessor
# import ultralytics

from backend.core.logging_config import get_logger
from backend.core.constants import VIDEO_FPS, SPEAKER_ROLES, get_unified_timestamp_us, DEEPGRAM_API_KEY

logger = get_logger(__name__)


@dataclass
class VideoFrame:
    """A single video frame with metadata."""
    timestamp_us: int
    frame_data: bytes
    resolution: Tuple[int, int]
    frame_number: int


@dataclass
class AudioSample:
    """An audio sample with metadata."""
    timestamp_us: int
    sample_data: bytes
    sample_rate: int
    channels: int


class CourtroomProcessor:
    """
    Real-time frame and audio processor for courtroom streams.

    Integrates:
    - YOLOv8n-face for lightweight entity tracking at 5 FPS
    - Deepgram STT with speaker diarisation
    - Temporal consistency checks to prevent belief drift
    """

    # Log frame stats every N frames (at 5 FPS → every 6 seconds)
    LOG_EVERY_N_FRAMES: int = 30

    def __init__(self, fps: int = VIDEO_FPS) -> None:
        """
        Args:
            fps: Frames per second to process (default: VIDEO_FPS = 5).
                 Kept low to conserve compute; heavy semantic indexing is
                 offloaded to Twelve Labs.
        """
        self.fps = fps
        self.current_speaker: str = "Unknown"
        self.frame_count: int = 0
        self.entities_detected: int = 0
        self.previous_entities: List[Dict[str, Any]] = []
        self.speaker_history: List[Tuple[str, int]] = []  # (role, timestamp_us)
        self.model_loaded: bool = False

        # TODO: Initialise after vision-agents installation
        # super().__init__(fps=fps)
        # self.face_model = ultralytics.YOLO("yolov8n-face.pt")
        # self.speaker_diarization = deepgram.STT(
        #     api_key=DEEPGRAM_API_KEY,
        #     diarize=True,
        #     punctuate=True,
        #     model="nova-2",
        # )

        logger.info(
            "CourtroomProcessor initialised | fps=%d entity_detection=YOLOv8n-face(pending) STT=Deepgram(pending)",
            fps,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _map_speaker_id_to_role(self, speaker_id: int) -> str:
        """Map a numeric Deepgram speaker ID to a courtroom role string."""
        return SPEAKER_ROLES.get(speaker_id, f"Speaker_{speaker_id}")

    def _check_temporal_consistency(self, current_entities: List[Dict[str, Any]]) -> bool:
        """
        Guard against belief drift by checking whether the entity count
        changed by more than 50 % across consecutive frames.

        Returns True if consistent, False if a drift event is detected.
        """
        if not self.previous_entities:
            self.previous_entities = current_entities
            return True

        prev_count = len(self.previous_entities)
        curr_count = len(current_entities)

        if prev_count > 0:
            change_ratio = abs(curr_count - prev_count) / prev_count
            if change_ratio > 0.5:
                logger.warning(
                    "Belief drift detected | entity count changed %.1f%%",
                    change_ratio * 100,
                )
                self.previous_entities = current_entities
                return False

        self.previous_entities = current_entities
        return True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def process_audio_chunk(
        self, audio_data: bytes
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Process a real-time audio chunk through Deepgram STT with diarisation.

        Workflow:
        1. Send audio to Deepgram → transcript + numeric speaker ID
        2. Map speaker ID to a courtroom role
        3. Track speaker changes

        Returns:
            (transcript_text, speaker_role) or (None, None) on failure /
            when no speech is detected.
        """
        try:
            timestamp_us = get_unified_timestamp_us()

            # TODO: Implement after deepgram integration
            # transcript_data = await self.speaker_diarization.transcribe(audio_data)
            # if transcript_data and hasattr(transcript_data, "speaker"):
            #     speaker_id = transcript_data.speaker
            #     speaker_role = self._map_speaker_id_to_role(speaker_id)
            #     if speaker_role != self.current_speaker:
            #         logger.info("Speaker changed | %s → %s", self.current_speaker, speaker_role)
            #         self.current_speaker = speaker_role
            #         self.speaker_history.append((speaker_role, timestamp_us))
            #     return transcript_data.text, speaker_role

            return None, None

        except Exception:
            logger.exception("Error processing audio chunk")
            return None, None

    def get_speaker_history(self) -> List[Tuple[str, int]]:
        """Return the history of speaker changes as (role, timestamp_us) pairs."""
        return self.speaker_history

    async def process_frame(
        self, frame: Any, timestamp: float
    ) -> Dict[str, Any]:
        """
        Vision Agents hook called for every incoming video frame.

        Workflow:
        1. Run YOLOv8n-face inference → entity count + bounding boxes
        2. Run temporal consistency check
        3. Emit a state dict consumed by the agent orchestration loop

        Args:
            frame: Video frame (numpy array in production; None in placeholder mode).
            timestamp: Frame timestamp in seconds from stream start.

        Returns:
            State dict: timestamp, entities_visible, inferred_speaker,
                        frame_number, consistent.
        """
        try:
            self.frame_count += 1
            timestamp_us = get_unified_timestamp_us()

            # TODO: Implement after ultralytics integration
            # results = self.face_model(frame)
            # entities = [
            #     {"bbox": box.xyxy.tolist(), "confidence": float(box.conf), "class": int(box.cls)}
            #     for box in results.boxes
            # ]
            # self.entities_detected = len(entities)
            # is_consistent = self._check_temporal_consistency(entities)

            entities: List[Dict[str, Any]] = []
            self.entities_detected = 0
            is_consistent = True

            state: Dict[str, Any] = {
                "timestamp": timestamp_us,
                "entities_visible": self.entities_detected,
                "inferred_speaker": self.current_speaker,
                "frame_number": self.frame_count,
                "consistent": is_consistent,
            }

            if self.frame_count % self.LOG_EVERY_N_FRAMES == 0:
                logger.debug(
                    "Frame %d | entities=%d speaker=%s",
                    self.frame_count,
                    self.entities_detected,
                    self.current_speaker,
                )

            return state

        except Exception:
            logger.exception("Error processing frame %d", self.frame_count)
            return {
                "timestamp": get_unified_timestamp_us(),
                "entities_visible": 0,
                "inferred_speaker": "Unknown",
                "frame_number": self.frame_count,
                "consistent": False,
                "error": "frame_processing_failed",
            }

    def get_stats(self) -> Dict[str, Any]:
        """Return processor statistics for monitoring."""
        return {
            "total_frames": self.frame_count,
            "current_speaker": self.current_speaker,
            "entities_detected": self.entities_detected,
            "fps": self.fps,
            "speaker_changes": len(self.speaker_history),
        }


if __name__ == "__main__":
    from backend.core.logging_config import configure_logging
    configure_logging()

    async def _test() -> None:
        processor = CourtroomProcessor(fps=5)
        for i in range(5):
            result = await processor.process_frame(None, i * 0.2)
            logger.info("Frame %d result: %s", i + 1, result)
            await asyncio.sleep(0.2)
        logger.info("Stats: %s", processor.get_stats())

    asyncio.run(_test())
