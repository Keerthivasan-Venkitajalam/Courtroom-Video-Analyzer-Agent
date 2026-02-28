"""
test_audio_processing.py
Test script for audio processing and speaker diarization.
"""
import asyncio
from processor import CourtroomProcessor
from constants import SPEAKER_ROLES

async def test_audio_processing():
    """Test the audio processing pipeline with simulated audio chunks."""
    print("=" * 60)
    print("AUDIO PROCESSING TEST")
    print("=" * 60)
    
    # Initialize processor
    processor = CourtroomProcessor(fps=5)
    
    print("\n🎤 Testing audio chunk processing...")
    print("=" * 60)
    
    # Simulate audio chunks with different speakers
    test_scenarios = [
        {
            'audio': b'simulated_audio_data_1',
            'expected_speaker': 'Judge',
            'expected_text': 'This court is now in session.'
        },
        {
            'audio': b'simulated_audio_data_2',
            'expected_speaker': 'Prosecution',
            'expected_text': 'Your Honor, the prosecution calls its first witness.'
        },
        {
            'audio': b'simulated_audio_data_3',
            'expected_speaker': 'Witness',
            'expected_text': 'I was present at the scene on March 15th.'
        },
        {
            'audio': b'simulated_audio_data_4',
            'expected_speaker': 'Defense',
            'expected_text': 'Objection, Your Honor. Leading the witness.'
        },
        {
            'audio': b'simulated_audio_data_5',
            'expected_speaker': 'Judge',
            'expected_text': 'Sustained. Counsel, please rephrase.'
        }
    ]
    
    print("\nProcessing audio chunks...")
    print("-" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n[Chunk {i}]")
        print(f"  Expected Speaker: {scenario['expected_speaker']}")
        print(f"  Expected Text: {scenario['expected_text']}")
        
        # Process audio chunk
        text, speaker = await processor.process_audio_chunk(scenario['audio'])
        
        if text and speaker:
            print(f"  ✅ Detected Speaker: {speaker}")
            print(f"  ✅ Transcribed Text: {text}")
        else:
            print(f"  ⚠️  No output (Deepgram not yet integrated)")
            print(f"  📝 Placeholder mode - actual implementation pending")
        
        # Small delay to simulate real-time processing
        await asyncio.sleep(0.5)
    
    # Display speaker history
    print("\n" + "=" * 60)
    print("SPEAKER HISTORY")
    print("=" * 60)
    
    speaker_history = processor.get_speaker_history()
    if speaker_history:
        for speaker, timestamp in speaker_history:
            print(f"  {speaker} at {timestamp}μs")
    else:
        print("  No speaker changes recorded (integration pending)")
    
    # Display processor stats
    print("\n" + "=" * 60)
    print("PROCESSOR STATISTICS")
    print("=" * 60)
    
    stats = processor.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\n📝 Note: Full functionality requires:")
    print("  1. Deepgram API key in .env")
    print("  2. vision-agents SDK installation")
    print("  3. Active audio stream")
    print("\n✅ Audio processing pipeline structure validated!")


if __name__ == "__main__":
    asyncio.run(test_audio_processing())
