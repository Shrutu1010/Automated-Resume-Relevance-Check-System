"""
Semantic matching service using embeddings for similarity calculation
"""
import numpy as np
from typing import List, Optional, Union
import logging
from sentence_transformers import SentenceTransformer
import os
from sklearn.metrics.pairwise import cosine_similarity

class SemanticMatcher:
    """Handles semantic similarity using sentence transformers"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize semantic matcher with sentence transformer model
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            logging.info(f"Loaded semantic model: {self.model_name}")
        except Exception as e:
            logging.error(f"Failed to load semantic model {self.model_name}: {e}")
            # Fallback to a smaller model
            try:
                self.model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
                logging.info("Loaded fallback semantic model: paraphrase-MiniLM-L3-v2")
            except Exception as e2:
                logging.error(f"Failed to load fallback model: {e2}")
                self.model = None
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Get embedding vector for text
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.model or not text.strip():
            return None
        
        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Generate embedding
            embedding = self.model.encode(cleaned_text, convert_to_numpy=True)
            return embedding
            
        except Exception as e:
            logging.error(f"Failed to generate embedding: {e}")
            return None
    
    def get_embeddings_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """
        Get embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not self.model:
            return [None] * len(texts)
        
        try:
            # Clean texts
            cleaned_texts = [self._preprocess_text(text) for text in texts]
            
            # Generate embeddings
            embeddings = self.model.encode(cleaned_texts, convert_to_numpy=True)
            return [emb for emb in embeddings]
            
        except Exception as e:
            logging.error(f"Failed to generate batch embeddings: {e}")
            return [None] * len(texts)
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better embedding quality
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Limit text length (models have token limits)
        max_length = 500  # Approximate token limit
        if len(text.split()) > max_length:
            text = ' '.join(text.split()[:max_length])
        
        return text
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Reshape for sklearn if needed
            if embedding1.ndim == 1:
                embedding1 = embedding1.reshape(1, -1)
            if embedding2.ndim == 1:
                embedding2 = embedding2.reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(embedding1, embedding2)[0][0]
            
            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logging.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: np.ndarray, 
                         candidate_embeddings: List[np.ndarray], 
                         top_k: int = 5) -> List[tuple]:
        """
        Find most similar embeddings to query
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embeddings
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        if not candidate_embeddings:
            return []
        
        try:
            similarities = []
            for i, candidate_emb in enumerate(candidate_embeddings):
                if candidate_emb is not None:
                    sim = self.calculate_similarity(query_embedding, candidate_emb)
                    similarities.append((i, sim))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            return similarities[:top_k]
            
        except Exception as e:
            logging.error(f"Failed to find similar embeddings: {e}")
            return []
    
    def semantic_search(self, query: str, documents: List[str], top_k: int = 5) -> List[tuple]:
        """
        Perform semantic search over documents
        
        Args:
            query: Search query
            documents: List of documents to search
            top_k: Number of top results to return
            
        Returns:
            List of (document_index, similarity_score, document_text) tuples
        """
        if not documents:
            return []
        
        try:
            # Get query embedding
            query_embedding = self.get_embedding(query)
            if query_embedding is None:
                return []
            
            # Get document embeddings
            doc_embeddings = self.get_embeddings_batch(documents)
            
            # Find most similar
            similar_indices = self.find_most_similar(query_embedding, doc_embeddings, top_k)
            
            # Return results with document text
            results = []
            for idx, score in similar_indices:
                results.append((idx, score, documents[idx]))
            
            return results
            
        except Exception as e:
            logging.error(f"Semantic search failed: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if semantic matching is available"""
        return self.model is not None

# Global semantic matcher instance
semantic_matcher = SemanticMatcher()
