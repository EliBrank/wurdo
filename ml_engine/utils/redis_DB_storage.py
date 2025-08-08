import json
from typing import Optional, Dict, Any
from upstash_redis import Redis
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")


# The Upstash Redis connection.
# This client handles the HTTP communication with the Upstash service.
redis_client = Redis(
    url=os.environ.get("KV_REST_API_URL"),
    token=os.environ.get("KV_REST_API_TOKEN")
)


# The TypeScript types can be represented as a Python dictionary.
FullWordData = Dict[str, Any]

async def get_word_data(word: str) -> Optional[FullWordData]:
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
        result = await redis_client.json.get(f"word:{word.lower()}", "$")
       
        # If the key does not exist, json_get returns None.
        if result and len(result)> 0:
            return result[0]
        return None
       

    except Exception as err:
        # Catch other potential errors
        print(f'An unexpected error occurred for word "{word}":', err)
        return None
   
   
def add_word_data(word: str, word_data: Dict[str, any]):
    """_summary_

    Args:
        word (str): The word that is to be created
        obj (obj): The objects to populate the word created

    Returns:
        Optional[FullWordData]: Success confirmation
    """
    if not word or not word_data:
        print("add_word_data requires both a word and ")
        return
    key = f"word:{word.lower()}"
    try:
        result = redis_client.json.set(key, "$", word_data)
        # The Upstash redis.json.set() will use the word for path and the obj to populate
        if result == "OK":
            print("SUccess")
            return True
        else:
            return None
    except Exception as err:
        print(f"An error occured while adding '{word}' Error:{err}")
       
       
async def populate_database_from_file(file_path: str) -> tuple[int, int]:
    """
    Reads a JSON file, and populates the Redis database with the words found.

    Args:
        file_path (str): The path to the JSON file to read.

    Returns:
        A tuple of (successful_adds, total_words).
    """
    print(f"Starting to populate the database from file: {file_path}")

    words_to_add = {}
    successful_adds = 0
    total_words = 0

    try:
        # Use 'with open' to ensure the file is properly closed, even if an error occurs.
        with open(file_path, 'r') as file:
            # json.load() reads from the file and parses the JSON into a Python dictionary.
            words_to_add = json.load(file)

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return (0, 0)
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
        return (0, 0)
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return (0, 0)

    # Now that we have the data, we can loop through it and add each word.
    for word, data in words_to_add.items():
        total_words += 1
        print(f"-> Attempting to add '{word}'...")
        success = add_word_data(word, data)
        if success:
            successful_adds += 1

    print(f"\nFinished processing. Added {successful_adds} out of {total_words} words.")
    return (successful_adds, total_words)


# # --- Example Usage ---
# Make sure your 'probability_tree.json' file is in the same directory as this script.
# file_to_read = "ml_engine/game_data/probability_trees.json"

# # # Call the new function to populate the database.
# success_count, total_count = populate_database_from_file(file_to_read)

# if success_count == total_count:
#     print("\nDatabase population completed successfully!")
# else:
#     print("\nWarning: Some words could not be added to the database.")



# example_word_object = {
#     "serialized": "long string of characters for aal",
#     "metadata": {
#         "size_bytes": 1033,
#         "compressed": True,
#         "stored_at": "2025-08-06T01:59:26"
#     }
# }

# # Add a new word to the database
# word_to_add = "aal"
# add_word_data(word_to_add, example_word_object)

# data = get_word_data(word_to_add)

# if data:
#     print(f"Data for '{word_to_add}':")
#     print(json.dumps(data, indent=2))
# else:
#     print(f"No data found for '{word_to_add}'.")


