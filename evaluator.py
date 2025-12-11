import time
import numpy as np
from typing import List, Dict, Any

try:
    from sklearn.metrics.pairwise import cosine_similarity
    from sentence_transformers import SentenceTransformer
    print("Loading the brain (Embedding Model)...")
    MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    HAS_MODELS = True
except ImportError:
    print("Warning: sentence-transformers or sklearn not available. Using fallback.")
    HAS_MODELS = False
    MODEL = None

def fallback_similarity(a, b):
    """Simple fallback similarity using dot product"""
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return np.dot(a, b) / (a_norm * b_norm)

def fallback_encode(text):
    """Simple fallback encoding using character frequencies"""
    if not text:
        return np.zeros(256)
    arr = np.zeros(256)
    for i, ch in enumerate(text[:256]):
        arr[i] = ord(ch) / 255.0
    return arr

class Evaluator:
    def __init__(self, context_texts: List[str], user_message: str, model_response: str):
        self.context_texts = context_texts or []
        self.user_message = user_message or ""
        self.model_response = model_response or ""
        
        # Calculate embeddings
        if HAS_MODELS and MODEL:
            self.user_emb = np.array(MODEL.encode(self.user_message)).reshape(1, -1)
            self.ai_emb = np.array(MODEL.encode(self.model_response)).reshape(1, -1)
            if self.context_texts:
                self.context_embs = np.array(MODEL.encode(self.context_texts))
            else:
                self.context_embs = np.array([])
        else:
            # Fallback encoding
            self.user_emb = fallback_encode(self.user_message).reshape(1, -1)
            self.ai_emb = fallback_encode(self.model_response).reshape(1, -1)
            if self.context_texts:
                self.context_embs = np.array([fallback_encode(ctx) for ctx in self.context_texts])
            else:
                self.context_embs = np.array([])

    def get_relevance_score(self):
        """
        Checks if the User's Question is mathematically similar to the Context.
        If they are similar, the context is relevant.
        """
        if len(self.context_embs) == 0:
            return 0.0
        
        # Compare User Query vs All Context chunks
        if HAS_MODELS:
            similarities = cosine_similarity(self.user_emb, self.context_embs)
        else:
            similarities = np.array([[fallback_similarity(self.user_emb[0], ctx) for ctx in self.context_embs]])
        
        # For the best match found
        best_match = float(np.max(similarities))
        return best_match

    def get_completeness_score(self):
        """
        Checks if the AI's Response covers the Context well.
        We mix two checks:
        1. Math similarity (Embeddings)
        2. Word overlap (Do they use the same keywords?)
        """
        if len(self.context_embs) == 0:
            return 0.0
            
        # 1. Embedding Similarity
        if HAS_MODELS:
            sims = cosine_similarity(self.ai_emb, self.context_embs)
        else:
            sims = np.array([[fallback_similarity(self.ai_emb[0], ctx) for ctx in self.context_embs]])
        emb_score = float(np.max(sims))
        
        # 2. Simple Keyword Overlap (Jaccard Index)
        # For the text to just look at unique words
        ai_words = set(self.model_response.lower().split())
        ctx_words = set(" ".join(self.context_texts).lower().split())
        
        if not ai_words: return 0.0
        
        # Calculate intersection
        overlap = len(ai_words.intersection(ctx_words)) / len(ai_words)
        
        # TO give 60% weight to math similarity, 40% to keyword overlap
        final_score = (0.6 * emb_score) + (0.4 * overlap)
        return final_score

    def check_hallucinations(self):
        """
        Splits the AI response into sentences and checks if EACH sentence
        is supported by the context.
        """
        # Split text into sentences (rough split by period)
        sentences = [s.strip() for s in self.model_response.split('.') if len(s) > 10]
        
        if not sentences:
            return {"summary": {"unsupported_count": 0, "total": 0, "ratio": 0.0}}

        if len(self.context_embs) == 0:
            # If there have no context, everything is technically unsupported
            return {"summary": {"unsupported_count": len(sentences), "total": len(sentences), "ratio": 1.0}}

        unsupported_count = 0
        details = []
        
        # Encode all sentences at once for speed
        if HAS_MODELS and MODEL:
            sent_embs = np.array(MODEL.encode(sentences))
        else:
            sent_embs = np.array([fallback_encode(s) for s in sentences])

        for i, sentence in enumerate(sentences):
            # Compare this sentence to the context
            if HAS_MODELS:
                sims = cosine_similarity(sent_embs[i].reshape(1, -1), self.context_embs)
            else:
                sims = np.array([[fallback_similarity(sent_embs[i], ctx) for ctx in self.context_embs]])
            max_sim = float(np.max(sims)) if sims.size > 0 else 0.0
            
            # THE THRESHOLD:
            # If similarity is below 0.55, we flag it as "Potentially Unsupported"
            is_supported = max_sim > 0.55
            
            if not is_supported:
                unsupported_count += 1
                
            details.append({
                "sentence": sentence,
                "score": max_sim,
                "is_supported": is_supported
            })

        return {
            "summary": {
                "unsupported_count": unsupported_count,
                "total_sentences": len(sentences),
                "unsupported_ratio": unsupported_count / len(sentences)
            },
            "details": details
        }

    def evaluate(self):
        """Runs all checks and returns the full report."""
        start_time = time.time()
        
        results = {
            "relevance_score": self.get_relevance_score(),
            "completeness_score": self.get_completeness_score(),
            "hallucination": self.check_hallucinations()
        }
        
        # Calculate Latency & Cost
        time_taken = time.time() - start_time
        
        # Rough cost calc: 1 token ~= 4 chars. Price $0.0001 per 1k tokens.
        total_chars = len(self.user_message) + len(self.model_response)
        est_cost = (total_chars / 4 / 1000) * 0.0001
        
        results["metrics"] = {
            "latency": time_taken,
            "cost_usd": est_cost
        }
        
        return results