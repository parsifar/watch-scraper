//DOM Elements
const DOM = Object.freeze({
    inputField: document.getElementById('model-field'),
    suggestionsBox: document.getElementById('suggestions'),
    form: document.getElementById('watch-form'),
    retailersList: document.querySelector('.retailers-wrapper'),
    loaderContainer: document.getElementById('watchLoader'),
    loaderGif: document.getElementById('loader-gif'),
    openAllBtn: document.getElementById('open-all'),
});

const state = {
    isLoading: false,
    models: [],
    priceMap: {},
    displayedRateLimitError: false,
};

const BACKEND_ENDPOINT = '/extract-price';

const retailers = [
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
];

//On Page load
renderRetailersList();

// Load models.json
fetch('models.json')
    .then((res) => res.json())
    .then((data) => {
        state.models = data;
    })
    .catch((err) => console.error('Failed to load models:', err));

// Suggestion logic
DOM.inputField.addEventListener('input', function () {
    const query = this.value.trim().toLowerCase();

    DOM.suggestionsBox.innerHTML = '';

    if (query.length === 0) {
        DOM.suggestionsBox.style.display = 'none';
        return;
    }

    const filtered = state.models.filter((model) =>
        model.toLowerCase().includes(query)
    );

    if (filtered.length === 0) {
        DOM.suggestionsBox.style.display = 'none';
        return;
    }

    filtered.forEach((model) => {
        const li = document.createElement('li');
        li.textContent = model;
        li.addEventListener('click', () => {
            DOM.inputField.value = model;
            DOM.suggestionsBox.style.display = 'none';
            DOM.form.dispatchEvent(new Event('submit')); // submit the form
        });
        DOM.suggestionsBox.appendChild(li);
    });

    DOM.suggestionsBox.style.display = 'block';
});

// Hide suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!DOM.form.contains(e.target)) {
        DOM.suggestionsBox.style.display = 'none';
    }
});

// Form submit handler
DOM.form.addEventListener('submit', function (e) {
    e.preventDefault();

    // Prevent submission if a search is already in progress
    if (state.isLoading) {
        Toastify({
            text: 'Search in progress. Please wait...',
            className: 'info',
        }).showToast();
        return; // exit early
    }

    const searchTerm = DOM.inputField.value.trim();
    if (!searchTerm) return;

    //reset UI
    resetRetailersList();
    showLoader();

    // an array of all fetch requests to the backend
    const fetchPromises = [];

    retailers.forEach((retailer) => {
        const retailerLinkEl = document.getElementById(retailer.id);

        if (!retailerLinkEl) return;

        const searchUrl = retailer.buildSearchUrl(searchTerm);
        retailerLinkEl.href = searchUrl;

        // Fetch prices from the backend
        const fetchPromise = fetch(BACKEND_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: searchUrl,
                term: searchTerm,
            }),
        })
            .then((res) => {
                //If scraper returns empty list
                if (!res.ok) {
                    if (res.status === 404) {
                        retailerLinkEl.textContent = 'No in-stock results';
                    } else if (
                        res.status === 429 &&
                        !state.displayedRateLimitError
                    ) {
                        Toastify({
                            text: 'Too many requests! Please wait 1 minute before trying again.',
                            className: 'error',
                            duration: 10000,
                        }).showToast();

                        state.displayedRateLimitError = true;

                        setTimeout(
                            () => (state.displayedRateLimitError = false),
                            60000
                        );
                    }

                    return null;
                }
                return res.json();
            })
            .then((data) => {
                console.log(data);

                if (typeof data?.starting_from === 'number') {
                    state.priceMap[retailer.id] = data.starting_from;
                    retailerLinkEl.textContent = 'From $' + data.starting_from;
                    retailerLinkEl.style.color = '#00ffff';
                } else {
                    state.priceMap[retailer.id] = null; // mark as failed
                }

                updateListOrder();
            })
            .catch((err) => {
                console.error('Fetch error for', retailer.id, err);
            });

        fetchPromises.push(fetchPromise);
    });

    // Wait for all fetches to complete (success or fail)
    Promise.allSettled(fetchPromises).then(() => {
        hideLoader();
        console.log('All price fetches are done!');

        // Push event to GTM
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({
            event: 'watch_search',
            search_term: searchTerm,
        });
    });
});

// Open all links button
DOM.openAllBtn.addEventListener('click', () => {
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
    if (state.isLoading) return;
    state.isLoading = true;
    DOM.loaderGif.src = './images/watch-loader.gif';
    DOM.loaderContainer.classList.add('active');
}

function hideLoader() {
    state.isLoading = false;
    DOM.loaderContainer.classList.remove('active');
}

function resetRetailersList() {
    state.priceMap = {};
    renderRetailersList();
}
function renderRetailersList() {
    DOM.retailersList.innerHTML = '';
    retailers.forEach((retailer) => {
        DOM.retailersList.innerHTML += retialerCardMarkup(retailer);
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
    const retailerItems = Array.from(DOM.retailersList.children);

    // Record current positions
    const positions = new Map();
    retailerItems.forEach((item) => {
        positions.set(item, item.getBoundingClientRect().top);
    });

    // Sort items: items with valid prices first, ascending, then items without prices
    const sortedRetailerItems = retailerItems.sort((a, b) => {
        const priceA = state.priceMap[a.dataset.id];
        const priceB = state.priceMap[b.dataset.id];

        if (priceA == null && priceB == null) return 0;
        if (priceA == null) return 1; // push empty to end
        if (priceB == null) return -1;
        return priceA - priceB;
    });

    // Reorder in DOM
    sortedRetailerItems.forEach((item) => DOM.retailersList.appendChild(item));

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
