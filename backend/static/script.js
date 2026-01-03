import { retailers } from './retailers.js';

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
DOM.form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (state.isLoading) {
        Toastify({
            text: 'Search in progress...',
            className: 'info',
        }).showToast();
        return;
    }

    const searchTerm = DOM.inputField.value.trim();
    if (!searchTerm) return;

    resetRetailersList();
    showLoader();

    const fetchPromises = retailers.map((retailer) => {
        const retailerLinkEl = document.getElementById(retailer.id);
        if (!retailerLinkEl) return Promise.resolve();

        return fetchRetailerPrice({
            retailer,
            searchTerm,
            retailerLinkEl,
        });
    });

    await Promise.allSettled(fetchPromises);

    hideLoader();

    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
        event: 'watch_search',
        search_term: searchTerm,
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

async function fetchRetailerPrice({ retailer, searchTerm, retailerLinkEl }) {
    const searchUrl = retailer.buildSearchUrl(searchTerm);
    retailerLinkEl.href = searchUrl;

    try {
        const res = await fetch(BACKEND_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: searchUrl,
                term: searchTerm,
            }),
        });

        if (!res.ok) {
            handleFetchError(res, retailerLinkEl);
            state.priceMap[retailer.id] = null;
            return;
        }

        const data = await res.json();

        if (typeof data?.starting_from === 'number') {
            state.priceMap[retailer.id] = data.starting_from;
            retailerLinkEl.textContent = `From $${data.starting_from}`;
            retailerLinkEl.style.color = '#00ffff';
        } else {
            state.priceMap[retailer.id] = null;
        }
    } catch (err) {
        console.error('Fetch error for', retailer.id, err);
        state.priceMap[retailer.id] = null;
    }

    updateListOrder();
}

function handleFetchError(res, retailerLinkEl) {
    if (res.status === 404) {
        retailerLinkEl.textContent = 'No in-stock results';
        return;
    }

    if (res.status === 429 && !state.displayedRateLimitError) {
        Toastify({
            text: 'Too many requests! Please wait 1 minute before trying again.',
            className: 'error',
            duration: 10000,
        }).showToast();

        state.displayedRateLimitError = true;
        setTimeout(() => (state.displayedRateLimitError = false), 60000);
    }
}

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

    // Sort items by price: ascending, nulls last
    const sortedItems = retailerItems.slice().sort((a, b) => {
        const priceA = state.priceMap[a.dataset.id];
        const priceB = state.priceMap[b.dataset.id];

        if (priceA == null && priceB == null) return 0;
        if (priceA == null) return 1;
        if (priceB == null) return -1;
        return priceA - priceB;
    });

    // Record current positions
    const oldPositions = new Map();
    retailerItems.forEach((item) =>
        oldPositions.set(item, item.getBoundingClientRect().top)
    );

    // Reorder DOM first
    sortedItems.forEach((item) => DOM.retailersList.appendChild(item));

    // Apply FLIP transform
    sortedItems.forEach((item) => {
        const oldTop = oldPositions.get(item);
        const newTop = item.getBoundingClientRect().top;
        const delta = oldTop - newTop;

        if (delta) {
            // only transform if changed
            item.style.transform = `translateY(${delta}px)`;
            item.style.transition = 'transform 0s';
        }
    });

    // Animate to final position
    requestAnimationFrame(() => {
        sortedItems.forEach((item) => {
            item.style.transition = 'transform 0.3s ease';
            item.style.transform = '';
        });
    });
}
