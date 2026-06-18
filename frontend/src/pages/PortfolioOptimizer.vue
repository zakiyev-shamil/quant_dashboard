<template>
  <div>
    <div class="header-container">
      <div>
        <h1 class="header-title">Portfolio Optimizer</h1>
        <p class="header-subtitle">Find the optimal risk-return trade-offs along the Efficient Frontier using Monte Carlo simulation</p>
      </div>
    </div>

    <div class="grid-3 mb-24">
      <!-- Input panel -->
      <div class="card" style="grid-column: span 1;">
        <h3 class="mb-24">Optimization Target</h3>

        <div class="form-group">
          <label>Assets (Comma Separated)</label>
          <input type="text" v-model="assetString" placeholder="SPY, QQQ, GLD, TLT" style="text-transform: uppercase;" />
        </div>

        <div class="form-group">
          <label>Start Date</label>
          <input type="date" v-model="filters.startDate" />
        </div>

        <div class="form-group">
          <label>End Date</label>
          <input type="date" v-model="filters.endDate" />
        </div>

        <div class="form-group">
          <label>Simulation Size (Portfolios)</label>
          <select v-model.number="filters.numPortfolios">
            <option :value="1000">1,000 (Fast)</option>
            <option :value="5000">5,000 (Standard)</option>
            <option :value="10000">10,000 (Detailed)</option>
          </select>
        </div>

        <div class="form-group">
          <label>Min / Max Asset Weight</label>
          <div class="flex gap-16">
            <input type="number" v-model.number="filters.minWeight" placeholder="Min (0.0)" step="0.05" min="0" max="1" style="width: 50%;" />
            <input type="number" v-model.number="filters.maxWeight" placeholder="Max (1.0)" step="0.05" min="0" max="1" style="width: 50%;" />
          </div>
        </div>

        <button @click="runOptimization" class="btn btn-primary w-full" style="width: 100%; margin-top: 16px;" :disabled="optimizing">
          {{ optimizing ? 'Running Simulations...' : 'Optimize Allocation' }}
        </button>
      </div>

      <!-- Frontier scatter chart & allocation weights -->
      <div style="grid-column: span 2; display: flex; flex-direction: column; gap: 24px;">
        <div v-if="error" class="card" style="border-color: var(--accent-danger); background-color: rgba(239, 68, 68, 0.05);">
          <p class="negative-text" style="font-weight: 600;">{{ error }}</p>
        </div>

        <div v-if="optimizing" class="loader"></div>

        <div v-if="result && !optimizing" style="display: flex; flex-direction: column; gap: 24px;">
          <!-- High-level comparisons -->
          <div class="grid-2">
            <!-- Max Sharpe -->
            <div class="card" style="border-left: 4px solid var(--accent-success);">
              <h3 class="positive-text">🏆 Maximum Sharpe Portfolio</h3>
              <div class="flex justify-between mt-24" style="margin-top: 16px;">
                <div>
                  <p class="metric-label">Expected Return</p>
                  <p class="metric-value">{{ (result.max_sharpe_portfolio.expected_return * 100).toFixed(2) }}%</p>
                </div>
                <div>
                  <p class="metric-label">Annual Volatility</p>
                  <p class="metric-value">{{ (result.max_sharpe_portfolio.volatility * 100).toFixed(2) }}%</p>
                </div>
                <div>
                  <p class="metric-label">Sharpe Ratio</p>
                  <p class="metric-value">{{ result.max_sharpe_portfolio.sharpe_ratio.toFixed(2) }}</p>
                </div>
              </div>
              <h4 style="margin-top: 20px;" class="mb-24">Optimal Weights</h4>
              <div class="table-container">
                <table>
                  <tbody>
                    <tr v-for="(weight, ticker) in result.max_sharpe_portfolio.weights" :key="ticker">
                      <td style="font-weight: 700;">{{ ticker }}</td>
                      <td class="text-right" style="font-weight: 700;">{{ (weight * 100).toFixed(1) }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Min Vol -->
            <div class="card" style="border-left: 4px solid var(--accent-secondary);">
              <h3 style="color: var(--accent-secondary);">🛡️ Minimum Volatility Portfolio</h3>
              <div class="flex justify-between mt-24" style="margin-top: 16px;">
                <div>
                  <p class="metric-label">Expected Return</p>
                  <p class="metric-value">{{ (result.min_volatility_portfolio.expected_return * 100).toFixed(2) }}%</p>
                </div>
                <div>
                  <p class="metric-label">Annual Volatility</p>
                  <p class="metric-value">{{ (result.min_volatility_portfolio.volatility * 100).toFixed(2) }}%</p>
                </div>
                <div>
                  <p class="metric-label">Sharpe Ratio</p>
                  <p class="metric-value">{{ result.min_volatility_portfolio.sharpe_ratio.toFixed(2) }}</p>
                </div>
              </div>
              <h4 style="margin-top: 20px;" class="mb-24">Optimal Weights</h4>
              <div class="table-container">
                <table>
                  <tbody>
                    <tr v-for="(weight, ticker) in result.min_volatility_portfolio.weights" :key="ticker">
                      <td style="font-weight: 700;">{{ ticker }}</td>
                      <td class="text-right" style="font-weight: 700;">{{ (weight * 100).toFixed(1) }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Efficient Frontier Plot -->
          <div class="card">
            <h3>Efficient Frontier Map</h3>
            <DataChart v-if="frontierChartData" type="scatter" :data="frontierChartData" :options="frontierChartOptions" />
          </div>
        </div>

        <div v-if="!result && !optimizing" class="card" style="text-align: center; padding: 60px 0;">
          <p style="color: var(--text-secondary); font-size: 16px;">Define symbols on the left and run the optimizer</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import { portfolioApi } from '../api';
import DataChart from '../components/DataChart.vue';

export default {
  name: 'PortfolioOptimizer',
  components: { DataChart },
  setup() {
    const assetString = ref('SPY, QQQ, GLD, TLT');
    const filters = ref({
      startDate: '2015-01-01',
      endDate: '2025-01-01',
      numPortfolios: 5000,
      minWeight: 0.0,
      maxWeight: 1.0,
      interval: '1d',
    });

    const optimizing = ref(false);
    const result = ref(null);
    const frontierChartData = ref(null);
    const error = ref(null);

    const frontierChartOptions = {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              const r = context.raw.y;
              const v = context.raw.x;
              const s = context.raw.sharpe;
              return `Return: ${(r * 100).toFixed(2)}%, Volatility: ${(v * 100).toFixed(2)}%, Sharpe: ${s.toFixed(2)}`;
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: 'Expected Volatility (Standard Deviation)', color: '#9ca3af' },
          grid: { color: '#24272f' },
          ticks: {
            color: '#9ca3af',
            callback: function(value) {
              return (value * 100).toFixed(0) + '%';
            },
          },
        },
        y: {
          title: { display: true, text: 'Expected Return', color: '#9ca3af' },
          grid: { color: '#24272f' },
          ticks: {
            color: '#9ca3af',
            callback: function(value) {
              return (value * 100).toFixed(0) + '%';
            },
          },
        },
      },
    };

    const runOptimization = async () => {
      optimizing.value = true;
      error.value = null;
      result.value = null;
      try {
        const symbols = assetString.value
          .split(',')
          .map(s => s.toUpperCase().trim())
          .filter(Boolean);

        const res = await portfolioApi.optimize(
          symbols,
          filters.value.startDate,
          filters.value.endDate,
          filters.value.numPortfolios,
          filters.value.minWeight,
          filters.value.maxWeight,
          filters.value.interval
        );

        result.value = res.data;

        // Frontier scatter plot dataset
        const points = [];
        const n = res.data.all_portfolios_returns.length;
        for (let i = 0; i < n; i++) {
          points.push({
            x: res.data.all_portfolios_volatilities[i],
            y: res.data.all_portfolios_returns[i],
            sharpe: res.data.all_portfolios_sharpes[i],
          });
        }

        frontierChartData.value = {
          datasets: [
            {
              label: 'Simulated Portfolios',
              data: points,
              backgroundColor: 'rgba(6, 182, 212, 0.4)',
              borderColor: 'transparent',
              pointRadius: 2,
            },
            {
              label: 'Max Sharpe Ratio',
              data: [{
                x: res.data.max_sharpe_portfolio.volatility,
                y: res.data.max_sharpe_portfolio.expected_return,
                sharpe: res.data.max_sharpe_portfolio.sharpe_ratio,
              }],
              backgroundColor: '#10b981',
              borderColor: '#fff',
              pointRadius: 8,
              pointHoverRadius: 10,
            },
            {
              label: 'Min Volatility',
              data: [{
                x: res.data.min_volatility_portfolio.volatility,
                y: res.data.min_volatility_portfolio.expected_return,
                sharpe: res.data.min_volatility_portfolio.sharpe_ratio,
              }],
              backgroundColor: '#ef4444',
              borderColor: '#fff',
              pointRadius: 8,
              pointHoverRadius: 10,
            },
          ],
        };

      } catch (err) {
        error.value = 'Optimization failed. Ensure all assets have data in local database for the selected date range. Error: ' + (err.response?.data?.detail || err.message);
      } finally {
        optimizing.value = false;
      }
    };

    return {
      assetString,
      filters,
      optimizing,
      result,
      frontierChartData,
      frontierChartOptions,
      error,
      runOptimization,
    };
  },
};
</script>
