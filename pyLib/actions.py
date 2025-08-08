import json
from typing import Optional, Dict, Any
from upstash_redis import Redis
import os


# The Upstash Redis connection.
# This client handles the HTTP communication with the Upstash service.
redis_client = Redis(
    url=os.environ.get("KV_REST_API_URL"),
    token=os.environ.get("KV_REST_API_TOKEN")
)


# The TypeScript types can be represented as a Python dictionary.
FullWordData = Dict[str, Any]

def get_word_data(word: str) -> Optional[FullWordData]:
    """
    Fetches word data from Upstash Redis using JSON.GET.
    
    Args:
        word: The word to look up.
        
    Returns:
        The full word data as a dictionary, or None if not found or an error occurs.
    """
    if not word:
        print("get_word_data called with empty word.")
        return None

    try:
        # The Upstash client's json.get() method is accessed directly from the client object.
        result = redis_client.json.get(f"word:{word.lower()}", "$")
        
        # If the key does not exist, json_get returns None.
        return result
        

    except Exception as err:
        # Catch other potential errors
        print(f'An unexpected error occurred for word "{word}":', err)
        return None

# --- Example Usage ---
# Assuming you have a key 'word:test' with JSON data in your Redis instance:
# This is how you would set the data with the upstash client:
# redis_client.json_set('word:test', '$', {'ipa': 'tɛst', 'syllables': 1, 'score': 100})

# Get data for a word
word_to_fetch = "aal"
data = get_word_data(word_to_fetch)

if data:
    print(f"Data for '{word_to_fetch}':")
    print(json.dumps(data, indent=2))
else:
    print(f"No data found for '{word_to_fetch}'.")