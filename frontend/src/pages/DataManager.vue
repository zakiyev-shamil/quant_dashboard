<template>
  <div>
    <div class="header-container">
      <div>
        <h1 class="header-title">Data Manager</h1>
        <p class="header-subtitle">Ingest historical price datasets from yfinance into local PostgreSQL storage</p>
      </div>
    </div>

    <div class="grid-2">
      <!-- Search and download card -->
      <div class="card">
        <h3>Search & Download Tickers</h3>
        <p style="font-size: 14px; color: var(--text-secondary); margin-top: 8px;" class="mb-24">
          Find matching SEC tickers and load them to PostgreSQL.
        </p>

        <div class="form-group mb-24">
          <label>Search Tickers / Company Names</label>
          <div class="flex gap-16">
            <input type="text" v-model="searchQuery" placeholder="Search AAPL, Bitcoin, Vanguard..." style="flex: 1;" @input="debounceSearch" />
          </div>
        </div>

        <!-- Search results list -->
        <div v-if="searchResults.length > 0" class="table-container mb-24" style="max-height: 250px; overflow-y: auto;">
          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Company/Title</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="res in searchResults" :key="res.ticker">
                <td style="font-weight: 700;">{{ res.ticker }}</td>
                <td>{{ res.name }}</td>
                <td>
                  <button @click="selectTicker(res.ticker)" class="btn btn-secondary" style="padding: 6px 12px; font-size: 13px;">
                    Select
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div style="border-top: 1px solid var(--border-color); padding-top: 24px;">
          <h4 class="mb-24">Download settings (Selected Ticker: <span style="color: var(--accent-secondary);">{{ downloadForm.symbol || 'None' }}</span>)</h4>
          <div class="form-group">
            <label>Start Date</label>
            <input type="date" v-model="downloadForm.startDate" />
          </div>
          <div class="form-group">
            <label>End Date</label>
            <input type="date" v-model="downloadForm.endDate" />
          </div>
          <div class="form-group">
            <label>Interval</label>
            <select v-model="downloadForm.interval">
              <option value="1d">Daily</option>
              <option value="1wk">Weekly</option>
              <option value="1mo">Monthly</option>
            </select>
          </div>
          <button @click="downloadTicker" class="btn btn-primary w-full" style="width: 100%; margin-top: 16px;" :disabled="downloading || !downloadForm.symbol">
            {{ downloading ? 'Downloading & Storing in DB...' : 'Download Data' }}
          </button>
        </div>
      </div>

      <!-- Local DB status table -->
      <div class="card">
        <h3>Local Database Directory</h3>
        <p style="font-size: 14px; color: var(--text-secondary); margin-top: 8px;" class="mb-24">
          Overview of all datasets stored locally.
        </p>

        <div v-if="loadingAvailable" class="loader"></div>

        <div v-else class="table-container" style="max-height: 550px; overflow-y: auto;">
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Rows</th>
                <th>First Date</th>
                <th>Last Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sym in availableSymbols" :key="sym">
                <td style="font-weight: 700;">{{ sym }}</td>
                <td>
                  <span v-if="dbStatuses[sym]" class="badge badge-success">{{ dbStatuses[sym].row_count }} rows</span>
                </td>
                <td>{{ dbStatuses[sym]?.first_date || 'N/A' }}</td>
                <td>{{ dbStatuses[sym]?.last_date || 'N/A' }}</td>
                <td>
                  <button @click="refreshTicker(sym)" class="btn btn-secondary" style="padding: 6px 12px; font-size: 13px;" :disabled="loadingRefresh[sym]">
                    {{ loadingRefresh[sym] ? 'Updating...' : 'Update' }}
                  </button>
                </td>
              </tr>
              <tr v-if="availableSymbols.length === 0">
                <td colspan="5" style="text-align: center; color: var(--text-secondary);">No datasets stored in PostgreSQL yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import { dataApi } from '../api';

export default {
  name: 'DataManager',
  setup() {
    const searchQuery = ref('');
    const searchResults = ref([]);
    const searchTimeout = ref(null);

    const downloadForm = ref({
      symbol: '',
      startDate: '2015-01-01',
      endDate: '2025-01-01',
      interval: '1d',
    });

    const downloading = ref(false);
    const loadingAvailable = ref(false);
    const availableSymbols = ref([]);
    const dbStatuses = ref({});
    const loadingRefresh = ref({});

    const debounceSearch = () => {
      if (searchTimeout.value) clearTimeout(searchTimeout.value);
      searchTimeout.value = setTimeout(async () => {
        if (!searchQuery.value) {
          searchResults.value = [];
          return;
        }
        try {
          const res = await dataApi.searchSymbols(searchQuery.value);
          searchResults.value = res.data.results;
        } catch (err) {
          console.error(err);
        }
      }, 300);
    };

    const selectTicker = (ticker) => {
      downloadForm.value.symbol = ticker;
    };

    const downloadTicker = async () => {
      downloading.value = true;
      try {
        await dataApi.downloadData(
          downloadForm.value.symbol,
          downloadForm.value.startDate,
          downloadForm.value.endDate,
          downloadForm.value.interval
        );
        alert(`Successfully downloaded and upserted ${downloadForm.value.symbol}!`);
        loadAvailableData();
      } catch (err) {
        alert('Download failed: ' + (err.response?.data?.detail || err.message));
      } finally {
        downloading.value = false;
      }
    };

    const refreshTicker = async (symbol) => {
      loadingRefresh.value[symbol] = true;
      try {
        await dataApi.downloadData(symbol, null, null, '1d'); // trigger full max refresh
        await fetchStatusFor(symbol);
      } catch (err) {
        alert('Failed to refresh data: ' + (err.response?.data?.detail || err.message));
      } finally {
        loadingRefresh.value[symbol] = false;
      }
    };

    const fetchStatusFor = async (symbol) => {
      try {
        const res = await dataApi.getStatus(symbol);
        dbStatuses.value[symbol] = res.data;
      } catch (err) {
        console.error(err);
      }
    };

    const loadAvailableData = async () => {
      loadingAvailable.value = true;
      try {
        const res = await dataApi.getSymbols();
        availableSymbols.value = res.data.available || [];
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
      loadAvailableData();
    });

    return {
      searchQuery,
      searchResults,
      downloadForm,
      downloading,
      loadingAvailable,
      availableSymbols,
      dbStatuses,
      loadingRefresh,
      debounceSearch,
      selectTicker,
      downloadTicker,
      refreshTicker,
    };
  },
};
</script>
