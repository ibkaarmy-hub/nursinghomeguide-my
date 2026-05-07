/**
 * JKM Elderly Care Centre (Pusat Jagaan Warga Emas) Scraper
 * Apify SDK v3 syntax
 *
 * Verified HTML structure (2026-05-07):
 *   div.card-body > div.row > div[data-key]  — one per facility
 *   h4                                        — name
 *   p:nth(0)                                  — licence, validity, ownership
 *   p:nth(1)                                  — address
 *   p:nth(2) > span x3                        — tel, fax, email
 *   div.col-sm-2 a[href*="maps.google"]       — GPS coords in href
 */

import { Actor } from 'apify';
import { CheerioCrawler, RequestQueue } from 'crawlee';

const BASE_URL = 'https://www.jkm.gov.my/main/pusat-jagaan';
const PARAMS   = 'search_name=&search_type=pusat-jagaan-warga-emas&search_state=';
const MAX_PAGES = 60;

await Actor.init();

const requestQueue = await RequestQueue.open();
await requestQueue.addRequest({
    url: `${BASE_URL}?${PARAMS}&page=1`,
    userData: { page: 1 },
});

const results = [];

const crawler = new CheerioCrawler({
    requestQueue,
    minConcurrency: 1,
    maxConcurrency: 1,
    requestHandlerTimeoutSecs: 60,
    maxRequestRetries: 3,

    // Residential Malaysian proxy to bypass IP block
    proxyConfiguration: await Actor.createProxyConfiguration({
        groups: ['RESIDENTIAL'],
        countryCode: 'MY',
    }),

    async requestHandler({ $, request }) {
        const { page } = request.userData;
        console.log(`Page ${page}: ${request.url}`);

        const cards = $('[data-key]');
        console.log(`  → ${cards.length} cards found`);

        if (cards.length === 0) {
            console.log(`  → Empty page, stopping.`);
            return;
        }

        cards.each((i, card) => {
            const $card = $(card);
            const paras  = $card.find('p');

            const name = $card.find('h4').text().trim();

            // "No. Pendaftaran : A/PJB WT 034/2022 (Tarikh Tempoh : 30.06.2022 - 29.06.2027) - Kediaman / NGO"
            const licencePara  = $(paras[0]).text().trim();
            const licenceMatch = licencePara.match(/No\.\s*Pendaftaran\s*:\s*([^(]+)/i);
            const validityMatch = licencePara.match(/Tarikh Tempoh\s*:\s*([\d.]+ - [\d.]+)/i);
            const ownershipMatch = licencePara.match(/\)\s*[-–]\s*(.+?)[\r\n]*$/);

            const address = $(paras[1]).text().trim();

            const spans = $(paras[2]).find('span');
            const phone = $(spans[0]).text().replace(/^Tel\s*:\s*/i, '').trim();
            const fax   = $(spans[1]).text().replace(/^Faks\s*:\s*/i, '').trim();
            const email = $(spans[2]).text().replace(/^Emel\s*:\s*/i, '').trim();

            const mapsHref  = $card.find('a[href*="maps.google"]').attr('href') || '';
            const gpsMatch  = mapsHref.match(/[?&]q=([-\d.]+)\s*,\s*([-\d.]+)/);

            results.push({
                name,
                licence_number: licenceMatch  ? licenceMatch[1].trim()  : '',
                validity_date:  validityMatch ? validityMatch[1].trim() : '',
                ownership:      ownershipMatch ? ownershipMatch[1].trim() : '',
                address,
                phone,
                fax,
                email,
                latitude:  gpsMatch ? gpsMatch[1] : '',
                longitude: gpsMatch ? gpsMatch[2] : '',
                maps_url:  mapsHref,
                page,
                scraped_at: new Date().toISOString(),
            });
        });

        console.log(`  → Total so far: ${results.length}`);

        // Queue next page if this one was full
        const nextPage = page + 1;
        if (cards.length === 10 && nextPage <= MAX_PAGES) {
            await requestQueue.addRequest({
                url: `${BASE_URL}?${PARAMS}&page=${nextPage}`,
                userData: { page: nextPage },
                uniqueKey: `page-${nextPage}`,
            });
        }
    },

    failedRequestHandler({ request }) {
        console.error(`Failed: ${request.url}`);
    },
});

await crawler.run();

console.log(`\n✅ Done. ${results.length} centres scraped.`);
await Actor.pushData(results);
console.log('Sample:', JSON.stringify(results[0], null, 2));

await Actor.exit();
