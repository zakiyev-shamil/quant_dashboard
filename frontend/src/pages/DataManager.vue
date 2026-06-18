<template>
  <div>
    <div class="header-container">
      <div>
        <h1 class="header-title">Data Manager</h1>
        <p class="header-subtitle">Browse the full SEC ticker universe and load historical prices into PostgreSQL</p>
      </div>
    </div>

    <div class="grid-3 mb-24">
      <div class="card">
        <p class="metric-label">Ticker Universe</p>
        <p class="metric-value">{{ formatNumber(registryTotal) }}</p>
        <span class="badge badge-success" style="margin-top: 8px;">company_tickers.json</span>
      </div>
      <div class="card">
        <p class="metric-label">Local Datasets</p>
        <p class="metric-value">{{ formatNumber(availableSymbols.length) }}</p>
        <span class="badge badge-warning" style="margin-top: 8px;">PostgreSQL</span>
      </div>
      <div class="card">
        <p class="metric-label">Selected Ticker</p>
        <p class="metric-value">{{ selectedTickerLabel }}</p>
        <span
          class="badge"
          :class="downloadForm.symbol ? 'badge-success' : 'badge-warning'"
          style="margin-top: 8px;"
        >
          {{ downloadForm.symbol ? 'Ready to Download' : 'Pick a Ticker' }}
        </span>
      </div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="section-heading">
          <div>
            <h3>Ticker Universe</h3>
            <p class="muted-text">Search ticker symbols or company names from the SEC registry.</p>
          </div>
          <span class="badge badge-success">{{ formatNumber(searchTotal) }} matches</span>
        </div>

        <div class="form-group mb-24">
          <label>Search All Tickers</label>
          <div class="ticker-search-row">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="AAPL, Tesla, Vanguard, JPM..."
              style="flex: 1; text-transform: uppercase;"
              @input="debounceSearch"
            />
            <button @click="clearSearch" class="btn btn-secondary" type="button">Clear</button>
          </div>
        </div>

        <div class="ticker-chip-row mb-24">
          <button
            v-for="ticker in defaultTickers"
            :key="ticker"
            type="button"
            class="ticker-chip"
            @click="selectTicker(ticker)"
          >
            {{ ticker }}
          </button>
        </div>

        <div v-if="loadingRegistry" class="loader"></div>

        <div v-else class="table-container ticker-results">
          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Company / Title</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="res in searchResults"
                :key="res.ticker"
                :class="{ 'selected-row': res.ticker === downloadForm.symbol }"
              >
                <td class="ticker-symbol">{{ res.ticker }}</td>
                <td>{{ res.name }}</td>
                <td>
                  <button
                    @click="selectTicker(res.ticker, res.name)"
                    class="btn btn-secondary"
                    style="padding: 6px 12px; font-size: 13px;"
                    type="button"
                  >
                    Select
                  </button>
                </td>
              </tr>
              <tr v-if="searchResults.length === 0">
                <td colspan="3" style="text-align: center; color: var(--text-secondary);">
                  No matching tickers found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="section-heading">
          <div>
            <h3>Download & Local Storage</h3>
            <p class="muted-text">Load the selected ticker into the local PostgreSQL price table.</p>
          </div>
        </div>

        <div class="selected-ticker-panel mb-24">
          <div>
            <p class="metric-label">Selected</p>
            <p class="selected-ticker">{{ downloadForm.symbol || 'None' }}</p>
            <p class="muted-text">{{ selectedTickerName || 'Choose from search results or type manually.' }}</p>
          </div>
          <span v-if="dbStatuses[downloadForm.symbol]" class="badge badge-success">
            {{ dbStatuses[downloadForm.symbol].row_count }} rows stored
          </span>
          <span v-else class="badge badge-warning">Not stored yet</span>
        </div>

        <form @submit.prevent="downloadTicker">
          <div class="form-group">
            <label>Ticker Symbol</label>
            <input type="text" v-model="downloadForm.symbol" style="text-transform: uppercase;" required />
          </div>
          <div class="grid-2 compact-grid">
            <div class="form-group">
              <label>Start Date</label>
              <input type="date" v-model="downloadForm.startDate" />
            </div>
            <div class="form-group">
              <label>End Date</label>
              <input type="date" v-model="downloadForm.endDate" />
            </div>
          </div>
          <div class="form-group">
            <label>Interval</label>
            <select v-model="downloadForm.interval">
              <option value="1d">Daily</option>
              <option value="1wk">Weekly</option>
              <option value="1mo">Monthly</option>
            </select>
          </div>
          <button class="btn btn-primary w-full" style="width: 100%; margin-top: 8px;" :disabled="downloading || !downloadForm.symbol">
            {{ downloading ? 'Downloading & Storing...' : 'Download Data' }}
          </button>
        </form>

        <div v-if="downloadMessage" class="status-panel success-panel">
          {{ downloadMessage }}
        </div>
        <div v-if="downloadError" class="status-panel error-panel">
          {{ downloadError }}
        </div>

        <div class="section-heading local-heading">
          <div>
            <h3>Local Database</h3>
            <p class="muted-text">Datasets already stored in PostgreSQL.</p>
          </div>
        </div>

        <div v-if="loadingAvailable" class="loader"></div>

        <div v-else class="table-container local-db-table">
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Rows</th>
                <th>Last Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sym in availableSymbols" :key="sym">
                <td class="ticker-symbol">{{ sym }}</td>
                <td>
                  <span v-if="dbStatuses[sym]" class="badge badge-success">
                    {{ formatNumber(dbStatuses[sym].row_count) }}
                  </span>
                </td>
                <td>{{ dbStatuses[sym]?.last_date || 'N/A' }}</td>
                <td>
                  <button
                    @click="refreshTicker(sym)"
                    class="btn btn-secondary"
                    style="padding: 6px 12px; font-size: 13px;"
                    :disabled="loadingRefresh[sym]"
                    type="button"
                  >
                    {{ loadingRefresh[sym] ? 'Updating...' : 'Update' }}
                  </button>
                </td>
              </tr>
              <tr v-if="availableSymbols.length === 0">
                <td colspan="4" style="text-align: center; color: var(--text-secondary);">
                  No datasets stored in PostgreSQL yet.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue';
import { dataApi } from '../api';

export default {
  name: 'DataManager',
  setup() {
    const defaultTickers = ref([]);
    const registryTotal = ref(0);
    const searchTotal = ref(0);
    const searchQuery = ref('');
    const searchResults = ref([]);
    const searchTimeout = ref(null);
    const selectedTickerName = ref('');

    const downloadForm = ref({
      symbol: '',
      startDate: '2015-01-01',
      endDate: '2025-01-01',
      interval: '1d',
    });

    const downloading = ref(false);
    const loadingRegistry = ref(false);
    const loadingAvailable = ref(false);
    const availableSymbols = ref([]);
    const dbStatuses = ref({});
    const loadingRefresh = ref({});
    const downloadMessage = ref('');
    const downloadError = ref('');

    const selectedTickerLabel = computed(() => downloadForm.value.symbol || 'None');

    const formatNumber = (value) => {
      return new Intl.NumberFormat('en-US').format(value || 0);
    };

    const loadRegistryPreview = async () => {
      loadingRegistry.value = true;
      try {
        const [symbolsRes, registryRes] = await Promise.all([
          dataApi.getSymbols(),
          dataApi.getRegistry(100, 0),
        ]);
        defaultTickers.value = symbolsRes.data.default_tickers || [];
        registryTotal.value = symbolsRes.data.registry_count || registryRes.data.total || 0;
        searchTotal.value = registryRes.data.total || registryTotal.value;
        searchResults.value = registryRes.data.results || [];
      } catch (err) {
        console.error('Failed to load ticker registry', err);
      } finally {
        loadingRegistry.value = false;
      }
    };

    const runSearch = async () => {
      loadingRegistry.value = true;
      try {
        const query = searchQuery.value.trim();
        if (!query) {
          const res = await dataApi.getRegistry(100, 0);
          searchTotal.value = res.data.total || 0;
          searchResults.value = res.data.results || [];
          return;
        }

        const res = await dataApi.searchSymbols(query, 100);
        searchTotal.value = res.data.total_matches || 0;
        searchResults.value = res.data.results || [];
      } catch (err) {
        console.error('Ticker search failed', err);
      } finally {
        loadingRegistry.value = false;
      }
    };

    const debounceSearch = () => {
      if (searchTimeout.value) clearTimeout(searchTimeout.value);
      searchTimeout.value = setTimeout(runSearch, 250);
    };

    const clearSearch = () => {
      searchQuery.value = '';
      runSearch();
    };

    const selectTicker = (ticker, name = '') => {
      downloadForm.value.symbol = ticker.toUpperCase();
      selectedTickerName.value = name;
      downloadMessage.value = '';
      downloadError.value = '';
    };

    const downloadTicker = async () => {
      downloading.value = true;
      downloadMessage.value = '';
      downloadError.value = '';
      try {
        const symbol = downloadForm.value.symbol.toUpperCase().trim();
        downloadForm.value.symbol = symbol;
        const res = await dataApi.downloadData(
          symbol,
          downloadForm.value.startDate,
          downloadForm.value.endDate,
          downloadForm.value.interval
        );
        downloadMessage.value = `${symbol}: ${formatNumber(res.data.rows_saved)} rows downloaded and stored.`;
        await loadAvailableData();
        await fetchStatusFor(symbol);
      } catch (err) {
        downloadError.value = 'Download failed: ' + (err.response?.data?.detail || err.message);
      } finally {
        downloading.value = false;
      }
    };

    const refreshTicker = async (symbol) => {
      loadingRefresh.value[symbol] = true;
      downloadMessage.value = '';
      downloadError.value = '';
      try {
        await dataApi.downloadData(symbol, null, null, '1d');
        await fetchStatusFor(symbol);
        downloadMessage.value = `${symbol} updated.`;
      } catch (err) {
        downloadError.value = 'Failed to refresh data: ' + (err.response?.data?.detail || err.message);
      } finally {
        loadingRefresh.value[symbol] = false;
      }
    };

    const fetchStatusFor = async (symbol) => {
      if (!symbol) return;
      try {
        const res = await dataApi.getStatus(symbol);
        if (res.data && res.data.row_count > 0) {
          dbStatuses.value[symbol] = res.data;
        }
      } catch (err) {
        console.error(err);
      }
    };

    const loadAvailableData = async () => {
      loadingAvailable.value = true;
      try {
        const res = await dataApi.getSymbols();
        availableSymbols.value = res.data.available || [];
        registryTotal.value = res.data.registry_count || registryTotal.value;
        defaultTickers.value = res.data.default_tickers || defaultTickers.value;
        for (const sym of availableSymbols.value) {
          await fetchStatusFor(sym);
        }
      } catch (err) {
        console.error('Failed to load local DB index', err);
      } finally {
        loadingAvailable.value = false;
      }
    };

    onMounted(() => {
      loadRegistryPreview();
      loadAvailableData();
    });

    return {
      defaultTickers,
      registryTotal,
      searchTotal,
      searchQuery,
      searchResults,
      selectedTickerName,
      downloadForm,
      downloading,
      loadingRegistry,
      loadingAvailable,
      availableSymbols,
      dbStatuses,
      loadingRefresh,
      downloadMessage,
      downloadError,
      selectedTickerLabel,
      formatNumber,
      debounceSearch,
      clearSearch,
      selectTicker,
      downloadTicker,
      refreshTicker,
    };
  },
};
</script>
