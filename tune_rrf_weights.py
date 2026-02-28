"""
tune_rrf_weights.py
Tune Reciprocal Rank Fusion (RRF) weighting for hybrid search.

This script tests different alpha weights to balance BM25 keyword matching
and vector semantic search. For legal proceedings, exact legal terminology
recall (BM25) is often more important than semantic similarity.

Validates:
- Property 26: Legal terminology prioritization
- Property 28: Search result completeness
"""
import asyncio
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import json


@dataclass
class SearchResult:
    """Represents a search result with dual scores."""
    text: str
    speaker: str
    timestamp_us: int
    bm25_score: float
    vector_score: float
    combined_score: float = 0.0
    rank: int = 0


@dataclass
class TestQuery:
    """Represents a test query with expected characteristics."""
    query: str
    query_type: str  # "legal_term", "semantic", "mixed"
    expected_focus: str  # "exact_match", "conceptual", "balanced"
    description: str


class RRFTuner:
    """
    Tunes Reciprocal Rank Fusion weighting for hybrid search.
    
    RRF Formula:
    combined_score = alpha * bm25_score + (1 - alpha) * vector_score
    
    Where:
    - alpha = 0.0: Pure vector semantic search
    - alpha = 0.5: Balanced hybrid search
    - alpha = 1.0: Pure BM25 keyword search
    """
    
    def __init__(self):
        """Initialize RRF tuner with mock transcript database."""
        self.mock_transcripts = self._create_mock_transcripts()
        self.test_queries = self._create_test_queries()
        
    def _create_mock_transcripts(self) -> List[Dict[str, Any]]:
        """
        Create mock transcript database with legal terminology.
        
        Returns:
            List of transcript documents with pre-computed BM25 and vector scores
        """
        return [
            {
                'text': '[00:02:15] Judge: This court is now in session under the Fifth Amendment protections.',
                'speaker': 'Judge',
                'timestamp_us': 135_000_000,
                'keywords': ['court', 'session', 'fifth amendment', 'protections', 'judge'],
                'concepts': ['legal_procedure', 'constitutional_rights', 'court_opening']
            },
            {
                'text': '[00:03:42] Prosecution: Your Honor, we invoke Miranda rights advisement for the record.',
                'speaker': 'Prosecution',
                'timestamp_us': 222_000_000,
                'keywords': ['miranda rights', 'advisement', 'prosecution', 'honor', 'record'],
                'concepts': ['constitutional_rights', 'legal_procedure', 'criminal_law']
            },
            {
                'text': '[00:05:18] Witness: I was present at the scene and observed the defendant.',
                'speaker': 'Witness',
                'timestamp_us': 318_000_000,
                'keywords': ['present', 'scene', 'observed', 'defendant', 'witness'],
                'concepts': ['testimony', 'observation', 'factual_statement']
            },
            {
                'text': '[00:07:45] Defense: Objection, Your Honor. This violates the hearsay rule.',
                'speaker': 'Defense',
                'timestamp_us': 465_000_000,
                'keywords': ['objection', 'hearsay rule', 'defense', 'violates', 'honor'],
                'concepts': ['legal_objection', 'evidence_rules', 'procedural_challenge']
            },
            {
                'text': '[00:08:02] Judge: Sustained. The hearsay objection is valid under Federal Rules of Evidence.',
                'speaker': 'Judge',
                'timestamp_us': 482_000_000,
                'keywords': ['sustained', 'hearsay', 'federal rules of evidence', 'valid', 'judge'],
                'concepts': ['judicial_ruling', 'evidence_law', 'procedural_decision']
            },
            {
                'text': '[00:10:30] Witness: The person I saw was wearing distinctive clothing.',
                'speaker': 'Witness',
                'timestamp_us': 630_000_000,
                'keywords': ['person', 'saw', 'wearing', 'distinctive', 'clothing'],
                'concepts': ['testimony', 'observation', 'description']
            },
            {
                'text': '[00:12:15] Prosecution: We present Exhibit A under chain of custody protocols.',
                'speaker': 'Prosecution',
                'timestamp_us': 735_000_000,
                'keywords': ['exhibit a', 'chain of custody', 'protocols', 'present', 'prosecution'],
                'concepts': ['evidence_presentation', 'legal_procedure', 'forensic_protocol']
            },
            {
                'text': '[00:14:50] Defense: We challenge the authentication of this evidence.',
                'speaker': 'Defense',
                'timestamp_us': 890_000_000,
                'keywords': ['challenge', 'authentication', 'evidence', 'defense'],
                'concepts': ['evidence_challenge', 'procedural_objection', 'legal_argument']
            },
            {
                'text': '[00:16:20] Judge: The burden of proof remains with the prosecution.',
                'speaker': 'Judge',
                'timestamp_us': 980_000_000,
                'keywords': ['burden of proof', 'prosecution', 'remains', 'judge'],
                'concepts': ['legal_standard', 'procedural_rule', 'judicial_instruction']
            },
            {
                'text': '[00:18:45] Witness: I felt uncertain about what I observed that night.',
                'speaker': 'Witness',
                'timestamp_us': 1_125_000_000,
                'keywords': ['uncertain', 'observed', 'night', 'felt', 'witness'],
                'concepts': ['credibility', 'testimony', 'uncertainty', 'emotional_state']
            },
            {
                'text': '[00:20:10] Prosecution: The preponderance of evidence supports our case.',
                'speaker': 'Prosecution',
                'timestamp_us': 1_210_000_000,
                'keywords': ['preponderance of evidence', 'supports', 'case', 'prosecution'],
                'concepts': ['legal_standard', 'argument', 'evidence_weight']
            },
            {
                'text': '[00:22:30] Defense: We request a sidebar conference regarding admissibility.',
                'speaker': 'Defense',
                'timestamp_us': 1_350_000_000,
                'keywords': ['sidebar conference', 'admissibility', 'request', 'defense'],
                'concepts': ['procedural_request', 'evidence_rules', 'legal_procedure']
            }
        ]
    
    def _create_test_queries(self) -> List[TestQuery]:
        """
        Create 5 diverse test queries for A/B comparison.
        
        Returns:
            List of test queries with different characteristics
        """
        return [
            TestQuery(
                query="Miranda rights",
                query_type="legal_term",
                expected_focus="exact_match",
                description="Exact legal terminology - should prioritize BM25 keyword match"
            ),
            TestQuery(
                query="arguments about witness credibility",
                query_type="semantic",
                expected_focus="conceptual",
                description="Conceptual query - should prioritize vector semantic search"
            ),
            TestQuery(
                query="hearsay objection",
                query_type="legal_term",
                expected_focus="exact_match",
                description="Specific legal term - should prioritize BM25 keyword match"
            ),
            TestQuery(
                query="evidence presentation procedures",
                query_type="mixed",
                expected_focus="balanced",
                description="Mixed query - benefits from both keyword and semantic matching"
            ),
            TestQuery(
                query="Fifth Amendment protections",
                query_type="legal_term",
                expected_focus="exact_match",
                description="Constitutional term - should prioritize BM25 keyword match"
            )
        ]
    
    def compute_bm25_score(self, query: str, document: Dict[str, Any]) -> float:
        """
        Compute BM25 score for keyword matching.
        
        Args:
            query: Search query
            document: Document with keywords
            
        Returns:
            BM25 score (0.0 to 1.0)
        """
        query_terms = set(query.lower().split())
        doc_keywords = set(document['keywords'])
        
        # Count matching terms
        matches = query_terms.intersection(doc_keywords)
        
        if not matches:
            return 0.0
        
        # Simple BM25 approximation: match ratio with term frequency boost
        match_score = len(matches) / len(query_terms) if query_terms else 0.0
        
        # Boost for exact phrase matches
        query_lower = query.lower()
        text_lower = document['text'].lower()
        if query_lower in text_lower:
            match_score *= 1.5
        
        # Normalize to 0-1 range
        return min(match_score, 1.0)
    
    def compute_vector_score(self, query: str, document: Dict[str, Any]) -> float:
        """
        Compute vector semantic similarity score.
        
        Args:
            query: Search query
            document: Document with concepts
            
        Returns:
            Vector similarity score (0.0 to 1.0)
        """
        # Map query to concepts (simplified semantic understanding)
        query_concepts = self._extract_concepts(query)
        doc_concepts = set(document['concepts'])
        
        # Compute concept overlap
        if not query_concepts:
            return 0.0
        
        matches = query_concepts.intersection(doc_concepts)
        semantic_score = len(matches) / len(query_concepts) if query_concepts else 0.0
        
        # Boost for related concepts (semantic similarity)
        related_boost = self._compute_concept_similarity(query_concepts, doc_concepts)
        semantic_score = (semantic_score + related_boost) / 2
        
        return min(semantic_score, 1.0)
    
    def _extract_concepts(self, query: str) -> set:
        """Extract semantic concepts from query."""
        query_lower = query.lower()
        concepts = set()
        
        # Legal terminology concepts
        if any(term in query_lower for term in ['miranda', 'fifth amendment', 'sixth amendment']):
            concepts.add('constitutional_rights')
        if any(term in query_lower for term in ['hearsay', 'objection', 'sustained', 'overruled']):
            concepts.add('legal_objection')
            concepts.add('evidence_rules')
        if any(term in query_lower for term in ['evidence', 'exhibit', 'chain of custody']):
            concepts.add('evidence_presentation')
            concepts.add('forensic_protocol')
        if any(term in query_lower for term in ['credibility', 'testimony', 'witness']):
            concepts.add('testimony')
            concepts.add('credibility')
        if any(term in query_lower for term in ['burden of proof', 'preponderance']):
            concepts.add('legal_standard')
        if any(term in query_lower for term in ['procedure', 'protocol', 'admissibility']):
            concepts.add('legal_procedure')
        
        return concepts
    
    def _compute_concept_similarity(self, query_concepts: set, doc_concepts: set) -> float:
        """Compute similarity between concept sets."""
        if not query_concepts or not doc_concepts:
            return 0.0
        
        # Related concept pairs (semantic relationships)
        related_pairs = {
            ('constitutional_rights', 'legal_procedure'),
            ('legal_objection', 'procedural_challenge'),
            ('evidence_presentation', 'legal_procedure'),
            ('testimony', 'credibility'),
            ('legal_standard', 'procedural_rule'),
        }
        
        similarity = 0.0
        for q_concept in query_concepts:
            for d_concept in doc_concepts:
                if (q_concept, d_concept) in related_pairs or (d_concept, q_concept) in related_pairs:
                    similarity += 0.3
        
        return min(similarity, 1.0)
    
    def search_with_alpha(self, query: str, alpha: float, top_k: int = 5) -> List[SearchResult]:
        """
        Perform hybrid search with specified alpha weight.
        
        Args:
            query: Search query
            alpha: Weight for BM25 (0.0 = pure vector, 1.0 = pure BM25)
            top_k: Number of results to return
            
        Returns:
            List of search results ranked by combined score
        """
        results = []
        
        for doc in self.mock_transcripts:
            bm25_score = self.compute_bm25_score(query, doc)
            vector_score = self.compute_vector_score(query, doc)
            
            # RRF formula: combined_score = alpha * bm25 + (1 - alpha) * vector
            combined_score = alpha * bm25_score + (1 - alpha) * vector_score
            
            if combined_score > 0:
                results.append(SearchResult(
                    text=doc['text'],
                    speaker=doc['speaker'],
                    timestamp_us=doc['timestamp_us'],
                    bm25_score=bm25_score,
                    vector_score=vector_score,
                    combined_score=combined_score
                ))
        
        # Sort by combined score
        results.sort(key=lambda x: x.combined_score, reverse=True)
        
        # Assign ranks and return top_k
        for i, result in enumerate(results[:top_k], 1):
            result.rank = i
        
        return results[:top_k]
    
    def evaluate_alpha(self, alpha: float) -> Dict[str, Any]:
        """
        Evaluate search quality for a specific alpha value.
        
        Args:
            alpha: Alpha weight to test
            
        Returns:
            Evaluation metrics
        """
        print(f"\n{'='*80}")
        print(f"TESTING ALPHA = {alpha:.2f}")
        print(f"{'='*80}")
        print(f"Configuration: {alpha*100:.0f}% BM25 keyword + {(1-alpha)*100:.0f}% vector semantic")
        
        query_results = []
        
        for test_query in self.test_queries:
            print(f"\n{'-'*80}")
            print(f"Query: \"{test_query.query}\"")
            print(f"Type: {test_query.query_type} | Expected Focus: {test_query.expected_focus}")
            print(f"Description: {test_query.description}")
            print(f"{'-'*80}")
            
            results = self.search_with_alpha(test_query.query, alpha, top_k=5)
            
            if not results:
                print("⚠️  No results found")
                query_results.append({
                    'query': test_query.query,
                    'query_type': test_query.query_type,
                    'results_count': 0,
                    'avg_bm25': 0.0,
                    'avg_vector': 0.0,
                    'avg_combined': 0.0,
                    'top_result_bm25': 0.0,
                    'top_result_vector': 0.0
                })
                continue
            
            # Display results
            for result in results:
                timestamp_sec = result.timestamp_us / 1_000_000
                print(f"\n  [{result.rank}] Score: {result.combined_score:.3f} "
                      f"(BM25: {result.bm25_score:.3f}, Vector: {result.vector_score:.3f})")
                print(f"      {result.speaker} at {timestamp_sec:.1f}s")
                print(f"      {result.text[:100]}...")
            
            # Compute metrics
            avg_bm25 = sum(r.bm25_score for r in results) / len(results)
            avg_vector = sum(r.vector_score for r in results) / len(results)
            avg_combined = sum(r.combined_score for r in results) / len(results)
            
            query_results.append({
                'query': test_query.query,
                'query_type': test_query.query_type,
                'expected_focus': test_query.expected_focus,
                'results_count': len(results),
                'avg_bm25': avg_bm25,
                'avg_vector': avg_vector,
                'avg_combined': avg_combined,
                'top_result_bm25': results[0].bm25_score,
                'top_result_vector': results[0].vector_score,
                'top_result_combined': results[0].combined_score
            })
        
        # Aggregate metrics
        legal_term_queries = [r for r in query_results if r['query_type'] == 'legal_term']
        semantic_queries = [r for r in query_results if r['query_type'] == 'semantic']
        
        metrics = {
            'alpha': alpha,
            'query_results': query_results,
            'avg_bm25_contribution': sum(r['avg_bm25'] for r in query_results) / len(query_results),
            'avg_vector_contribution': sum(r['avg_vector'] for r in query_results) / len(query_results),
            'legal_term_avg_score': sum(r['avg_combined'] for r in legal_term_queries) / len(legal_term_queries) if legal_term_queries else 0.0,
            'semantic_avg_score': sum(r['avg_combined'] for r in semantic_queries) / len(semantic_queries) if semantic_queries else 0.0
        }
        
        return metrics
    
    def run_ab_comparison(self) -> Dict[str, Any]:
        """
        Run A/B comparison across different alpha weights.
        
        Tests alpha values: 0.3, 0.5, 0.6, 0.7, 0.8
        
        Returns:
            Comparison results with recommendations
        """
        print("="*80)
        print("RECIPROCAL RANK FUSION (RRF) ALPHA WEIGHT TUNING")
        print("="*80)
        print("\nObjective: Balance BM25 keyword matching and vector semantic search")
        print("Context: Legal proceedings require exact legal terminology recall")
        print("\nTesting 5 alpha values: 0.3, 0.5, 0.6, 0.7, 0.8")
        print("  - Lower alpha (0.3): Emphasizes semantic understanding")
        print("  - Higher alpha (0.7-0.8): Emphasizes exact keyword matching")
        print("  - Balanced alpha (0.5): Equal weight to both approaches")
        
        # Test different alpha values
        alpha_values = [0.3, 0.5, 0.6, 0.7, 0.8]
        all_metrics = []
        
        for alpha in alpha_values:
            metrics = self.evaluate_alpha(alpha)
            all_metrics.append(metrics)
        
        # Generate comparison report
        print(f"\n{'='*80}")
        print("COMPARISON SUMMARY")
        print(f"{'='*80}")
        
        print(f"\n{'Alpha':<8} {'BM25 Contrib':<15} {'Vector Contrib':<15} {'Legal Terms':<15} {'Semantic':<15}")
        print(f"{'-'*80}")
        
        for metrics in all_metrics:
            print(f"{metrics['alpha']:<8.2f} "
                  f"{metrics['avg_bm25_contribution']:<15.3f} "
                  f"{metrics['avg_vector_contribution']:<15.3f} "
                  f"{metrics['legal_term_avg_score']:<15.3f} "
                  f"{metrics['semantic_avg_score']:<15.3f}")
        
        # Determine best alpha for legal proceedings
        best_alpha = self._recommend_alpha(all_metrics)
        
        return {
            'all_metrics': all_metrics,
            'recommended_alpha': best_alpha,
            'test_queries': [q.__dict__ for q in self.test_queries]
        }
    
    def _recommend_alpha(self, all_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Recommend best alpha value based on metrics.
        
        For legal proceedings, we prioritize:
        1. High performance on legal terminology queries (exact matches)
        2. Reasonable performance on semantic queries (conceptual understanding)
        3. Overall balance
        
        Args:
            all_metrics: Metrics for all tested alpha values
            
        Returns:
            Recommendation with reasoning
        """
        print(f"\n{'='*80}")
        print("RECOMMENDATION")
        print(f"{'='*80}")
        
        # Score each alpha based on legal proceedings requirements
        scored_alphas = []
        
        for metrics in all_metrics:
            # Legal term performance is 2x more important for courtroom use
            legal_term_score = metrics['legal_term_avg_score'] * 2.0
            semantic_score = metrics['semantic_avg_score'] * 1.0
            
            # Combined weighted score
            total_score = legal_term_score + semantic_score
            
            scored_alphas.append({
                'alpha': metrics['alpha'],
                'total_score': total_score,
                'legal_term_score': metrics['legal_term_avg_score'],
                'semantic_score': metrics['semantic_avg_score']
            })
        
        # Find best alpha
        best = max(scored_alphas, key=lambda x: x['total_score'])
        
        print(f"\nRecommended Alpha: {best['alpha']:.2f}")
        print(f"  Configuration: {best['alpha']*100:.0f}% BM25 + {(1-best['alpha'])*100:.0f}% Vector")
        print(f"\nReasoning:")
        print(f"  - Legal term query performance: {best['legal_term_score']:.3f}")
        print(f"  - Semantic query performance: {best['semantic_score']:.3f}")
        print(f"  - Weighted total score: {best['total_score']:.3f}")
        
        if best['alpha'] >= 0.7:
            print(f"\n✅ High BM25 weight prioritizes exact legal terminology matching")
            print(f"   This is optimal for courtroom proceedings where statute names,")
            print(f"   case citations, and specific legal terms must be recalled precisely.")
        elif best['alpha'] >= 0.5:
            print(f"\n✅ Balanced weight provides good performance on both exact matches")
            print(f"   and conceptual queries, suitable for mixed legal queries.")
        else:
            print(f"\n⚠️  Lower BM25 weight emphasizes semantic understanding over exact")
            print(f"   matching. Consider increasing alpha for better legal term recall.")
        
        return {
            'alpha': best['alpha'],
            'bm25_weight': best['alpha'],
            'vector_weight': 1 - best['alpha'],
            'legal_term_score': best['legal_term_score'],
            'semantic_score': best['semantic_score'],
            'total_score': best['total_score'],
            'reasoning': f"Optimal for legal proceedings with {best['alpha']*100:.0f}% emphasis on exact keyword matching"
        }


async def main():
    """Run RRF tuning experiment."""
    tuner = RRFTuner()
    results = tuner.run_ab_comparison()
    
    # Save results to file
    output_file = "rrf_tuning_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}")
    
    print("\n✅ RRF tuning complete!")
    print("\nNext Steps:")
    print("  1. Update constants.py with recommended alpha value")
    print("  2. Configure TurboPuffer RAG with optimal weights")
    print("  3. Test with real courtroom transcript data")
    print("  4. Monitor query performance in production")


if __name__ == "__main__":
    asyncio.run(main())
