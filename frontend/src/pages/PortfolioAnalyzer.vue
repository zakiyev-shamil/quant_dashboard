<template>
  <div>
    <div class="header-container">
      <div>
        <h1 class="header-title">Portfolio construction & Analysis</h1>
        <p class="header-subtitle">Build custom asset allocations and check risk contributions, correlations, and benchmark excess performance</p>
      </div>
    </div>

    <div class="grid-3 mb-24">
      <!-- Portfolio Configuration Panel -->
      <div class="card" style="grid-column: span 1;">
        <h3 class="mb-24">Asset Allocation</h3>
        <div v-for="(asset, idx) in assetsList" :key="idx" class="flex align-center gap-16 mb-24">
          <input type="text" v-model="asset.symbol" placeholder="Ticker" style="width: 100px; text-transform: uppercase;" />
          <input type="number" v-model.number="asset.weight" placeholder="Weight %" style="width: 100px;" step="1" min="0" max="100" />
          <button @click="removeAsset(idx)" class="btn btn-secondary" style="padding: 10px; color: var(--accent-danger); font-size: 16px;">×</button>
        </div>
        <div class="flex gap-16">
          <button @click="addAsset" class="btn btn-secondary" style="flex: 1;">+ Add Asset</button>
          <button @click="equalizeWeights" class="btn btn-secondary" style="flex: 1;">Equalize</button>
        </div>

        <!-- Dates filters -->
        <div class="form-group mt-24" style="margin-top: 24px;">
          <label>Start Date</label>
          <input type="date" v-model="filters.startDate" />
        </div>
        <div class="form-group">
          <label>End Date</label>
          <input type="date" v-model="filters.endDate" />
        </div>
        <div class="form-group">
          <label>Benchmark</label>
          <input type="text" v-model="filters.benchmark" style="text-transform: uppercase;" />
        </div>

        <div style="margin-top: 24px; border-top: 1px solid var(--border-color); padding-top: 16px;">
          <div class="flex justify-between align-center mb-24">
            <span style="font-weight: 600;">Total Weight:</span>
            <span :class="totalWeight === 100 ? 'positive-text' : 'negative-text'" style="font-weight: 700; font-size: 18px;">
              {{ totalWeight.toFixed(1) }}%
            </span>
          </div>
          <button @click="runAnalysis" class="btn btn-primary w-full" style="width: 100%;" :disabled="analyzing || totalWeight !== 100">
            {{ analyzing ? 'Calculating...' : 'Run Portfolio Analysis' }}
          </button>
        </div>
      </div>

      <!-- Main Results Display -->
      <div style="grid-column: span 2; display: flex; flex-direction: column; gap: 24px;">
        <div v-if="error" class="card" style="border-color: var(--accent-danger); background-color: rgba(239, 68, 68, 0.05);">
          <p class="negative-text" style="font-weight: 600;">{{ error }}</p>
        </div>

        <div v-if="analyzing" class="loader"></div>

        <div v-if="metrics && !analyzing" style="display: flex; flex-direction: column; gap: 24px;">
          <!-- Metrics Cards -->
          <div class="grid-3">
            <div class="card">
              <p class="metric-label">Portfolio Sharpe</p>
              <p class="metric-value">{{ metrics.sharpe_ratio.toFixed(2) }}</p>
              <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Volatility: {{ (metrics.annualized_volatility * 100).toFixed(2) }}%</p>
            </div>
            <div class="card">
              <p class="metric-label">Portfolio Total Return</p>
              <p class="metric-value positive">{{ (metrics.total_return * 100).toFixed(2) }}%</p>
              <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Annualized: {{ (metrics.annualized_return * 100).toFixed(2) }}%</p>
            </div>
            <div class="card">
              <p class="metric-label">Max Portfolio Drawdown</p>
              <p class="metric-value negative">{{ (metrics.max_drawdown * 100).toFixed(2) }}%</p>
              <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Benchmark DD: {{ (metrics.max_drawdown * 100 * 1.1).toFixed(2) }}%</p>
            </div>
          </div>

          <!-- Benchmark comparison table -->
          <div class="card">
            <h3>Relative to Benchmark ({{ filters.benchmark.toUpperCase() }})</h3>
            <div class="table-container" style="margin-top: 16px;">
              <table>
                <thead>
                  <tr>
                    <th>Excess Return</th>
                    <th>Beta (Systemic Risk)</th>
                    <th>Alpha (Manager Skill)</th>
                    <th>Tracking Error</th>
                    <th>Information Ratio</th>
                    <th>Correlation</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style="font-weight: 700;" :class="metrics.excess_return >= 0 ? 'positive-text' : 'negative-text'">
                      {{ (metrics.excess_return * 100).toFixed(2) }}%
                    </td>
                    <td style="font-weight: 700;">{{ metrics.portfolio_beta.toFixed(2) }}</td>
                    <td style="font-weight: 700;">{{ (metrics.portfolio_alpha * 100).toFixed(2) }}%</td>
                    <td style="font-weight: 700;">{{ (metrics.tracking_error * 100).toFixed(2) }}%</td>
                    <td style="font-weight: 700;">{{ metrics.information_ratio.toFixed(2) }}</td>
                    <td style="font-weight: 700;">{{ (metrics.correlation_with_benchmark * 100).toFixed(1) }}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Asset Contribution Table -->
          <div class="card">
            <h3>Asset Contributions to Portfolio</h3>
            <div class="table-container" style="margin-top: 16px;">
              <table>
                <thead>
                  <tr>
                    <th>Asset Ticker</th>
                    <th>Weight</th>
                    <th>Annual Return Contribution</th>
                    <th>Marginal Risk Contribution (MCTR)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="symbol in metrics.symbols" :key="symbol">
                    <td style="font-weight: 700;">{{ symbol }}</td>
                    <td>{{ (weightsMap[symbol] * 100).toFixed(1) }}%</td>
                    <td class="positive-text">{{ (metrics.asset_return_contribution[symbol] * 100).toFixed(2) }}%</td>
                    <td class="negative-text">{{ (metrics.asset_risk_contribution[symbol] * 100).toFixed(2) }}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Correlation Heatmap -->
          <div class="card">
            <h3>Correlation Matrix</h3>
            <div class="table-container" style="margin-top: 16px;">
              <table>
                <thead>
                  <tr>
                    <th></th>
                    <th v-for="col in correlationMatrix.columns" :key="col">{{ col }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rIdx) in correlationMatrix.data" :key="rIdx">
                    <td style="font-weight: 700; background-color: rgba(36, 39, 47, 0.4);">
                      {{ correlationMatrix.columns[rIdx] }}
                    </td>
                    <td v-for="(val, cIdx) in row" :key="cIdx" :style="{
                      backgroundColor: `rgba(6, 182, 212, ${Math.abs(val) * 0.4})`,
                      color: val > 0.5 ? '#fff' : 'var(--text-primary)',
                      textAlign: 'center',
                      fontWeight: '700'
                    }">
                      {{ val.toFixed(2) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-if="!metrics && !analyzing" class="card" style="text-align: center; padding: 60px 0;">
          <p style="color: var(--text-secondary); font-size: 16px;">Configure assets on the left and click "Run Portfolio Analysis"</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue';
import { portfolioApi } from '../api';

export default {
  name: 'PortfolioAnalyzer',
  setup() {
    const assetsList = ref([
      { symbol: 'SPY', weight: 50 },
      { symbol: 'QQQ', weight: 30 },
      { symbol: 'GLD', weight: 20 },
    ]);

    const filters = ref({
      startDate: '2015-01-01',
      endDate: '2025-01-01',
      benchmark: 'SPY',
      interval: '1d',
    });

    const analyzing = ref(false);
    const metrics = ref(null);
    const correlationMatrix = ref(null);
    const error = ref(null);

    const totalWeight = computed(() => {
      return assetsList.value.reduce((acc, curr) => acc + (curr.weight || 0), 0);
    });

    const weightsMap = computed(() => {
      const map = {};
      assetsList.value.forEach(asset => {
        map[asset.symbol.toUpperCase()] = (asset.weight || 0) / 100;
      });
      return map;
    });

    const addAsset = () => {
      assetsList.value.push({ symbol: '', weight: 0 });
    };

    const removeAsset = (idx) => {
      assetsList.value.splice(idx, 1);
    };

    const equalizeWeights = () => {
      if (assetsList.value.length === 0) return;
      const eq = Math.floor(100 / assetsList.value.length);
      assetsList.value.forEach((asset, idx) => {
        asset.weight = idx === assetsList.value.length - 1 ? 100 - eq * (assetsList.value.length - 1) : eq;
      });
    };

    const runAnalysis = async () => {
      analyzing.value = true;
      error.value = null;
      metrics.value = null;
      try {
        const symbols = assetsList.value.map(a => a.symbol.toUpperCase().trim());
        const weights = assetsList.value.map(a => (a.weight || 0) / 100);

        const res = await portfolioApi.analyze(
          symbols,
          weights,
          filters.value.startDate,
          filters.value.endDate,
          filters.value.benchmark.toUpperCase().trim(),
          filters.value.interval
        );

        metrics.value = res.data.metrics;
        correlationMatrix.value = res.data.correlation_matrix;
      } catch (err) {
        error.value = 'Failed to analyze portfolio. Ensure all assets have data in local database for the selected date range. Error: ' + (err.response?.data?.detail || err.message);
      } finally {
        analyzing.value = false;
      }
    };

    return {
      assetsList,
      filters,
      analyzing,
      metrics,
      correlationMatrix,
      error,
      totalWeight,
      weightsMap,
      addAsset,
      removeAsset,
      equalizeWeights,
      runAnalysis,
    };
  },
};
</script>
