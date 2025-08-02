import pronouncing
import logging
from typing import Dict, List, Set
import re

logger = logging.getLogger(__name__)

class CMURhymeClient:
    def __init__(self):
        """Initialize CMU Dictionary-based rhyme client."""
        self.pronouncing = pronouncing
        logger.info("Initialized CMU Dictionary rhyme client")
    
    def get_rhymes(self, word: str) -> List[str]:
        """Get all rhymes for a word using CMU Dictionary."""
        try:
            rhymes = self.pronouncing.rhymes(word)
            logger.info(f"Found {len(rhymes)} rhymes for '{word}' using CMU Dictionary")
            return rhymes
        except Exception as e:
            logger.error(f"Error getting rhymes for '{word}': {e}")
            return []
    
    def get_pronunciation(self, word: str) -> List[str]:
        """Get pronunciation for a word."""
        try:
            return self.pronouncing.phones_for_word(word)
        except Exception as e:
            logger.error(f"Error getting pronunciation for '{word}': {e}")
            return []
    
    def get_syllable_count(self, word: str) -> int:
        """Get syllable count for a word."""
        try:
            phones = self.pronouncing.phones_for_word(word)
            if not phones:
                return 0
            
            # Use the built-in syllable_count function for accuracy
            return self.pronouncing.syllable_count(phones[0])
        except Exception as e:
            logger.error(f"Error getting syllable count for '{word}': {e}")
            return 0
    
    def is_pronounceable(self, word: str) -> bool:
        """Check if a word has a pronunciation in CMU Dictionary."""
        try:
            return len(self.pronouncing.phones_for_word(word)) > 0
        except Exception as e:
            logger.error(f"Error checking pronunciation for '{word}': {e}")
            return False
    
    def get_stress_pattern(self, word: str) -> str:
        """Get stress pattern for a word."""
        try:
            stress_patterns = self.pronouncing.stresses_for_word(word)
            if not stress_patterns:
                return ""
            # Return the first stress pattern (most common)
            return stress_patterns[0]
        except Exception as e:
            logger.error(f"Error getting stress pattern for '{word}': {e}")
            return ""
    
    def filter_rhymes_by_quality(self, rhymes: List[str], min_syllables: int = 1, max_syllables: int = 3) -> List[str]:
        """Filter rhymes by syllable count and other quality criteria."""
        filtered = []
        
        for rhyme in rhymes:
            # Check if it's pronounceable
            if not self.is_pronounceable(rhyme):
                continue
            
            # Check length (3-7 characters)
            if len(rhyme) < 3 or len(rhyme) > 7:
                continue
            
            # Check if it's alphabetic only (no hyphens or apostrophes for DistilGPT-2 compatibility)
            if not re.match(r"^[a-zA-Z]+$", rhyme):
                continue
            
            # Check for excessive repeated letters (only 3+ consecutive same letters)
            if self._has_excessive_repeats(rhyme):
                continue
            
            filtered.append(rhyme)
        
        return filtered
    
    def _has_excessive_repeats(self, word: str) -> bool:
        """Check for excessive repeated letters that suggest non-standard words."""
        # Check for 3+ consecutive same letters
        for i in range(len(word) - 2):
            if word[i] == word[i+1] == word[i+2]:
                return True
        
        # Removed the vowel/consonant pattern check - it was too restrictive
        # Words like "air", "ere" are legitimate and should be allowed
        
        return False
    
    def categorize_rhymes_by_quality(self, word: str, rhymes: List[str]) -> Dict[str, List[str]]:
        """Categorize rhymes by quality using CMU Dictionary features."""
        perfect_rhymes = []
        near_rhymes = []
        
        word_phones = self.get_pronunciation(word)
        if not word_phones:
            return {"perfect": [], "near": []}
        
        word_pronunciation = word_phones[0]  # Use first pronunciation
        
        for rhyme in rhymes:
            rhyme_phones = self.get_pronunciation(rhyme)
            if not rhyme_phones:
                continue
            
            rhyme_pronunciation = rhyme_phones[0]
            
            # Check if it's a perfect rhyme (same ending)
            if self._is_perfect_rhyme(word_pronunciation, rhyme_pronunciation):
                perfect_rhymes.append(rhyme)
            elif self._is_near_rhyme(word_pronunciation, rhyme_pronunciation):
                near_rhymes.append(rhyme)
        
        return {
            "perfect": perfect_rhymes,
            "near": near_rhymes
        }
    
    def _is_perfect_rhyme(self, phones1: str, phones2: str) -> bool:
        """Check if two pronunciations form a perfect rhyme."""
        # Extract the rhyming part (last stressed vowel and everything after)
        rhyme1 = self._extract_rhyming_part(phones1)
        rhyme2 = self._extract_rhyming_part(phones2)
        
        return rhyme1 == rhyme2 and rhyme1 != ""
    
    def _is_near_rhyme(self, phones1: str, phones2: str) -> bool:
        """Check if two pronunciations form a near rhyme."""
        # Extract the rhyming part
        rhyme1 = self._extract_rhyming_part(phones1)
        rhyme2 = self._extract_rhyming_part(phones2)
        
        if rhyme1 == "" or rhyme2 == "":
            return False
        
        # Check for similar consonant patterns
        return self._similar_consonant_pattern(rhyme1, rhyme2)
    
    def _extract_rhyming_part(self, phones: str) -> str:
        """Extract the rhyming part of a pronunciation."""
        # Split into phonemes
        phonemes = phones.split()
        
        # Find the last stressed vowel
        for i in range(len(phonemes) - 1, -1, -1):
            if any(stress in phonemes[i] for stress in ['1', '2']):
                # Return from this vowel to the end
                return ' '.join(phonemes[i:])
        
        return ""
    
    def get_rhyming_part(self, word: str) -> str:
        """Get the rhyming part of a word (from stressed vowel to end)."""
        try:
            phones = self.get_pronunciation(word)
            if not phones:
                return ""
            return self.pronouncing.rhyming_part(phones[0])
        except Exception as e:
            logger.error(f"Error getting rhyming part for '{word}': {e}")
            return ""
    
    def search_by_pronunciation(self, pattern: str) -> List[str]:
        """Search for words whose pronunciation matches a regex pattern."""
        try:
            return self.pronouncing.search(pattern)
        except Exception as e:
            logger.error(f"Error searching pronunciation pattern '{pattern}': {e}")
            return []
    
    def search_by_stress_pattern(self, pattern: str) -> List[str]:
        """Search for words whose stress pattern matches a regex pattern."""
        try:
            return self.pronouncing.search_stresses(pattern)
        except Exception as e:
            logger.error(f"Error searching stress pattern '{pattern}': {e}")
            return []
    
    def _similar_consonant_pattern(self, rhyme1: str, rhyme2: str) -> bool:
        """Check if two rhyming parts have similar consonant patterns."""
        # Extract consonants only
        consonants1 = ''.join(c for c in rhyme1 if c.isalpha() and c not in 'AEIOU')
        consonants2 = ''.join(c for c in rhyme2 if c.isalpha() and c not in 'AEIOU')
        
        # Check if they share similar consonant structure
        if len(consonants1) >= 2 and len(consonants2) >= 2:
            # Check if they end with similar consonant patterns
            return consonants1[-2:] == consonants2[-2:]
        
        return False 