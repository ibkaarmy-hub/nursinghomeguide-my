"""Export the final 32 Selangor facilities into 4 batches of 8."""
import json, math, sys
sys.stdout.reconfigure(encoding='utf-8')

BATCH_SIZE = 8
BATCH_START = 16

with open('sel_remaining_for_later.json', 'r', encoding='utf-8') as f:
    remaining = json.load(f)

print(f'Remaining: {len(remaining)}')
n_batches = math.ceil(len(remaining) / BATCH_SIZE)
for i in range(n_batches):
    chunk = remaining[i*BATCH_SIZE:(i+1)*BATCH_SIZE]
    fname = f'sel_batch_{BATCH_START + i}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(chunk, f, ensure_ascii=False, indent=2)
    print(f'  {fname}: {len(chunk)} (rev: {[c["review_count"] for c in chunk[:3]]})')

# Clear the queue file
with open('sel_remaining_for_later.json', 'w', encoding='utf-8') as f:
    json.dump([], f)
print('\\nQueue cleared.')
