export const retailers = [
    {
        id: 'watch-it',
        name: 'Watch It!',
        url: 'https://www.watchit.ca/',
        buildSearchUrl: (term) =>
            `https://www.watchit.ca/pages/search-results-page?q=${encodeURIComponent(
                term
            )}`,
    },
    {
        id: 'watchory',
        name: 'Watchory',
        url: 'https://watchory.ca/',
        buildSearchUrl: (term) =>
            `https://watchory.ca/search?q=${encodeURIComponent(term)}`,
    },
    {
        id: 'big-time-watches',
        name: 'Big Time Watches',
        url: 'https://bigtimewatches.com/',
        buildSearchUrl: (term) =>
            `https://bigtimewatches.com/search?q=${encodeURIComponent(term)}`,
    },
    {
        id: 'city-watches',
        name: 'City Watches',
        url: 'https://www.citywatches.ca/',
        buildSearchUrl: (term) =>
            `https://www.citywatches.ca/search?q=${encodeURIComponent(term)}`,
    },
    {
        id: 'ebay',
        name: 'eBay',
        url: 'https://www.ebay.ca/',
        buildSearchUrl: (term) =>
            `https://www.ebay.ca/sch/i.html?_nkw=${encodeURIComponent(term)}`,
    },
    {
        id: 'bijoux-eclore',
        name: 'Bijoux Eclore',
        url: 'https://www.bijouxeclore.com/',
        buildSearchUrl: (term) =>
            `https://www.bijouxeclore.com/search?q=${encodeURIComponent(
                term
            )}&options%5Bprefix%5D=last&type=product`,
    },
    {
        id: 'kavar-jewellers',
        name: 'Kavar Jewellers',
        url: 'https://www.kavarjewellers.ca/',
        buildSearchUrl: (term) =>
            `https://www.kavarjewellers.ca/collections/search%3Fkeyword%3D${encodeURIComponent(
                term
            )}`,
    },
    {
        id: 'peoples-jewellers',
        name: 'Peoples Jewellers',
        url: 'https://www.peoplesjewellers.com/',
        buildSearchUrl: (term) =>
            `https://www.peoplesjewellers.com/search?text=${encodeURIComponent(
                term
            )}`,
    },
    {
        id: 'creation-watches',
        name: 'Creation Watches',
        url: 'https://www.creationwatches.com/',
        buildSearchUrl: (term) =>
            `https://www.creationwatches.com/products/search?keyword=${encodeURIComponent(
                term
            )}`,
    },
    {
        id: 'canada-watch-house',
        name: 'Canada Watch House',
        url: 'https://canadawatchhouse.ca/',
        buildSearchUrl: (term) =>
            `https://canadawatchhouse.ca/search?q=${encodeURIComponent(term)}`,
    },
    {
        id: 'assaleh',
        name: 'Assaleh',
        url: 'https://assaleh.ca/',
        buildSearchUrl: (term) =>
            `https://assaleh.ca/search?q=${encodeURIComponent(term)}`,
    },
    {
        id: 'gem-bijou',
        name: 'Gem Bijou',
        url: 'https://gembijou.com/',
        buildSearchUrl: (term) =>
            `https://gembijou.com/search?q=${encodeURIComponent(
                term
            )}&options%5Bprefix%5D=last`,
    },
];
