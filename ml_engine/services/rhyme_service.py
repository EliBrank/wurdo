import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import logging
from models.cmu_rhyme_client import CMURhymeClient

logger = logging.getLogger(__name__)

@dataclass
class RhymeData:
    perfect: List[str]
    rich: List[str]
    slant: List[str]
    all_rhymes: List[str]

class RhymeProcessor:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.cmu_client = CMURhymeClient()
    
    def filter_by_length(self, words: List[Dict]) -> List[str]:
        """Filter words to 3-7 characters, alphabetic only."""
        filtered = []
        for word_data in words:
            word = word_data.get('word', '').lower()
            if (3 <= len(word) <= 7 and 
                re.match(r'^[a-zA-Z]+$', word)):
                filtered.append(word)
        return filtered
    
    def get_frequency(self, word_data: Dict) -> float:
        """Extract frequency from word data (placeholder for CMU approach)."""
        # For CMU Dictionary, we'll use a simple approach
        # In a real implementation, you might integrate with frequency data
        return 1.0  # Default frequency for all words
    
    def is_standard_word(self, word_data: Dict, min_frequency: float = 1.0) -> bool:
        """Check if a word meets our quality standards."""
        word = word_data.get('word', '').lower()
        
        # Check if it's alphabetic only
        if not re.match(r'^[a-zA-Z]+$', word):
            return False
        
        # Check length (3-7 characters)
        if len(word) < 3 or len(word) > 7:
            return False
        
        # Check if it's pronounceable (using CMU Dictionary)
        if not self.cmu_client.is_pronounceable(word):
            return False
        
        # Check for excessive repeated letters
        if self._has_excessive_repeats(word):
            return False
        
        return True
    
    def _has_excessive_repeats(self, word: str) -> bool:
        """Check for excessive repeated letters that suggest non-standard words."""
        # Check for 3+ consecutive same letters
        for i in range(len(word) - 2):
            if word[i] == word[i+1] == word[i+2]:
                return True
        
        return False
    
    def categorize_rhymes(self, api_results: Dict, start_word: str, min_frequency: float = 1.0) -> RhymeData:
        """Categorize rhymes using CMU Dictionary."""
        # Get rhymes from CMU Dictionary
        all_rhymes = self.cmu_client.get_rhymes(start_word)
        
        # Filter rhymes by quality
        filtered_rhymes = self.cmu_client.filter_rhymes_by_quality(all_rhymes)
        
        # Categorize by quality using CMU Dictionary
        categorized = self.cmu_client.categorize_rhymes_by_quality(start_word, filtered_rhymes)
        
        # Convert to our expected format
        perfect_rhymes = categorized.get('perfect', [])
        near_rhymes = categorized.get('near', [])
        
        # For now, treat near rhymes as slant rhymes
        slant_rhymes = near_rhymes
        
        # Rich rhymes (homophones) - we'll need to implement this separately
        rich_rhymes = []
        
        # Remove duplicates and sort
        perfect_set = set(perfect_rhymes)
        rich_set = set(rich_rhymes)
        slant_set = set(slant_rhymes) - perfect_set - rich_set
        
        all_rhymes = list(perfect_set | rich_set | slant_set)
        
        return RhymeData(
            perfect=list(perfect_set),
            rich=list(rich_set),
            slant=list(slant_set),
            all_rhymes=all_rhymes
        )
    
    def is_legitimate_rhyme(self, word_data: Dict, start_word: str, rhyme_type: str) -> bool:
        """Determine if a word is a legitimate rhyme."""
        word = word_data.get('word', '').lower()
        
        # Basic quality checks
        if not self.is_standard_word(word_data):
            return False
        
        # For CMU Dictionary, we trust the categorization
        return True
    
    def _is_phonetic_variation(self, word: str, start_word: str) -> bool:
        """Detect phonetic variations (not needed for CMU Dictionary)."""
        return False  # CMU Dictionary doesn't include phonetic variations
    
    def _is_legitimate_homophone(self, word: str, start_word: str) -> bool:
        """Check against known homophone pairs."""
        # This could be enhanced with a homophone database
        homophone_pairs = [
            ("there", "their"), ("there", "they're"),
            ("here", "hear"), ("where", "wear"),
            ("to", "too"), ("to", "two"),
            ("for", "four"), ("by", "buy"),
            ("see", "sea"), ("meet", "meat")
        ]
        
        for pair in homophone_pairs:
            if word in pair and start_word in pair:
                return True
        
        return False
    
    def _is_legitimate_slant_rhyme(self, word: str, start_word: str) -> bool:
        """Check against known slant rhyme patterns."""
        # This could be enhanced with a slant rhyme database
        slant_patterns = [
            ("light", "like"), ("light", "might"), ("light", "sight"),
            ("cat", "cut"), ("cat", "cot"), ("cat", "kit"),
            ("there", "where"), ("there", "care"), ("there", "share")
        ]
        
        for pattern in slant_patterns:
            if word in pattern and start_word in pattern:
                return True
        
        return False
    
    async def tokenize_rhymes(self, rhyme_data: RhymeData) -> Dict[str, List[int]]:
        """Tokenize all rhyme words efficiently."""
        all_words = (rhyme_data.perfect + 
                    rhyme_data.rich + 
                    rhyme_data.slant)
        
        # Batch tokenization
        tokenized = {}
        for word in all_words:
            try:
                tokens = self.tokenizer.encode(word)
                tokenized[word] = tokens
            except Exception as e:
                logger.warning(f"Failed to tokenize '{word}': {e}")
                continue
        
        return {
            "perfect_tokens": [tokenized[w][0] for w in rhyme_data.perfect if w in tokenized],
            "rich_tokens": [tokenized[w][0] for w in rhyme_data.rich if w in tokenized],
            "slant_tokens": [tokenized[w][0] for w in rhyme_data.slant if w in tokenized],
            "all_tokens": list(set([
                tokenized[w][0] for w in rhyme_data.all_rhymes 
                if w in tokenized
            ]))
        } 