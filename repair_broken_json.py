"""Repair broken sel_batch_*_results.json files. Agents emitted unescaped quotes
inside editorial strings, which broke JSON parsing."""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

BS = chr(92)  # \\
QT = chr(34)  # "

def repair(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    try:
        json.loads(text)
        print(f'  {path}: already valid')
        return text
    except json.JSONDecodeError:
        pass

    # Find each editorial field and re-escape its contents
    pattern = re.compile(r'"editorial":\s*"(.*?)",\s*\n\s*"facts":', re.DOTALL)

    def escape_body(body):
        out = []
        i = 0
        while i < len(body):
            c = body[i]
            if c == BS and i + 1 < len(body):
                out.append(body[i:i+2]); i += 2; continue
            if c == QT:
                out.append(BS + QT); i += 1; continue
            if c == '\n':
                out.append(BS + 'n'); i += 1; continue
            if c == '\r':
                i += 1; continue
            if c == '\t':
                out.append(BS + 't'); i += 1; continue
            out.append(c); i += 1
        return ''.join(out)

    def replace_match(m):
        body = m.group(1)
        return f'"editorial": "{escape_body(body)}",\n      "facts":'

    fixed = pattern.sub(replace_match, text)
    try:
        json.loads(fixed)
        print(f'  {path}: repaired')
        return fixed
    except json.JSONDecodeError as e:
        print(f'  {path}: still broken at line {e.lineno} col {e.colno} ({e.msg})')
        lines = fixed.split('\n')
        if 0 <= e.lineno - 1 < len(lines):
            print(f'    L{e.lineno}: {lines[e.lineno-1][:300]}')
        return None

if __name__ == '__main__':
    for f in ['sel_batch_16_results.json', 'sel_batch_19_results.json']:
        fixed = repair(f)
        if fixed:
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(fixed)
