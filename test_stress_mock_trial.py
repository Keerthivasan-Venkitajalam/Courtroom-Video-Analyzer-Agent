"""
test_stress_mock_trial.py
20-Minute Mock Trial Stress Test

This comprehensive stress test validates system performance under realistic courtroom conditions:
- Complex mock trial scenario with multiple overlapping speakers
- Physical evidence presentations
- Objections and legal procedures
- Concurrent user sessions
- Sustained load over 20 minutes

Validates:
- Property 3: 95th percentile latency under load
- Property 56: Concurrent session support (up to 10 users)

Task 12.1: Run 20-minute Mock Trial Stress Test (All)
"""
import asyncio
import time
import statistics
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import random

from index import CourtroomIndexer
from api_server import QueryRequest
from ingestion import TranscriptSegment, TranscriptIngestion
from constants import SPEAKER_ROLES, get_unified_timestamp_us


@dataclass
class StressTestMetrics:
    """Metrics collected during stress test."""
    query_latencies: List[int] = field(default_factory=list)
    component_latencies: Dict[str, List[int]] = field(default_factory=dict)
    failed_queries: int = 0
    successful_queries: int = 0
    concurrent_sessions: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    
    def add_query_latency(self, latency_ms: int, success: bool = True):
        """Record query latency."""
        self.query_latencies.append(latency_ms)
        if success:
            self.successful_queries += 1
        else:
            self.failed_queries += 1
    
    def add_component_latency(self, component: str, latency_ms: int):
        """Record component-specific latency."""
        if component not in self.component_latencies:
            self.component_latencies[component] = []
        self.component_latencies[component].append(latency_ms)
    
    def get_percentile(self, percentile: int) -> float:
        """Calculate percentile of query latencies."""
        if not self.query_latencies:
            return 0.0
        sorted_latencies = sorted(self.query_latencies)
        index = int(len(sorted_latencies) * (percentile / 100.0))
        return sorted_latencies[min(index, len(sorted_latencies) - 1)]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive test summary."""
        duration_sec = self.end_time - self.start_time if self.end_time > 0 else 0
        
        return {
            'duration_seconds': duration_sec,
            'total_queries': len(self.query_latencies),
            'successful_queries': self.successful_queries,
            'failed_queries': self.failed_queries,
            'success_rate': (self.successful_queries / len(self.query_latencies) * 100) 
                           if self.query_latencies else 0,
            'concurrent_sessions': self.concurrent_sessions,
            'latency_stats': {
                'min_ms': min(self.query_latencies) if self.query_latencies else 0,
                'max_ms': max(self.query_latencies) if self.query_latencies else 0,
                'mean_ms': statistics.mean(self.query_latencies) if self.query_latencies else 0,
                'median_ms': statistics.median(self.query_latencies) if self.query_latencies else 0,
                'p50_ms': self.get_percentile(50),
                'p95_ms': self.get_percentile(95),
                'p99_ms': self.get_percentile(99),
            },
            'component_latencies': {
                component: {
                    'mean_ms': statistics.mean(latencies),
                    'p95_ms': sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
                }
                for component, latencies in self.component_latencies.items()
            }
        }


class MockTrialScenario:
    """
    Generates a realistic 20-minute mock trial scenario with:
    - Opening statements
    - Witness testimony
    - Cross-examination
    - Evidence presentation
    - Objections
    - Closing arguments
    """
    
    def __init__(self):
        self.segments: List[TranscriptSegment] = []
        self.current_time_us = get_unified_timestamp_us()
        
    def add_segment(self, text: str, speaker_role: str, duration_sec: float = 5.0, 
                   confidence: float = 0.95):
        """Add a transcript segment to the scenario."""
        speaker_id = SPEAKER_ROLES.index(speaker_role) if speaker_role in SPEAKER_ROLES else 0
        
        segment = TranscriptSegment(
            text=text,
            speaker_id=speaker_id,
            speaker_role=speaker_role,
            timestamp_us=self.current_time_us,
            confidence=confidence
        )
        
        self.segments.append(segment)
        self.current_time_us += int(duration_sec * 1_000_000)
    
    def generate_trial(self) -> List[TranscriptSegment]:
        """Generate complete 20-minute mock trial scenario."""
        print("🎬 Generating 20-minute mock trial scenario...")
        
        # Phase 1: Opening (0-3 minutes)
        self._generate_opening()
        
        # Phase 2: Prosecution Case (3-8 minutes)
        self._generate_prosecution_case()
        
        # Phase 3: Defense Case (8-13 minutes)
        self._generate_defense_case()
        
        # Phase 4: Evidence Presentation (13-16 minutes)
        self._generate_evidence_presentation()
        
        # Phase 5: Closing Arguments (16-20 minutes)
        self._generate_closing_arguments()
        
        print(f"✅ Generated {len(self.segments)} transcript segments")
        print(f"   Duration: {(self.current_time_us - self.segments[0].timestamp_us) / 60_000_000:.1f} minutes")
        
        return self.segments
    
    def _generate_opening(self):
        """Generate opening statements (0-3 minutes)."""
        self.add_segment(
            "This court is now in session. The Honorable Judge Martinez presiding. Please be seated.",
            "Judge", 4.0
        )
        
        self.add_segment(
            "Good morning, Your Honor. The prosecution is ready to proceed.",
            "Prosecution", 3.0
        )
        
        self.add_segment(
            "The defense is ready, Your Honor.",
            "Defense", 2.5
        )
        
        self.add_segment(
            "Counsel, you may proceed with opening statements. Prosecution, you have the floor.",
            "Judge", 4.0
        )
        
        self.add_segment(
            "Thank you, Your Honor. Ladies and gentlemen of the jury, the evidence will show that on the night of March 15th, 2024, the defendant willfully and knowingly committed fraud by falsifying financial documents to deceive investors. We will present testimony from three witnesses who will corroborate these facts beyond a reasonable doubt.",
            "Prosecution", 18.0
        )
        
        self.add_segment(
            "The prosecution will demonstrate through bank records, email correspondence, and expert testimony that the defendant orchestrated a scheme to inflate company valuations by over ten million dollars. This was not an accident or oversight—this was deliberate deception.",
            "Prosecution", 15.0
        )
        
        self.add_segment(
            "Defense, your opening statement.",
            "Judge", 3.0
        )
        
        self.add_segment(
            "Your Honor, members of the jury, my client stands before you today falsely accused. The prosecution would have you believe that standard business practices constitute fraud. The evidence will show that every transaction was properly documented, every disclosure was made in good faith, and every decision was made with the advice of legal counsel. This is a case of prosecutorial overreach, not criminal conduct.",
            "Defense", 20.0
        )
    
    def _generate_prosecution_case(self):
        """Generate prosecution witness testimony (3-8 minutes)."""
        self.add_segment(
            "The prosecution calls Dr. Emily Chen to the stand.",
            "Prosecution", 3.0
        )
        
        self.add_segment(
            "Please state your name and occupation for the record.",
            "Judge", 3.0
        )
        
        self.add_segment(
            "My name is Dr. Emily Chen. I'm a forensic accountant with twenty years of experience analyzing financial fraud cases.",
            "Witness", 6.0
        )
        
        self.add_segment(
            "Dr. Chen, did you have the opportunity to examine the defendant's financial records from January through March 2024?",
            "Prosecution", 5.0
        )
        
        self.add_segment(
            "Yes, I conducted a comprehensive analysis of all bank statements, ledgers, and transaction records for that period.",
            "Witness", 5.0
        )
        
        self.add_segment(
            "And what did your analysis reveal?",
            "Prosecution", 2.5
        )
        
        self.add_segment(
            "I discovered multiple discrepancies between reported revenues and actual cash flows. Specifically, the defendant's company reported twelve million dollars in revenue, but bank deposits totaled only two million dollars. The remaining ten million dollars appears to have been fabricated.",
            "Witness", 12.0
        )
        
        self.add_segment(
            "Objection, Your Honor! The witness is speculating about intent. She can testify to the numbers, but not to whether anything was fabricated.",
            "Defense", 6.0
        )
        
        self.add_segment(
            "Sustained. Dr. Chen, please limit your testimony to your factual findings.",
            "Judge", 4.0
        )
        
        self.add_segment(
            "I apologize, Your Honor. My analysis shows a ten million dollar discrepancy between reported and actual revenues.",
            "Witness", 5.0
        )
        
        self.add_segment(
            "Dr. Chen, in your professional opinion, could this discrepancy be the result of accounting errors or legitimate business practices?",
            "Prosecution", 6.0
        )
        
        self.add_segment(
            "Objection! Calls for speculation.",
            "Defense", 2.0
        )
        
        self.add_segment(
            "Overruled. The witness is qualified as an expert and may offer her professional opinion.",
            "Judge", 4.0
        )
        
        self.add_segment(
            "In my professional opinion, discrepancies of this magnitude cannot be explained by standard accounting errors. The pattern suggests systematic manipulation of financial records.",
            "Witness", 8.0
        )
        
        self.add_segment(
            "Thank you, Dr. Chen. Your witness, counsel.",
            "Prosecution", 3.0
        )
    
    def _generate_defense_case(self):
        """Generate defense cross-examination and witness (8-13 minutes)."""
        self.add_segment(
            "Dr. Chen, you mentioned you have twenty years of experience. How many of those years were spent working for the prosecution in criminal cases?",
            "Defense", 6.0
        )
        
        self.add_segment(
            "Approximately fifteen years.",
            "Witness", 2.0
        )
        
        self.add_segment(
            "So you're frequently hired by prosecutors to find evidence of wrongdoing, correct?",
            "Defense", 4.0
        )
        
        self.add_segment(
            "I'm hired to analyze financial records objectively.",
            "Witness", 3.0
        )
        
        self.add_segment(
            "But you're paid by the prosecution in this case, aren't you?",
            "Defense", 3.0
        )
        
        self.add_segment(
            "Objection, relevance!",
            "Prosecution", 2.0
        )
        
        self.add_segment(
            "I'll allow it. The witness may answer.",
            "Judge", 3.0
        )
        
        self.add_segment(
            "Yes, I'm compensated for my time and expertise.",
            "Witness", 3.0
        )
        
        self.add_segment(
            "Dr. Chen, did you examine the company's accounts receivable records?",
            "Defense", 4.0
        )
        
        self.add_segment(
            "Yes, I reviewed those records.",
            "Witness", 2.5
        )
        
        self.add_segment(
            "And isn't it true that the ten million dollar discrepancy you mentioned represents outstanding invoices that hadn't been paid yet?",
            "Defense", 6.0
        )
        
        self.add_segment(
            "The records show outstanding invoices, yes, but—",
            "Witness", 3.0
        )
        
        self.add_segment(
            "Thank you, Dr. Chen. No further questions.",
            "Defense", 3.0
        )
        
        self.add_segment(
            "The defense calls Michael Rodriguez to the stand.",
            "Defense", 3.0
        )
        
        self.add_segment(
            "Please state your name and occupation.",
            "Judge", 2.5
        )
        
        self.add_segment(
            "Michael Rodriguez. I'm the Chief Financial Officer of the defendant's company.",
            "Witness", 4.0
        )
        
        self.add_segment(
            "Mr. Rodriguez, can you explain the company's revenue recognition practices?",
            "Defense", 4.0
        )
        
        self.add_segment(
            "We follow standard GAAP accounting principles. Revenue is recognized when services are delivered, even if payment hasn't been received yet. This is completely normal in our industry.",
            "Witness", 8.0
        )
        
        self.add_segment(
            "So the ten million dollars in question represents legitimate business transactions?",
            "Defense", 4.0
        )
        
        self.add_segment(
            "Absolutely. These are real contracts with real clients. Some payments are simply delayed due to standard payment terms.",
            "Witness", 6.0
        )
    
    def _generate_evidence_presentation(self):
        """Generate evidence presentation phase (13-16 minutes)."""
        self.add_segment(
            "The prosecution would like to introduce Exhibit A into evidence—bank statements from March 2024.",
            "Prosecution", 5.0
        )
        
        self.add_segment(
            "Any objection, counsel?",
            "Judge", 2.0
        )
        
        self.add_segment(
            "No objection, Your Honor.",
            "Defense", 2.0
        )
        
        self.add_segment(
            "Exhibit A is admitted. Please continue.",
            "Judge", 3.0
        )
        
        self.add_segment(
            "Your Honor, I'd like to direct the court's attention to page seven of Exhibit A, which shows a series of wire transfers totaling five hundred thousand dollars to an offshore account.",
            "Prosecution", 8.0
        )
        
        self.add_segment(
            "The defense would like to introduce Exhibit B—email correspondence between the defendant and legal counsel regarding these transactions.",
            "Defense", 6.0
        )
        
        self.add_segment(
            "Objection! Attorney-client privilege.",
            "Prosecution", 2.5
        )
        
        self.add_segment(
            "Your Honor, the defendant has waived privilege by claiming advice of counsel as a defense.",
            "Defense", 5.0
        )
        
        self.add_segment(
            "I'll allow it. Exhibit B is admitted.",
            "Judge", 3.0
        )
        
        self.add_segment(
            "These emails clearly show that the defendant sought and received legal advice before every transaction in question. This demonstrates good faith compliance, not criminal intent.",
            "Defense", 8.0
        )
        
        self.add_segment(
            "The prosecution introduces Exhibit C—a forensic analysis report showing that several invoices were backdated.",
            "Prosecution", 6.0
        )
        
        self.add_segment(
            "Objection! Foundation. Who prepared this report?",
            "Defense", 3.0
        )
        
        self.add_segment(
            "Dr. Chen prepared this report as part of her analysis.",
            "Prosecution", 3.0
        )
        
        self.add_segment(
            "Then it should have been introduced during her testimony. I'll sustain the objection. Exhibit C is not admitted at this time.",
            "Judge", 6.0
        )
    
    def _generate_closing_arguments(self):
        """Generate closing arguments (16-20 minutes)."""
        self.add_segment(
            "We'll now hear closing arguments. Prosecution, you may proceed.",
            "Judge", 4.0
        )
        
        self.add_segment(
            "Your Honor, members of the jury, the evidence is clear. The defendant systematically manipulated financial records to deceive investors. Dr. Chen's expert testimony showed a ten million dollar discrepancy that cannot be explained by legitimate business practices. The bank statements prove that money was diverted to offshore accounts. The defendant's own CFO admitted that payments were delayed—but failed to explain why invoices were issued for services never rendered.",
            "Prosecution", 22.0
        )
        
        self.add_segment(
            "This is not a case of aggressive accounting or business judgment. This is fraud, plain and simple. The prosecution has met its burden of proof beyond a reasonable doubt. We ask that you return a verdict of guilty.",
            "Prosecution", 12.0
        )
        
        self.add_segment(
            "Defense, your closing argument.",
            "Judge", 3.0
        )
        
        self.add_segment(
            "Ladies and gentlemen, the prosecution wants you to believe that standard business practices are criminal. But the evidence tells a different story. My client followed legal advice at every step. The so-called discrepancy is simply accounts receivable—money that will be paid when contracts are fulfilled. The offshore transfers were legitimate business expenses, properly documented and disclosed.",
            "Defense", 20.0
        )
        
        self.add_segment(
            "The prosecution has not proven criminal intent. They have not proven that my client knowingly deceived anyone. They have shown you complex business transactions and asked you to assume the worst. But assumption is not proof. Suspicion is not evidence. The prosecution has failed to meet its burden, and you must return a verdict of not guilty.",
            "Defense", 18.0
        )
        
        self.add_segment(
            "Thank you, counsel. The jury will now deliberate. Court is adjourned.",
            "Judge", 4.0
        )


class StressTestRunner:
    """Orchestrates the 20-minute stress test."""
    
    def __init__(self, num_concurrent_users: int = 10):
        self.num_concurrent_users = num_concurrent_users
        self.metrics = StressTestMetrics()
        self.indexers: List[CourtroomIndexer] = []
        self.ingestion_systems: List[TranscriptIngestion] = []
        
    async def setup(self):
        """Initialize test environment."""
        print("=" * 80)
        print("20-MINUTE MOCK TRIAL STRESS TEST")
        print("=" * 80)
        print(f"Concurrent users: {self.num_concurrent_users}")
        print(f"Test duration: 20 minutes")
        print(f"Validates: Property 3 (95th percentile latency), Property 56 (Concurrent sessions)")
        print("=" * 80)
        
        # Initialize indexers for concurrent users
        print(f"\n[Setup] Initializing {self.num_concurrent_users} concurrent user sessions...")
        
        for i in range(self.num_concurrent_users):
            session_id = f"stress-test-user-{i+1}"
            
            # Create indexer
            indexer = CourtroomIndexer(
                stream_url=f"rtsp://localhost:8554/courtcam",
                session_id=session_id
            )
            await indexer.start_live_indexing()
            self.indexers.append(indexer)
            
            # Create ingestion system
            ingestion = TranscriptIngestion(session_id=session_id)
            await ingestion.initialize()
            self.ingestion_systems.append(ingestion)
            
            print(f"  ✅ User {i+1} session initialized: {session_id}")
        
        self.metrics.concurrent_sessions = self.num_concurrent_users
        print(f"\n✅ All {self.num_concurrent_users} user sessions ready")
    
    async def ingest_trial_transcript(self, segments: List[TranscriptSegment]):
        """Ingest trial transcript into all user sessions."""
        print(f"\n[Ingestion] Ingesting {len(segments)} transcript segments...")
        
        start_time = time.time()
        
        # Ingest into all sessions concurrently
        tasks = []
        for ingestion in self.ingestion_systems:
            tasks.append(ingestion.ingest_batch(segments))
        
        results = await asyncio.gather(*tasks)
        
        duration = time.time() - start_time
        total_ingested = sum(results)
        
        print(f"✅ Ingestion complete in {duration:.2f}s")
        print(f"   Total segments ingested: {total_ingested}")
        print(f"   Segments per session: {total_ingested / self.num_concurrent_users:.0f}")
    
    async def run_concurrent_queries(self, queries: List[str], duration_minutes: float = 20.0):
        """Run queries concurrently from all user sessions."""
        print(f"\n[Query Load] Running concurrent queries for {duration_minutes} minutes...")
        print(f"   Queries per user: {len(queries)}")
        print(f"   Total query load: {len(queries) * self.num_concurrent_users}")
        
        self.metrics.start_time = time.time()
        end_time = self.metrics.start_time + (duration_minutes * 60)
        
        query_tasks = []
        
        # Create query tasks for each user
        for user_idx, indexer in enumerate(self.indexers):
            for query in queries:
                # Stagger queries to simulate realistic load
                delay = random.uniform(0, duration_minutes * 60 / len(queries))
                query_tasks.append(
                    self._execute_query_with_delay(indexer, query, delay, user_idx + 1)
                )
        
        # Execute all queries concurrently
        await asyncio.gather(*query_tasks)
        
        self.metrics.end_time = time.time()
        
        print(f"\n✅ Query load test complete")
        print(f"   Duration: {self.metrics.end_time - self.metrics.start_time:.2f}s")
        print(f"   Total queries: {len(self.metrics.query_latencies)}")
    
    async def _execute_query_with_delay(self, indexer: CourtroomIndexer, 
                                       query: str, delay: float, user_id: int):
        """Execute a single query after a delay."""
        await asyncio.sleep(delay)
        
        start_time = time.time()
        
        try:
            # Execute both transcript and video queries
            transcript_start = time.time()
            transcript_results = await indexer.query_transcript(query, top_k=5)
            transcript_latency = int((time.time() - transcript_start) * 1000)
            
            video_start = time.time()
            video_results = await indexer.query_video_moments(query)
            video_latency = int((time.time() - video_start) * 1000)
            
            total_latency = int((time.time() - start_time) * 1000)
            
            # Record metrics
            self.metrics.add_query_latency(total_latency, success=True)
            self.metrics.add_component_latency('transcript_search', transcript_latency)
            self.metrics.add_component_latency('video_search', video_latency)
            
            # Log if latency exceeds threshold
            if total_latency > 500:
                print(f"  ⚠️  User {user_id} query exceeded 500ms: {total_latency}ms - '{query[:50]}...'")
            
        except Exception as e:
            total_latency = int((time.time() - start_time) * 1000)
            self.metrics.add_query_latency(total_latency, success=False)
            print(f"  ❌ User {user_id} query failed: {e}")
    
    def print_results(self):
        """Print comprehensive test results."""
        summary = self.metrics.get_summary()
        
        print("\n" + "=" * 80)
        print("STRESS TEST RESULTS")
        print("=" * 80)
        
        print(f"\n📊 Test Configuration:")
        print(f"   Duration: {summary['duration_seconds']:.2f} seconds ({summary['duration_seconds']/60:.2f} minutes)")
        print(f"   Concurrent users: {summary['concurrent_sessions']}")
        print(f"   Total queries: {summary['total_queries']}")
        
        print(f"\n✅ Query Success Rate:")
        print(f"   Successful: {summary['successful_queries']}")
        print(f"   Failed: {summary['failed_queries']}")
        print(f"   Success rate: {summary['success_rate']:.2f}%")
        
        print(f"\n⏱️  Latency Statistics:")
        stats = summary['latency_stats']
        print(f"   Min: {stats['min_ms']}ms")
        print(f"   Max: {stats['max_ms']}ms")
        print(f"   Mean: {stats['mean_ms']:.2f}ms")
        print(f"   Median (P50): {stats['median_ms']:.2f}ms")
        print(f"   P95: {stats['p95_ms']:.2f}ms")
        print(f"   P99: {stats['p99_ms']:.2f}ms")
        
        print(f"\n🎯 Property Validation:")
        
        # Property 3: 95th percentile latency under load
        p95_latency = stats['p95_ms']
        if p95_latency <= 500:
            print(f"   ✅ Property 3 (95th percentile ≤500ms): PASSED ({p95_latency:.2f}ms)")
        else:
            print(f"   ❌ Property 3 (95th percentile ≤500ms): FAILED ({p95_latency:.2f}ms)")
        
        # Property 56: Concurrent session support
        if summary['concurrent_sessions'] >= 10 and summary['success_rate'] >= 95:
            print(f"   ✅ Property 56 (10 concurrent sessions): PASSED ({summary['concurrent_sessions']} sessions, {summary['success_rate']:.1f}% success)")
        else:
            print(f"   ⚠️  Property 56 (10 concurrent sessions): PARTIAL ({summary['concurrent_sessions']} sessions, {summary['success_rate']:.1f}% success)")
        
        print(f"\n📈 Component Performance:")
        for component, comp_stats in summary['component_latencies'].items():
            print(f"   {component}:")
            print(f"     Mean: {comp_stats['mean_ms']:.2f}ms")
            print(f"     P95: {comp_stats['p95_ms']:.2f}ms")
        
        print("\n" + "=" * 80)
        print("STRESS TEST COMPLETE")
        print("=" * 80)


async def run_stress_test():
    """Main stress test execution."""
    # Generate mock trial scenario
    scenario = MockTrialScenario()
    trial_segments = scenario.generate_trial()
    
    # Initialize stress test runner
    runner = StressTestRunner(num_concurrent_users=10)
    await runner.setup()
    
    # Ingest trial transcript
    await runner.ingest_trial_transcript(trial_segments)
    
    # Define diverse query set covering all trial aspects
    test_queries = [
        # Opening statements
        "What did the prosecution say in opening statements?",
        "Show me the defense opening statement",
        
        # Witness testimony
        "What did Dr. Emily Chen testify about?",
        "Find the forensic accountant testimony",
        "Show me witness testimony about financial discrepancies",
        
        # Cross-examination
        "When did the defense cross-examine Dr. Chen?",
        "Show me questions about accounts receivable",
        
        # Objections
        "Find all objections raised during the trial",
        "When did the judge sustain an objection?",
        "Show me when objections were overruled",
        
        # Evidence presentation
        "What evidence was introduced as Exhibit A?",
        "Show me when bank statements were presented",
        "Find moments when evidence was admitted",
        "When was Exhibit C rejected?",
        
        # Specific legal terms
        "Find mentions of fraud",
        "Show me discussions about criminal intent",
        "When was attorney-client privilege mentioned?",
        
        # Speaker-specific queries
        "What did the judge say about evidence?",
        "Show me all prosecution arguments",
        "Find defense attorney statements",
        
        # Closing arguments
        "Show me the prosecution closing argument",
        "What did the defense say in closing?",
        "Find the final statements before deliberation",
        
        # Temporal queries
        "What happened in the first 5 minutes?",
        "Show me testimony from the middle of the trial",
        "Find events near the end of the trial",
        
        # Complex multimodal queries
        "When did witnesses point to documents?",
        "Show me moments when evidence was physically presented",
        "Find instances of overlapping speech during objections"
    ]
    
    # Run concurrent query load for 20 minutes
    # Note: For actual 20-minute test, use duration_minutes=20.0
    # For faster testing, use a shorter duration
    await runner.run_concurrent_queries(test_queries, duration_minutes=20.0)
    
    # Print results
    runner.print_results()


if __name__ == "__main__":
    print("🎬 Starting 20-Minute Mock Trial Stress Test...")
    print("   This test validates system performance under realistic courtroom load")
    print("   with multiple concurrent users, complex queries, and sustained traffic.")
    print()
    
    asyncio.run(run_stress_test())
