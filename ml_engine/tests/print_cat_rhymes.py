import json

with open('test_game_data.json', 'r') as f:
    data = json.load(f)

cat_data = data.get('cat', {})

print("cat rhyme lists:")
for key in ["rhy.val", "rhy.prf.val", "rhy.rch.val", "rhy.sln.val"]:
    print(f"\n{key}:")
    print(cat_data.get(key, [])) 