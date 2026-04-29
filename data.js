// Google Sheets CSV URL — update this if you change the sheet
const SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub?output=csv";

async function loadFacilities() {
    const res = await fetch(SHEET_CSV_URL);
    const text = await res.text();
    return parseCSV(text);
}

function parseCSV(text) {
    const lines = text.trim().split('\n');
    const headers = parseCSVLine(lines[0]);
    return lines.slice(1).map(line => {
        const vals = parseCSVLine(line);
        const obj = {};
        headers.forEach((h, i) => obj[h.trim()] = (vals[i] || '').trim());
        return obj;
    }).filter(r => r.title);
}

function parseCSVLine(line) {
    const result = [];
    let cur = '', inQuotes = false;
    for (let i = 0; i < line.length; i++) {
        const ch = line[i];
        if (ch === '"') {
            if (inQuotes && line[i+1] === '"') { cur += '"'; i++; }
            else inQuotes = !inQuotes;
        } else if (ch === ',' && !inQuotes) {
            result.push(cur); cur = '';
        } else {
            cur += ch;
        }
    }
    result.push(cur);
    return result;
}
