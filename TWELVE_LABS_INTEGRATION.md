# Twelve Labs Pegasus 1.2 Integration Guide

This document explains the Twelve Labs Pegasus 1.2 integration for video intelligence in the Courtroom Video Analyzer Agent.

## Overview

Twelve Labs Pegasus 1.2 is used for:
- Real-time video scene indexing
- Entity detection (judge, witnesses, attorneys, defendants, evidence)
- Visual event recognition (document presentation, gestures, objections)
- Semantic video search

## Integration Architecture

```
RTSP Stream → VideoDB → Twelve Labs Pegasus 1.2 → Scene Index
                                                        ↓
                                                   Searchable
                                                   Video Moments
```

## Implementation

### 1. Indexing Configuration

The indexing is configured in `index.py` with a custom legal domain prompt:

```python
PEGASUS_LEGAL_PROMPT = """Monitor the courtroom proceedings. Identify the judge, witnesses, and counsel. 
Detail legal arguments, objections, and physical evidence presented. 
Focus on: Miranda rights, physical exhibits, cross-examination, opening statements, closing arguments."""
```

### 2. Starting Live Indexing

```python
from index import CourtroomIndexer

# Initialize indexer
indexer = CourtroomIndexer(
    stream_url="rtsp://localhost:8554/courtcam",
    session_id="session-001"
)

# Start indexing
await indexer.start_live_indexing()
```

### 3. Workflow

1. **Connection**: VideoDB connects to RTSP stream
2. **Stream Creation**: Creates live stream object
3. **Index Initialization**: Calls `rt_stream.index_scenes()` with:
   - Custom legal domain prompt
   - Pegasus 1.2 model
   - Temporal scene extraction
4. **Continuous Indexing**: Pegasus processes frames in real-time
5. **Scene Index ID**: Returns unique index ID for queries

## Custom Legal Domain Prompt

The prompt is optimized for courtroom proceedings:

### Key Focus Areas:
- **Participants**: Judge, witnesses, counsel identification
- **Legal Events**: Arguments, objections, evidence presentation
- **Specific Terms**: Miranda rights, physical exhibits, cross-examination
- **Proceedings**: Opening statements, closing arguments

### Why This Matters:
- Improves accuracy for legal-specific queries
- Prioritizes relevant visual events
- Reduces false positives for non-legal content

## Scene Index ID

After indexing starts, you receive a `scene_index_id`:

```python
scene_index_id = "twelvelabs_index_abc123"
```

This ID is used for:
- Querying video moments
- Retrieving specific scenes
- Generating HLS playback URLs

## Querying Video Moments

```python
# Search for specific moments
results = await indexer.query_video_moments(
    "when did the witness present the document?"
)

for match in results:
    print(f"Found at {match.start_time}s - {match.end_time}s")
    print(f"Description: {match.description}")
    print(f"Play: {match.stream_url}")
```

## Performance Characteristics

### Latency Budget
- **Target**: 200ms for video intelligence queries
- **Optimization**: Pre-computed embeddings
- **Caching**: VideoDB indexes frames continuously

### Frame-Level Precision
- **Timestamp Accuracy**: 33ms (30 FPS)
- **Indexing Rate**: Real-time (no buffering)
- **Scene Detection**: Automatic boundary detection

## API Requirements

### Twelve Labs API Key
Get from: https://playground.twelvelabs.io/

Add to `.env`:
```bash
TWELVE_LABS_API_KEY=your_api_key_here
```

### VideoDB API Key
Get from: https://videodb.io/

Add to `.env`:
```bash
VIDEODB_API_KEY=your_api_key_here
```

## Error Handling

### Connection Failures
```python
if not await indexer.start_live_indexing():
    print("Failed to start indexing")
    # Fallback: Use pre-uploaded test video
```

### Query Failures
```python
results = await indexer.query_video_moments(query)
if not results:
    print("No matching video moments found")
    # Return empty result to agent
```

## Testing

### Test with Mock Stream

```bash
# Start RTSP stream
./scripts/start_rtsp_stream.sh mock_trial.mp4

# Run indexer test
python index.py
```

### Verify Indexing

```python
# Check if scene_index_id is generated
assert indexer.scene_index_id is not None
print(f"Index ID: {indexer.scene_index_id}")
```

## Optimization Tips

### 1. Prompt Engineering
- Be specific about what to detect
- Include domain-specific terminology
- Focus on actionable events

### 2. Model Selection
- Use Pegasus 1.2 for best accuracy
- Consider Pegasus 1.0 for faster processing
- Balance accuracy vs. latency

### 3. Scene Extraction
- Temporal extraction for continuous streams
- Shot-based for edited content
- Adjust based on content type

## Troubleshooting

### Issue: Indexing not starting
**Solution**: 
- Verify API keys are valid
- Check RTSP stream is accessible
- Ensure VideoDB connection is established

### Issue: Poor search results
**Solution**:
- Refine the legal domain prompt
- Add more specific keywords
- Test with different query phrasings

### Issue: High latency
**Solution**:
- Use pre-computed embeddings
- Enable VideoDB caching
- Reduce video resolution if needed

## Integration with Agent

The Pegasus index is exposed to the Gemini agent via MCP tools:

```python
@llm.register_function(
    description="Search the live courtroom video for specific semantic moments"
)
async def search_video(query: str) -> str:
    results = await indexer.query_video_moments(query)
    # Format and return results
```

## Next Steps

1. ✅ Configure API keys
2. ✅ Start RTSP stream
3. ✅ Initialize indexer
4. ✅ Verify scene_index_id is generated
5. ⏳ Test with sample queries
6. ⏳ Optimize prompt for your use case
7. ⏳ Integrate with agent orchestration

## References

- [Twelve Labs Documentation](https://docs.twelvelabs.io/)
- [VideoDB Documentation](https://docs.videodb.io/)
- [Pegasus Model Details](https://www.twelvelabs.io/blog/pegasus-1)
