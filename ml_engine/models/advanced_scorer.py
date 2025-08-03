import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedDistilGPT2Scorer:
    """
    Advanced DistilGPT-2 scorer with log-space scoring method.
    """
    
    def __init__(self, model_name: str = "distilgpt2", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.tokenizer = None
        self.model = None
        self.is_initialized = False
        
    def initialize(self):
        """Initialize the model and tokenizer."""
        if self.is_initialized:
            return
            
        logger.info(f"Initializing {self.model_name} model...")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            # Move to device
            self.model.to(self.device)
            self.model.eval()
            
            self.is_initialized = True
            logger.info(f"✅ {self.model_name} initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.model_name}: {e}")
            raise
    
    def get_logits_and_probs(self, prompt: str) -> Tuple[torch.Tensor, torch.Tensor, List[int]]:
        """
        Get both logits and probabilities for a given prompt.
        
        Returns:
            logits: Raw logits from the model
            probabilities: Softmax probabilities
            tokens: Token IDs for the prompt
        """
        if not self.is_initialized:
            self.initialize()
            
        # Tokenize the prompt
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        inputs = inputs.to(self.device)
        
        # Get model outputs
        with torch.no_grad():
            outputs = self.model(inputs)
            logits = outputs.logits
            
        # Get logits and probabilities for the last position
        last_logits = logits[0, -1, :]
        probabilities = F.softmax(last_logits, dim=-1)
        
        return last_logits, probabilities, inputs[0].tolist()
    
    def score_candidate_probability_based(self, prompt: str, candidate_word: str) -> Dict:
        """
        Score candidate using probability-based approach.
        Uses probabilities directly and scales relative to the highest probability.
        """
        try:
            logits, probs, prompt_tokens = self.get_logits_and_probs(prompt)
            
            # Tokenize candidate
            candidate_tokens = self.tokenizer.encode(candidate_word)
            candidate_token = candidate_tokens[0]
            
            # Get candidate probability
            candidate_prob = probs[candidate_token].item()
            
            # Get max probability (most likely token)
            max_prob = probs.max().item()
            
            # Scale relative to max probability (0 to max_prob range)
            normalized_prob = candidate_prob / max_prob
            
            # Creativity score: higher probability = more likely = lower creativity
            creativity_score = 1.0 - normalized_prob
            
            return {
                "method": "probability_based",
                "prompt": prompt,
                "candidate_word": candidate_word,
                "candidate_token": candidate_token,
                "raw_probability": candidate_prob,
                "normalized_probability": normalized_prob,
                "creativity_score": creativity_score,
                "max_probability": max_prob
            }
            
        except Exception as e:
            logger.error(f"Error in probability-based scoring: {e}")
            return {"error": str(e)}
    
    def score_multiple_candidates(self, prompt: str, candidates: List[str]) -> Dict:
        """
        Score multiple candidates using probability-based approach.
        """
        results = {
            "prompt": prompt,
            "candidates": candidates,
            "scores": []
        }
        
        for candidate in candidates:
            score_result = self.score_candidate_probability_based(prompt, candidate)
            results["scores"].append(score_result)
        
        # Sort by creativity score (highest first)
        results["scores"].sort(key=lambda x: x["creativity_score"], reverse=True)
        
        return results
    
    def score_multiple_candidates_optimized(self, prompt: str, candidates: List[str]) -> Dict:
        """
        Score multiple candidates using ONE probability vector lookup.
        Much more efficient than calling the model multiple times.
        """
        try:
            # Get probability vector ONCE
            logits, probs, prompt_tokens = self.get_logits_and_probs(prompt)
            max_prob = probs.max().item()
            
            results = {
                "prompt": prompt,
                "candidates": candidates,
                "scores": [],
                "probability_vector_size": len(probs),
                "max_probability": max_prob
            }
            
            # Look up all candidates from the same probability vector
            for candidate in candidates:
                # Tokenize candidate
                candidate_tokens = self.tokenizer.encode(candidate)
                candidate_token = candidate_tokens[0]
                
                # Get candidate probability from the pre-computed vector
                candidate_prob = probs[candidate_token].item()
                
                # Scale relative to max probability
                normalized_prob = candidate_prob / max_prob
                
                # Creativity score
                creativity_score = 1.0 - normalized_prob
                
                score_result = {
                    "method": "probability_based_optimized",
                    "prompt": prompt,
                    "candidate_word": candidate,
                    "candidate_token": candidate_token,
                    "raw_probability": candidate_prob,
                    "normalized_probability": normalized_prob,
                    "creativity_score": creativity_score,
                    "max_probability": max_prob
                }
                
                results["scores"].append(score_result)
            
            # Sort by creativity score (highest first)
            results["scores"].sort(key=lambda x: x["creativity_score"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in optimized scoring: {e}")
            return {"error": str(e)}
    
    def get_probability_vector(self, prompt: str) -> Dict:
        """
        Get the full probability vector for a prompt.
        This can be stored and used to look up ANY word's probability.
        """
        try:
            logits, probs, prompt_tokens = self.get_logits_and_probs(prompt)
            
            return {
                "prompt": prompt,
                "probability_vector": probs.tolist(),
                "max_probability": probs.max().item(),
                "vocabulary_size": len(probs),
                "prompt_tokens": prompt_tokens
            }
            
        except Exception as e:
            logger.error(f"Error getting probability vector: {e}")
            return {"error": str(e)}
    
    def lookup_candidate_from_vector(self, probability_vector: List[float], candidate_word: str, max_prob: float) -> Dict:
        """
        Look up a candidate's probability from a pre-computed probability vector.
        """
        try:
            # Tokenize candidate
            candidate_tokens = self.tokenizer.encode(candidate_word)
            candidate_token = candidate_tokens[0]
            
            # Get candidate probability from the vector
            candidate_prob = probability_vector[candidate_token]
            
            # Scale relative to max probability
            normalized_prob = candidate_prob / max_prob
            
            # Creativity score
            creativity_score = 1.0 - normalized_prob
            
            return {
                "candidate_word": candidate_word,
                "candidate_token": candidate_token,
                "raw_probability": candidate_prob,
                "normalized_probability": normalized_prob,
                "creativity_score": creativity_score
            }
            
        except Exception as e:
            logger.error(f"Error looking up candidate: {e}")
            return {"error": str(e)}
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        if not self.is_initialized:
            return {"error": "Model not initialized"}
            
        return {
            "model_name": self.model_name,
            "device": self.device,
            "vocabulary_size": self.tokenizer.vocab_size,
            "max_length": self.model.config.max_position_embeddings,
            "parameters": sum(p.numel() for p in self.model.parameters())
        }

# Singleton instance
_global_advanced_scorer = None

def get_advanced_scorer(model_name: str = "distilgpt2", device: str = "cpu") -> AdvancedDistilGPT2Scorer:
    """Get or create a global advanced scorer instance."""
    global _global_advanced_scorer
    
    if _global_advanced_scorer is None:
        _global_advanced_scorer = AdvancedDistilGPT2Scorer(model_name, device)
        _global_advanced_scorer.initialize()
    
    return _global_advanced_scorer 