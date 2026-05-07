/**
 * JKM Elderly Care Centre (Pusat Jagaan Warga Emas) Scraper
 * Scrapes all 529 centres from jkm.gov.my
 *
 * Apify requirements:
 * - Use residential proxies (Malaysia) to bypass IP block
 * - Actor name: jkm-elderly-care-scraper
 */

const Apify = require('apify');

Apify.main(async () => {
  const baseUrl = 'https://www.jkm.gov.my/main/pusat-jagaan';
  const results = [];
  let pageNum = 1;
  const maxPages = 100; // Safety limit; stop earlier if empty page hit

  const requestQueue = await Apify.openRequestQueue();

  // Add initial request
  await requestQueue.addRequest({
    url: `${baseUrl}?search_name=&search_type=pusat-jagaan-warga-emas&search_state=&page=${pageNum}`,
    uniqueKey: `page-${pageNum}`,
  });

  const crawler = new Apify.CheerioCrawler({
    requestQueue,
    minConcurrency: 1,
    maxConcurrency: 1,
    requestHandlerTimeoutSecs: 60,

    // Use residential proxies to bypass IP block
    useApifyProxy: true,
    apifyProxyGroups: ['RESIDENTIAL'],
    apifyProxyCountry: 'MY', // Malaysian IPs

    handlePageFunction: async ({ $, request, response }) => {
      const currentPage = new URL(request.url).searchParams.get('page') || '1';
      console.log(`Scraping page ${currentPage}: ${request.url}`);

      // Extract centres from this page
      const centres = [];
      const rows = $('table tbody tr'); // TODO: verify selector on actual page

      if (rows.length === 0) {
        console.log(`No rows found on page ${currentPage}. Stopping pagination.`);
        return;
      }

      rows.each((i, row) => {
        const $row = $(row);

        // Extract all cells
        const cells = $row.find('td');
        if (cells.length < 8) return; // Skip malformed rows

        const centre = {
          name: $(cells[0]).text().trim(),
          licence_number: $(cells[1]).text().trim(),
          validity_date: $(cells[2]).text().trim(),
          ownership: $(cells[3]).text().trim(), // Kediaman / NGO / Persendirian
          address: $(cells[4]).text().trim(),
          phone: $(cells[5]).text().trim(),
          fax: $(cells[6]).text().trim(),
          email: $(cells[7]).text().trim(),
          gps: $(cells[8])?.text().trim() || '',
          page: parseInt(currentPage),
          scraped_at: new Date().toISOString(),
        };

        centres.push(centre);
        results.push(centre);
      });

      console.log(`Extracted ${centres.length} centres from page ${currentPage}`);

      // Find pagination links at bottom and add next pages
      const paginationLinks = $('a[href*="page="]'); // Page number links
      const nextPageNum = parseInt(currentPage) + 1;

      if (paginationLinks.length > 0 && nextPageNum <= maxPages) {
        await requestQueue.addRequest({
          url: `${baseUrl}?search_name=&search_type=pusat-jagaan-warga-emas&search_state=&page=${nextPageNum}`,
          uniqueKey: `page-${nextPageNum}`,
        });
      }
    },

    handleFailedRequestFunction: async ({ request }) => {
      console.error(`Request failed: ${request.url}`);
      console.error(`Error: ${request.errorMessages}`);
    },
  });

  await crawler.run();

  console.log(`\n✅ Scraping complete. Total centres extracted: ${results.length}`);

  // Save results to dataset
  const dataset = await Apify.openDataset('JKM_CENTRES');
  await dataset.pushData(results);

  console.log(`Results saved to dataset: JKM_CENTRES`);
  console.log(`Sample result:`, results[0]);
});
