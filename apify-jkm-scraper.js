/**
 * JKM Elderly Care Centre (Pusat Jagaan Warga Emas) Scraper
 * Scrapes all 529 centres from jkm.gov.my
 *
 * Verified HTML structure (2026-05-07):
 *   div.card-body > div.row > div[data-key]  — one per facility
 *   h4                                        — name
 *   p:nth(0)                                  — licence, validity, ownership
 *   p:nth(1)                                  — address
 *   p:nth(2) > span x3                        — tel, fax, email
 *   div.col-sm-2 a[href*="maps.google"]       — GPS coords in href
 *
 * Pagination: ?page=N at bottom, ~53 pages for 529 results
 */

const Apify = require('apify');

Apify.main(async () => {
  const BASE_URL = 'https://www.jkm.gov.my/main/pusat-jagaan';
  const PARAMS = 'search_name=&search_type=pusat-jagaan-warga-emas&search_state=';
  const MAX_PAGES = 60;

  const requestQueue = await Apify.openRequestQueue();
  await requestQueue.addRequest({
    url: `${BASE_URL}?${PARAMS}&page=1`,
    userData: { page: 1 },
  });

  const allResults = [];

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    minConcurrency: 1,
    maxConcurrency: 1,
    requestHandlerTimeoutSecs: 60,
    maxRequestRetries: 3,

    // Residential Malaysian proxy to bypass IP block
    useApifyProxy: true,
    apifyProxyGroups: ['RESIDENTIAL'],
    apifyProxyCountry: 'MY',

    handlePageFunction: async ({ $, request }) => {
      const { page } = request.userData;
      console.log(`Page ${page}: ${request.url}`);

      const cards = $('[data-key]');
      console.log(`  → Found ${cards.length} cards`);

      if (cards.length === 0) {
        console.log(`  → No cards on page ${page}, stopping.`);
        return;
      }

      cards.each((i, card) => {
        const $card = $(card);
        const paras = $card.find('p');

        // Name
        const name = $card.find('h4').text().trim();

        // Parse licence paragraph: "No. Pendaftaran : A/PJB WT 034/2022 (Tarikh Tempoh : 30.06.2022 - 29.06.2027) - Kediaman / NGO"
        const licencePara = $(paras[0]).text().trim();
        const licenceMatch = licencePara.match(/No\.\s*Pendaftaran\s*:\s*([^\(]+)/i);
        const validityMatch = licencePara.match(/Tarikh Tempoh\s*:\s*([\d.]+ - [\d.]+)/i);
        const ownershipMatch = licencePara.match(/\)\s*-\s*(.+)$/);

        const licence_number = licenceMatch ? licenceMatch[1].trim() : '';
        const validity_date = validityMatch ? validityMatch[1].trim() : '';
        const ownership = ownershipMatch ? ownershipMatch[1].trim() : '';

        // Address
        const address = $(paras[1]).text().trim();

        // Contact spans: Tel, Faks, Emel
        const spans = $(paras[2]).find('span');
        const telRaw = $(spans[0]).text().trim();
        const faxRaw = $(spans[1]).text().trim();
        const emailRaw = $(spans[2]).text().trim();

        const phone = telRaw.replace(/^Tel\s*:\s*/i, '').trim();
        const fax = faxRaw.replace(/^Faks\s*:\s*/i, '').trim();
        const email = emailRaw.replace(/^Emel\s*:\s*/i, '').trim();

        // GPS: extract from Google Maps href "http://maps.google.com/?q=LAT,LNG"
        const mapsHref = $card.find('a[href*="maps.google"]').attr('href') || '';
        const gpsMatch = mapsHref.match(/[?&]q=([-\d.]+),([-\d.]+)/);
        const latitude = gpsMatch ? gpsMatch[1] : '';
        const longitude = gpsMatch ? gpsMatch[2] : '';

        const centre = {
          name,
          licence_number,
          validity_date,
          ownership,
          address,
          phone,
          fax,
          email,
          latitude,
          longitude,
          maps_url: mapsHref,
          page,
          scraped_at: new Date().toISOString(),
        };

        allResults.push(centre);
      });

      console.log(`  → Total so far: ${allResults.length}`);

      // Queue next page if within limit
      const nextPage = page + 1;
      if (nextPage <= MAX_PAGES && cards.length === 10) {
        await requestQueue.addRequest({
          url: `${BASE_URL}?${PARAMS}&page=${nextPage}`,
          userData: { page: nextPage },
          uniqueKey: `page-${nextPage}`,
        });
      }
    },

    handleFailedRequestFunction: async ({ request }) => {
      console.error(`Failed: ${request.url}`, request.errorMessages);
    },
  });

  await crawler.run();

  console.log(`\n✅ Done. Total centres scraped: ${allResults.length}`);

  await Apify.pushData(allResults);
  console.log('Results saved to Apify dataset.');
  console.log('Sample:', JSON.stringify(allResults[0], null, 2));
});
