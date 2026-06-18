<template>
  <div>
    <div class="header-container">
      <div>
        <h1 class="header-title">QuantLab Lite</h1>
        <p class="header-subtitle">Professional Quantitative Finance Dashboard & Research Environment</p>
      </div>
      <router-link to="/data-manager" class="btn btn-accent">
        Manage Data
      </router-link>
    </div>

    <!-- Overview Stats -->
    <div class="grid-3 mb-24">
      <div class="card">
        <p class="metric-label">Registered SEC Tickers</p>
        <p class="metric-value">{{ formatNumber(registryCount) }}</p>
        <router-link to="/data-manager" class="badge badge-success" style="margin-top: 8px;">Browse Universe</router-link>
      </div>
      <div class="card">
        <p class="metric-label">Local Database Engine</p>
        <p class="metric-value">PostgreSQL</p>
        <span class="badge badge-success" style="margin-top: 8px;">Active Connection</span>
      </div>
      <div class="card">
        <p class="metric-label">Risk-Free Rate (Configured)</p>
        <p class="metric-value">{{ (rfRate * 100).toFixed(1) }}%</p>
        <span class="badge badge-warning" style="margin-top: 8px;">Dynamic Load</span>
      </div>
    </div>

    <div class="grid-2">
      <!-- Default tickers status -->
      <div class="card">
        <h3 class="mb-24">Core Assets (Default Registry)</h3>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Type</th>
                <th>Database Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ticker in defaultTickers" :key="ticker">
                <td style="font-weight: 700;">{{ ticker }}</td>
                <td>{{ ticker.includes('-USD') ? 'Crypto' : 'Stock/ETF' }}</td>
                <td>
                  <span v-if="statuses[ticker]" class="badge badge-success">
                    {{ statuses[ticker].row_count }} rows ({{ statuses[ticker].last_date }})
                  </span>
                  <span v-else class="badge badge-danger">No Data Stored</span>
                </td>
                <td>
                  <button @click="downloadTicker(ticker)" class="btn btn-primary" style="padding: 6px 12px; font-size: 13px;" :disabled="loading[ticker]">
                    {{ loading[ticker] ? 'Syncing...' : 'Sync Data' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Quick analysis info -->
      <div class="card" style="display: flex; flex-direction: column; gap: 16px;">
        <h3>Analytical Tools</h3>

        <div class="flex align-center gap-16" style="border-bottom: 1px solid var(--border-color); padding-bottom: 16px;">
          <div style="background-color: var(--border-color); padding: 12px; border-radius: 8px; font-size: 20px;">📈</div>
          <div>
            <router-link to="/asset-analyzer" style="font-weight: 700; font-size: 16px;">Asset Analyzer</router-link>
            <p style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">Explore price charts, daily log returns, volatility, drawdowns, and technical indicators.</p>
          </div>
        </div>

        <div class="flex align-center gap-16" style="border-bottom: 1px solid var(--border-color); padding-bottom: 16px;">
          <div style="background-color: var(--border-color); padding: 12px; border-radius: 8px; font-size: 20px;">💼</div>
          <div>
            <router-link to="/portfolio-analyzer" style="font-weight: 700; font-size: 16px;">Portfolio Construction</router-link>
            <p style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">Assign asset weights, calculate correlation/covariance matrices, and view risk/return contributions.</p>
          </div>
        </div>

        <div class="flex align-center gap-16" style="border-bottom: 1px solid var(--border-color); padding-bottom: 16px;">
          <div style="background-color: var(--border-color); padding: 12px; border-radius: 8px; font-size: 20px;">⚡</div>
          <div>
            <router-link to="/portfolio-optimizer" style="font-weight: 700; font-size: 16px;">Portfolio Optimizer</router-link>
            <p style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">Run Monte Carlo simulations to plot the Efficient Frontier, discovering Max Sharpe & Min Vol portfolios.</p>
          </div>
        </div>

        <div class="flex align-center gap-16">
          <div style="background-color: var(--border-color); padding: 12px; border-radius: 8px; font-size: 20px;">🔬</div>
          <div>
            <router-link to="/backtester" style="font-weight: 700; font-size: 16px;">Backtesting Lab</router-link>
            <p style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">Simulate SMA Crossover, Momentum, Mean Reversion, RSI, or Bollinger strategies with commission rules.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import { dataApi } from '../api';

export default {
  name: 'Home',
  setup() {
    const defaultTickers = ref(['SPY', 'QQQ', 'TLT', 'GLD', 'AAPL', 'MSFT', 'NVDA', 'JPM', 'XOM', 'BTC-USD', 'ETH-USD']);
    const statuses = ref({});
    const loading = ref({});
    const rfRate = ref(0.05); // default configuration
    const registryCount = ref(0);

    const loadStatuses = async () => {
      try {
        const res = await dataApi.getSymbols();
        registryCount.value = res.data.registry_count || 0;
        defaultTickers.value = res.data.default_tickers || defaultTickers.value;
        if (res.data && res.data.available) {
          for (const sym of defaultTickers.value) {
            try {
              const statRes = await dataApi.getStatus(sym);
              if (statRes.data && statRes.data.row_count > 0) {
                statuses.value[sym] = statRes.data;
              }
            } catch (err) {
              // no data stored
            }
          }
        }
      } catch (err) {
        console.error('Error fetching statuses', err);
      }
    };

    const formatNumber = (value) => {
      return new Intl.NumberFormat('en-US').format(value || 0);
    };

    const downloadTicker = async (ticker) => {
      loading.value[ticker] = true;
      try {
        await dataApi.downloadData(ticker);
        const statRes = await dataApi.getStatus(ticker);
        statuses.value[ticker] = statRes.data;
      } catch (err) {
        alert(`Failed to download ${ticker}: ` + (err.response?.data?.detail || err.message));
      } finally {
        loading.value[ticker] = false;
      }
    };

    onMounted(() => {
      loadStatuses();
    });

    return {
      defaultTickers,
      statuses,
      loading,
      rfRate,
      registryCount,
      formatNumber,
      downloadTicker,
    };
  },
};
</script>
