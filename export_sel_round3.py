"""Export next 50 Selangor facilities from sel_remaining_for_later.json
into batches 11-15."""
import json, math

BATCH_SIZE = 10
BATCH_START = 11
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
    print(f'  {fname}: {len(chunk)} (rev: {[c["review_count"] for c in chunk[:3]]})')

left = remaining[TOP_N:]
with open('sel_remaining_for_later.json', 'w', encoding='utf-8') as f:
    json.dump(left, f, ensure_ascii=False, indent=2)
print(f'\\nLeft for round 4: {len(left)}')
