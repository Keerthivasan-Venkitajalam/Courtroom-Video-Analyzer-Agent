"""
test_timestamp_alignment.py
Verify timestamp alignment between video clips and transcript moments.
Tests that both TurboPuffer text result AND VideoDB video clip return the same moment.
"""
import asyncio
from index import CourtroomIndexer
from timestamp_sync import TimestampSynchronizer


async def test_timestamp_alignment():
    """
    Test timestamp alignment across video and transcript.
    
    Scenario: User queries 'what was said at 4:15 PM'
    Expected: Both TurboPuffer text result AND VideoDB video clip return same moment
    """
    print("=" * 60)
    print("TIMESTAMP ALIGNMENT VERIFICATION TEST")
    print("=" * 60)
    
    # Initialize indexer with timestamp sync
    indexer = CourtroomIndexer(
        stream_url="rtsp://localhost:8554/courtcam",
        session_id="timestamp-alignment-test"
    )
    
    await indexer.start_live_indexing()
    
    # Test scenario: Query for specific time
    test_time_seconds = 255.0  # 4:15 into the session
    test_time_us = int(test_time_seconds * 1_000_000)
    
    print(f"\n📍 Test Query: 'What was said at {test_time_seconds / 60:.0f}:{test_time_seconds % 60:.0f}?'")
    print(f"   Target timestamp: {test_time_us}μs ({test_time_seconds}s)")
    
    # Step 1: Add transcript chunk at specific time
    print("\n[Step 1] Adding transcript chunk at target time...")
    await indexer.add_transcript_chunk(
        text="The defendant was wearing a blue jacket that evening.",
        speaker="Witness",
        timestamp=test_time_seconds
    )
    
    # Step 2: Query transcript for that moment
    print("\n[Step 2] Querying transcript...")
    transcript_results = await indexer.query_transcript("blue jacket", top_k=1)
    
    if transcript_results:
        result = transcript_results[0]
        transcript_time_us = result['timestamp_us']
        transcript_time_s = transcript_time_us / 1_000_000
        
        print(f"✅ Found transcript result:")
        print(f"   Text: {result['text']}")
        print(f"   Speaker: {result['speaker']}")
        print(f"   Timestamp: {transcript_time_us}μs ({transcript_time_s:.2f}s)")
    else:
        print("❌ No transcript results found")
        transcript_time_us = None
    
    # Step 3: Query video for that moment
    print("\n[Step 3] Querying video...")
    video_results = await indexer.query_video_moments("witness testimony about blue jacket")
    
    if video_results:
        result = video_results[0]
        video_start_us = int(result.start_time * 1_000_000)
        video_end_us = int(result.end_time * 1_000_000)
        
        print(f"✅ Found video result:")
        print(f"   Description: {result.description}")
        print(f"   Start: {video_start_us}μs ({result.start_time:.2f}s)")
        print(f"   End: {video_end_us}μs ({result.end_time:.2f}s)")
        print(f"   HLS URL: {result.stream_url}")
    else:
        print("❌ No video results found")
        video_start_us = None
        video_end_us = None
    
    # Step 4: Verify alignment
    print("\n" + "=" * 60)
    print("ALIGNMENT VERIFICATION")
    print("=" * 60)
    
    if transcript_time_us and video_start_us:
        # Check if transcript timestamp falls within video clip range
        is_aligned = video_start_us <= transcript_time_us <= video_end_us
        
        # Calculate discrepancy
        if is_aligned:
            discrepancy_us = 0
        else:
            # Distance to nearest boundary
            discrepancy_us = min(
                abs(transcript_time_us - video_start_us),
                abs(transcript_time_us - video_end_us)
            )
        
        discrepancy_ms = discrepancy_us / 1000
        
        print(f"\n📊 Alignment Analysis:")
        print(f"   Target time: {test_time_us}μs")
        print(f"   Transcript time: {transcript_time_us}μs")
        print(f"   Video range: {video_start_us}μs - {video_end_us}μs")
        print(f"   Discrepancy: {discrepancy_ms:.2f}ms")
        print(f"   Threshold: ±100ms")
        
        if discrepancy_ms <= 100:
            print(f"\n✅ ALIGNMENT VERIFIED: Discrepancy within ±100ms threshold")
            alignment_status = "PASS"
        else:
            print(f"\n❌ ALIGNMENT FAILED: Discrepancy exceeds ±100ms threshold")
            alignment_status = "FAIL"
    else:
        print("\n⚠️  Cannot verify alignment: Missing results")
        alignment_status = "INCOMPLETE"
    
    # Step 5: Test with multiple timestamps
    print("\n" + "=" * 60)
    print("MULTIPLE TIMESTAMP ALIGNMENT TEST")
    print("=" * 60)
    
    test_cases = [
        (135.0, "Judge", "This court is now in session"),
        (318.0, "Witness", "I was present at the scene"),
        (465.0, "Defense", "Objection, Your Honor"),
        (630.0, "Witness", "The defendant was wearing a blue jacket")
    ]
    
    alignment_results = []
    
    for timestamp_s, speaker, text in test_cases:
        print(f"\n[Test] {timestamp_s}s - {speaker}: {text[:40]}...")
        
        # Add transcript
        await indexer.add_transcript_chunk(text, speaker, timestamp_s)
        
        # Query both
        transcript_results = await indexer.query_transcript(text.split()[0], top_k=1)
        video_results = await indexer.query_video_moments(f"{speaker} {text.split()[0]}")
        
        if transcript_results and video_results:
            t_time = transcript_results[0]['timestamp_us']
            v_start = int(video_results[0].start_time * 1_000_000)
            v_end = int(video_results[0].end_time * 1_000_000)
            
            aligned = v_start <= t_time <= v_end
            discrepancy = 0 if aligned else min(abs(t_time - v_start), abs(t_time - v_end))
            
            alignment_results.append({
                'timestamp': timestamp_s,
                'aligned': aligned,
                'discrepancy_ms': discrepancy / 1000
            })
            
            status = "✅" if discrepancy / 1000 <= 100 else "❌"
            print(f"  {status} Discrepancy: {discrepancy / 1000:.2f}ms")
        else:
            print(f"  ⚠️  Incomplete results")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if alignment_results:
        aligned_count = sum(1 for r in alignment_results if r['discrepancy_ms'] <= 100)
        total_count = len(alignment_results)
        avg_discrepancy = sum(r['discrepancy_ms'] for r in alignment_results) / total_count
        
        print(f"\n📊 Results:")
        print(f"   Total tests: {total_count}")
        print(f"   Aligned (≤100ms): {aligned_count}")
        print(f"   Failed (>100ms): {total_count - aligned_count}")
        print(f"   Average discrepancy: {avg_discrepancy:.2f}ms")
        print(f"   Success rate: {aligned_count / total_count * 100:.1f}%")
        
        if aligned_count == total_count:
            print(f"\n✅ ALL TESTS PASSED: Timestamp alignment verified!")
        else:
            print(f"\n⚠️  SOME TESTS FAILED: Review timestamp synchronization")
    
    # Test synchronizer status
    print("\n" + "=" * 60)
    print("SYNCHRONIZER STATUS")
    print("=" * 60)
    
    sync_status = indexer.timestamp_sync.get_sync_status()
    print(f"\nUnified time: {sync_status['unified_time_us']}μs")
    print(f"\nComponent offsets:")
    for component, info in sync_status['components'].items():
        print(f"  {component}:")
        print(f"    Offset: {info['offset_ms']:.2f}ms")
        print(f"    Last sync: {info['last_sync_ago_s']:.2f}s ago")
    
    # Validate consistency
    consistency = indexer.timestamp_sync.validate_consistency()
    print(f"\nConsistency check:")
    print(f"  Max discrepancy: {consistency['max_discrepancy_ms']:.2f}ms")
    print(f"  Status: {'✅ Consistent' if consistency['is_consistent'] else '❌ Inconsistent'}")
    
    print("\n✅ Timestamp alignment verification complete!")


if __name__ == "__main__":
    asyncio.run(test_timestamp_alignment())
