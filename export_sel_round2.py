"""Export next 50 Selangor facilities from sel_remaining_for_later.json
into 5 new batches (sel_batch_6 through sel_batch_10)."""
import json, math

BATCH_SIZE = 10
BATCH_START = 6  # next batch number
TOP_N = 50

with open('sel_remaining_for_later.json', 'r', encoding='utf-8') as f:
    remaining = json.load(f)

print(f'Remaining in queue: {len(remaining)}')
top = remaining[:TOP_N]
n_batches = math.ceil(len(top) / BATCH_SIZE)

for i in range(n_batches):
    chunk = top[i*BATCH_SIZE:(i+1)*BATCH_SIZE]
    fname = f'sel_batch_{BATCH_START + i}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, ensure_ascii=False, indent=2)
    print(f'  {fname}: {len(chunk)} facilities (review counts: {[c["review_count"] for c in chunk[:3]]})')

# Save what's left for round 3
left = remaining[TOP_N:]
with open('sel_remaining_for_later.json', 'w', encoding='utf-8') as f:
    json.dump(left, f, ensure_ascii=False, indent=2)
print(f'\\nLeft for round 3: {len(left)}')
