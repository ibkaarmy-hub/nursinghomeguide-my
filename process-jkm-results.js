/**
 * Post-processor for JKM scraped data
 * Maps JKM fields to nursing-home-guide sheet schema
 * Identifies duplicates, generates comparison reports
 *
 * Usage: node process-jkm-results.js <path-to-jkm-raw-json>
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Utility: normalise address for deduplication
function normaliseAddress(addr) {
  return addr
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .replace(/[.,]/g, '')
    .trim();
}

// Utility: compute slug from name + address
function generateSlug(name, address) {
  const combined = `${name} ${address}`.toLowerCase();
  return combined
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '-')
    .substring(0, 60);
}

// Main processor
async function processJKMResults(inputFile) {
  if (!fs.existsSync(inputFile)) {
    console.error(`❌ File not found: ${inputFile}`);
    process.exit(1);
  }

  console.log(`📂 Reading JKM raw results from: ${inputFile}`);
  const rawData = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));
  const jkmCentres = Array.isArray(rawData) ? rawData : rawData.data || [];

  console.log(`✅ Loaded ${jkmCentres.length} centres from JKM scrape\n`);

  // Try to load existing sheet data for deduplication
  let existingFacilities = [];
  const existingDataPath = path.join(__dirname, 'data', 'facilities.csv');
  if (fs.existsSync(existingDataPath)) {
    const csv = fs.readFileSync(existingDataPath, 'utf-8');
    const lines = csv.split('\n');
    const headers = lines[0].split(',');
    existingFacilities = lines.slice(1).map(line => {
      const parts = line.split(',');
      return {
        slug: parts[headers.indexOf('slug')] || '',
        title: parts[headers.indexOf('title')] || '',
        address: parts[headers.indexOf('address')] || '',
        phone: parts[headers.indexOf('phone')] || '',
      };
    });
    console.log(`📋 Loaded ${existingFacilities.length} existing facilities for deduplication\n`);
  }

  // Map JKM to sheet schema
  const mapped = jkmCentres.map(centre => ({
    // Identity
    title: centre.name,
    slug: generateSlug(centre.name, centre.address),
    address: centre.address,
    area: extractArea(centre.address),

    // Contact
    phone: centre.phone,
    email: centre.email,
    fax: centre.fax,

    // Licensing
    licence_number: centre.licence_number,
    validity_date: centre.validity_date,

    // Location
    latitude: centre.gps ? extractLat(centre.gps) : '',
    longitude: centre.gps ? extractLng(centre.gps) : '',

    // Admin
    ownership_type: centre.ownership,
    status: '', // blank = live
    last_updated: new Date().toISOString().split('T')[0],
    source: 'JKM_scrape_2026',

    // Raw JKM data (for reference)
    _jkm_raw: JSON.stringify(centre),
  }));

  // Deduplicate: check for matches in existing data
  const duplicates = [];
  const newCentres = [];

  mapped.forEach(jkm => {
    const existingMatch = existingFacilities.find(ex => {
      const jkmAddrNorm = normaliseAddress(jkm.address);
      const exAddrNorm = normaliseAddress(ex.address);
      return jkmAddrNorm === exAddrNorm ||
             (jkm.phone && jkm.phone === ex.phone && ex.phone.length > 0);
    });

    if (existingMatch) {
      duplicates.push({
        jkm_centre: jkm.title,
        jkm_address: jkm.address,
        existing_slug: existingMatch.slug,
        existing_title: existingMatch.title,
        confidence: 'address_match',
        action_needed: 'verify & merge',
      });
    } else {
      newCentres.push(jkm);
    }
  });

  console.log(`\n📊 Deduplication Results:`);
  console.log(`   - Potential duplicates: ${duplicates.length}`);
  console.log(`   - New centres: ${newCentres.length}`);
  console.log(`   - Total: ${mapped.length}\n`);

  // Write outputs
  const outputDir = './jkm-results';
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

  // 1. CSV ready for sheet import
  const csvHeaders = Object.keys(newCentres[0] || {}).filter(k => !k.startsWith('_')).join(',');
  const csvRows = newCentres.map(c =>
    Object.keys(c)
      .filter(k => !k.startsWith('_'))
      .map(k => `"${(c[k] || '').toString().replace(/"/g, '""')}"`)
      .join(',')
  ).join('\n');

  const csvOutput = `${csvHeaders}\n${csvRows}`;
  fs.writeFileSync(path.join(outputDir, 'jkm_new_centres.csv'), csvOutput);
  console.log(`✅ Saved new centres CSV: ${outputDir}/jkm_new_centres.csv`);

  // 2. Duplicates report
  fs.writeFileSync(
    path.join(outputDir, 'jkm_duplicates_report.json'),
    JSON.stringify(duplicates, null, 2)
  );
  console.log(`✅ Saved duplicates report: ${outputDir}/jkm_duplicates_report.json`);

  // 3. Full mapped results
  fs.writeFileSync(
    path.join(outputDir, 'jkm_full_mapped.json'),
    JSON.stringify(mapped, null, 2)
  );
  console.log(`✅ Saved full mapped results: ${outputDir}/jkm_full_mapped.json`);

  // Summary
  console.log(`\n📋 Summary:`);
  console.log(`   JKM scraped: ${jkmCentres.length}`);
  console.log(`   New to add: ${newCentres.length}`);
  console.log(`   Potential merges: ${duplicates.length}`);
  console.log(`\n📁 All results in: ./${outputDir}/`);
}

// Helper: extract area from address (Malay states)
function extractArea(address) {
  const states = [
    'Johor', 'Kedah', 'Kelantan', 'Kuala Lumpur', 'Labuan', 'Melaka',
    'Negeri Sembilan', 'Pahang', 'Penang', 'Perak', 'Perlis', 'Putrajaya',
    'Sabah', 'Sarawak', 'Selangor', 'Terengganu'
  ];
  for (const state of states) {
    if (address.toLowerCase().includes(state.toLowerCase())) {
      return state;
    }
  }
  return '';
}

// Helper: extract latitude from GPS string (assumes "lat, lng" format)
function extractLat(gpsString) {
  const match = gpsString.match(/^([0-9.]+)/);
  return match ? match[1] : '';
}

// Helper: extract longitude from GPS string
function extractLng(gpsString) {
  const match = gpsString.match(/[0-9.]+,\s*([0-9.]+)/);
  return match ? match[1] : '';
}

// Run
const inputFile = process.argv[2];
if (!inputFile) {
  console.error('Usage: node process-jkm-results.js <path-to-jkm-raw-json>');
  process.exit(1);
}

processJKMResults(inputFile).catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
