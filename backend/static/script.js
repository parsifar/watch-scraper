//DOM Elements
const input = document.getElementById('model-field');
const suggestionsBox = document.getElementById('suggestions');
const form = document.getElementById('watch-form');
const retailerLinks = document.querySelectorAll('.retailer-link');
const retailersList = document.querySelector('.retailers-wrapper');
const loader = document.getElementById('watchLoader');
const loaderAnimatedGif = document.getElementById('loader-gif');

const BACKEND_ENDPOINT = '/extract-price';

let isLoading = false;
let models = [];
let priceMap = {}; // store prices here
let displayedRateLimitError = false;

const retailers = [
    { id: 'watch-it', name: 'Watch It!', url: 'https://www.watchit.ca/' },
    { id: 'watchory', name: 'Watchory', url: 'https://watchory.ca/' },
    {
        id: 'big-time-watches',
        name: 'Big Time Watches',
        url: 'https://bigtimewatches.com/',
    },
    {
        id: 'city-watches',
        name: 'City Watches',
        url: 'https://www.citywatches.ca/',
    },
    { id: 'ebay', name: 'eBay', url: 'https://www.ebay.ca/' },
    {
        id: 'bijoux-eclore',
        name: 'Bijoux Eclore',
        url: 'https://www.bijouxeclore.com/',
    },
    {
        id: 'kavar-jewellers',
        name: 'Kavar Jewellers',
        url: 'https://www.kavarjewellers.ca/',
    },
    {
        id: 'peoples-jewellers',
        name: 'Peoples Jewellers',
        url: 'https://www.peoplesjewellers.com/',
    },
    {
        id: 'creation-watches',
        name: 'Creation Watches',
        url: 'https://www.creationwatches.com/',
    },
    {
        id: 'canada-watch-house',
        name: 'Canada Watch House',
        url: 'https://canadawatchhouse.ca/',
    },
    {
        id: 'assaleh',
        name: 'Assaleh',
        url: 'https://assaleh.ca/',
    },
];

//On Page load
renderRetailersList();

// Load models.json
fetch('models.json')
    .then((res) => res.json())
    .then((data) => {
        models = data;
    })
    .catch((err) => console.error('Failed to load models:', err));

// Suggestion logic
input.addEventListener('input', function () {
    const query = this.value.trim().toLowerCase();

    suggestionsBox.innerHTML = '';

    if (query.length === 0) {
        suggestionsBox.style.display = 'none';
        return;
    }

    const filtered = models.filter((model) =>
        model.toLowerCase().includes(query)
    );

    if (filtered.length === 0) {
        suggestionsBox.style.display = 'none';
        return;
    }

    filtered.forEach((model) => {
        const li = document.createElement('li');
        li.textContent = model;
        li.addEventListener('click', () => {
            input.value = model;
            suggestionsBox.style.display = 'none';
            form.dispatchEvent(new Event('submit')); // submit the form
        });
        suggestionsBox.appendChild(li);
    });

    suggestionsBox.style.display = 'block';
});

// Hide suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!form.contains(e.target)) {
        suggestionsBox.style.display = 'none';
    }
});

// Form submit handler
form.addEventListener('submit', function (e) {
    e.preventDefault();

    // Prevent submission if a search is already in progress
    if (isLoading) {
        Toastify({
            text: 'Search in progress. Please wait...',
            className: 'info',
        }).showToast();
        return; // exit early
    }

    const searchTerm = input.value.trim();
    if (!searchTerm) return;

    //reset UI
    resetRetailersList();
    showLoader();

    // Map of retailer IDs to search URL patterns
    const retailerSearchURLs = getRetailerSearchUrls(searchTerm);

    // Get prices from the backend
    const fetchPromises = [];

    for (const id in retailerSearchURLs) {
        const retailerLink = document.getElementById(id);

        if (!retailerLink) continue;
        retailerLink.href = retailerSearchURLs[id];

        // Fetch prices from the backend
        const fetchPromise = fetch(BACKEND_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: retailerSearchURLs[id],
                term: searchTerm,
            }),
        })
            .then((res) => {
                //If scraper returns empty list
                if (!res.ok) {
                    if (res.status === 404) {
                        retailerLink.textContent = 'No in-stock results';
                    } else if (res.status === 429 && !displayedRateLimitError) {
                        Toastify({
                            text: 'Too many requests! Please wait 1 minute before trying again.',
                            className: 'error',
                            duration: 10000,
                        }).showToast();
                        displayedRateLimitError = true;
                        setTimeout(
                            () => (displayedRateLimitError = false),
                            60000
                        );
                    }

                    return null;
                }
                return res.json();
            })
            .then((data) => {
                console.log(data);

                if (data && data.starting_from != null) {
                    priceMap[id] = data.starting_from;
                    retailerLink.textContent = 'From $' + data.starting_from;
                    retailerLink.style.color = '#00ffff';
                } else {
                    priceMap[id] = null; // mark as failed
                }

                updateListOrder();
            })
            .catch((err) => {
                console.error('Fetch error for', id, err);
            });

        fetchPromises.push(fetchPromise);
    }

    // Wait for all fetches to complete (success or fail)
    Promise.allSettled(fetchPromises).then(() => {
        hideLoader();
        console.log('All price fetches are done!');

        // Push event to GTM
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({
            event: 'watch_search',
            search_term: searchValue,
        });
    });
});

// Open all links button
document.getElementById('open-all').addEventListener('click', () => {
    const links = document.querySelectorAll('.retailer-link');
    links.forEach((link, index) => {
        const url = link.href;
        if (url) {
            // stagger slightly to bypass popup blockers
            setTimeout(() => {
                window.open(url, '_blank');
            }, index * 100);
        }
    });
});

// Functions

function showLoader() {
    if (isLoading) return;
    isLoading = true;
    loaderAnimatedGif.src = './images/watch-loader.gif';
    loader.classList.add('active');
}

function hideLoader() {
    isLoading = false;
    loader.classList.remove('active');
}
function getRetailerSearchUrls(searchTerm) {
    return {
        'watch-it': `https://www.watchit.ca/pages/search-results-page?q=${encodeURIComponent(
            searchTerm
        )}`,
        watchory: `https://watchory.ca/search?q=${encodeURIComponent(
            searchTerm
        )}`,
        'big-time-watches': `https://bigtimewatches.com/search?q=${encodeURIComponent(
            searchTerm
        )}`,
        'city-watches': `https://www.citywatches.ca/search?q=${encodeURIComponent(
            searchTerm
        )}`,
        ebay: `https://www.ebay.ca/sch/i.html?_nkw=${encodeURIComponent(
            searchTerm
        )}`,
        'bijoux-eclore': `https://www.bijouxeclore.com/search?q=${encodeURIComponent(
            searchTerm
        )}&options%5Bprefix%5D=last&type=product`,
        'kavar-jewellers': `https://www.kavarjewellers.ca/collections/search%3Fkeyword%3D${encodeURIComponent(
            searchTerm
        )}`,
        'peoples-jewellers': `https://www.peoplesjewellers.com/search?text=${encodeURIComponent(
            searchTerm
        )}`,
        'creation-watches': `https://www.creationwatches.com/products/search?keyword=${encodeURIComponent(
            searchTerm
        )}`,
        'canada-watch-house': `https://canadawatchhouse.ca/search?q=${encodeURIComponent(
            searchTerm
        )}`,
        assaleh: `https://assaleh.ca/search?q=${encodeURIComponent(
            searchTerm
        )}`,
    };
}

function resetRetailersList() {
    priceMap = {};
    renderRetailersList();
}
function renderRetailersList() {
    retailersList.innerHTML = '';
    retailers.forEach((retailer) => {
        retailersList.innerHTML += retialerCardMarkup(retailer);
    });
}

function retialerCardMarkup(retailer) {
    return `
        <div class="retailer-card" data-id="${retailer.id}">
            <p class="retailer-name">${retailer.name}</p>
            <a
                href="${retailer.url}"
                class="retailer-link"
                id="${retailer.id}"
                target="_blank"
                >Check Price</a
            >
        </div>
        `;
}

function updateListOrder() {
    const retailerItems = Array.from(retailersList.children);

    // Record current positions
    const positions = new Map();
    retailerItems.forEach((item) => {
        positions.set(item, item.getBoundingClientRect().top);
    });

    // Sort items: items with valid prices first, ascending, then items without prices
    const sortedRetailerItems = retailerItems.sort((a, b) => {
        const priceA = priceMap[a.dataset.id];
        const priceB = priceMap[b.dataset.id];

        if (priceA == null && priceB == null) return 0;
        if (priceA == null) return 1; // push empty to end
        if (priceB == null) return -1;
        return priceA - priceB;
    });

    // Reorder in DOM
    sortedRetailerItems.forEach((item) => retailersList.appendChild(item));

    // Apply FLIP animation
    sortedRetailerItems.forEach((item) => {
        const oldTop = positions.get(item);
        const newTop = item.getBoundingClientRect().top;
        const delta = oldTop - newTop;

        item.style.transform = `translateY(${delta}px)`;
        item.style.transition = 'transform 0s';
    });

    // Force reflow and animate
    requestAnimationFrame(() => {
        sortedRetailerItems.forEach((item) => {
            item.style.transition = 'transform 0.3s ease';
            item.style.transform = '';
        });
    });
}
