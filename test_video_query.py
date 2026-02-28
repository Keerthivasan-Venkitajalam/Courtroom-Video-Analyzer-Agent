"""
test_video_query.py
Test script for video moment querying with Twelve Labs integration.
"""
import asyncio
from index import CourtroomIndexer

async def test_video_queries():
    """Test the video query pipeline with various search queries."""
    print("=" * 60)
    print("VIDEO QUERY TEST")
    print("=" * 60)
    
    # Initialize indexer
    indexer = CourtroomIndexer(
        stream_url="rtsp://localhost:8554/courtcam",
        session_id="test-session-video-query"
    )
    
    # Start indexing
    print("\n📹 Starting live indexing...")
    success = await indexer.start_live_indexing()
    
    if not success:
        print("❌ Failed to start indexing")
        return
    
    print(f"✅ Indexing started with ID: {indexer.scene_index_id}")
    
    # Test queries
    test_queries = [
        "when did the witness testify?",
        "show me when the objection was raised",
        "find moments when evidence was presented",
        "what did the judge say during opening statements?",
        "show me cross-examination of the witness"
    ]
    
    print("\n" + "=" * 60)
    print("RUNNING TEST QUERIES")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Query {i}] {query}")
        print("-" * 60)
        
        # Execute query
        results = await indexer.query_video_moments(query)
        
        if results:
            print(f"✅ Found {len(results)} matching moments:")
            for j, match in enumerate(results, 1):
                print(f"\n  Match {j}:")
                print(f"    Time: {match.start_time:.1f}s - {match.end_time:.1f}s")
                print(f"    Duration: {match.end_time - match.start_time:.1f}s")
                print(f"    Description: {match.description}")
                print(f"    HLS URL: {match.stream_url}")
        else:
            print("  ⚠️  No matching moments found")
        
        # Small delay between queries
        await asyncio.sleep(0.5)
    
    # Test HLS URL generation
    print("\n" + "=" * 60)
    print("HLS URL GENERATION TEST")
    print("=" * 60)
    
    test_segments = [
        (120.5, 185.3),
        (245.2, 258.9),
        (310.4, 345.8)
    ]
    
    for start, end in test_segments:
        hls_url = indexer._generate_hls_url(start, end)
        print(f"  Segment {start:.1f}s - {end:.1f}s")
        print(f"    URL: {hls_url}")
        print(f"    Valid format: {'✅' if '.m3u8' in hls_url else '❌'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"  Total queries tested: {len(test_queries)}")
    print(f"  Index ID: {indexer.scene_index_id}")
    print(f"  Session ID: {indexer.session_id}")
    
    print("\n📝 Note: Full functionality requires:")
    print("  1. VideoDB API key in .env")
    print("  2. Twelve Labs API key in .env")
    print("  3. Active RTSP stream")
    print("  4. Indexed video content")
    
    print("\n✅ Video query pipeline structure validated!")


if __name__ == "__main__":
    asyncio.run(test_video_queries())
