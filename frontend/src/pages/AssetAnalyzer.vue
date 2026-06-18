<template>
  <div>
    <div class="header-container">
      <div>
        <h1 class="header-title">Asset Analyzer</h1>
        <p class="header-subtitle">Evaluate performance, risk metrics, and drawdowns for individual assets</p>
      </div>
    </div>

    <!-- Filters Panel -->
    <div class="card mb-24">
      <form @submit.prevent="runAnalysis" class="flex align-center gap-16" style="flex-wrap: wrap;">
        <div class="form-group" style="margin-bottom: 0;">
          <label>Ticker Symbol</label>
          <input type="text" v-model="filters.symbol" placeholder="e.g. SPY" required style="width: 120px;" />
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label>Start Date</label>
          <input type="date" v-model="filters.startDate" style="width: 160px;" />
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label>End Date</label>
          <input type="date" v-model="filters.endDate" style="width: 160px;" />
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label>Interval</label>
          <select v-model="filters.interval" style="width: 120px;">
            <option value="1d">Daily</option>
            <option value="1wk">Weekly</option>
            <option value="1mo">Monthly</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary" style="align-self: flex-end;" :disabled="analyzing">
          {{ analyzing ? 'Analyzing...' : 'Analyze' }}
        </button>
      </form>
    </div>

    <div v-if="error" class="card mb-24" style="border-color: var(--accent-danger); background-color: rgba(239, 68, 68, 0.05);">
      <p class="negative-text" style="font-weight: 600;">{{ error }}</p>
    </div>

    <div v-if="analyzing" class="loader"></div>

    <div v-if="metrics && !analyzing">
      <!-- Performance summary cards -->
      <div class="grid-3 mb-24">
        <div class="card">
          <p class="metric-label">Total Return</p>
          <p class="metric-value" :class="metrics.total_return >= 0 ? 'positive' : 'negative'">
            {{ (metrics.total_return * 100).toFixed(2) }}%
          </p>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Entire period</p>
        </div>
        <div class="card">
          <p class="metric-label">Annualized Sharpe Ratio</p>
          <p class="metric-value">{{ metrics.sharpe_ratio.toFixed(2) }}</p>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Rf = 5.0%</p>
        </div>
        <div class="card">
          <p class="metric-label">Maximum Drawdown</p>
          <p class="metric-value negative">{{ (metrics.max_drawdown * 100).toFixed(2) }}%</p>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Duration: {{ metrics.max_drawdown_duration_days || 'N/A' }} days</p>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid-2 mb-24">
        <div class="card">
          <h3>Adjusted Price History (USD)</h3>
          <DataChart v-if="priceChartData" type="line" :data="priceChartData" :options="chartOptions" />
        </div>
        <div class="card">
          <h3>Cumulative Return Growth</h3>
          <DataChart v-if="returnsChartData" type="line" :data="returnsChartData" :options="chartOptions" />
        </div>
      </div>

      <div class="grid-2 mb-24">
        <div class="card">
          <h3>Drawdown Series (%)</h3>
          <DataChart v-if="drawdownChartData" type="line" :data="drawdownChartData" :options="drawdownChartOptions" />
        </div>
        <div class="card">
          <h3>Rolling Volatility (21-Day Annualized)</h3>
          <DataChart v-if="volChartData" type="line" :data="volChartData" :options="chartOptions" />
        </div>
      </div>

      <!-- Detail Metrics Tables -->
      <div class="card">
        <h3 class="mb-24">Detailed Asset Statistics</h3>
        <div class="grid-2">
          <div>
            <h4 class="mb-24">Performance Ratios & Returns</h4>
            <div class="table-container">
              <table>
                <tbody>
                  <tr>
                    <td>Compound Annual Growth Rate (CAGR)</td>
                    <td class="text-right" style="font-weight: 700;">{{ (metrics.cagr * 100).toFixed(2) }}%</td>
                  </tr>
                  <tr>
                    <td>Annualized Mean Return</td>
                    <td class="text-right" style="font-weight: 700;">{{ (metrics.annualized_return * 100).toFixed(2) }}%</td>
                  </tr>
                  <tr>
                    <td>Sortino Ratio</td>
                    <td class="text-right" style="font-weight: 700;">{{ metrics.sortino_ratio.toFixed(2) }}</td>
                  </tr>
                  <tr>
                    <td>Calmar Ratio</td>
                    <td class="text-right" style="font-weight: 700;">{{ metrics.calmar_ratio.toFixed(2) }}</td>
                  </tr>
                  <tr>
                    <td>Best Daily Return</td>
                    <td class="text-right positive-text" style="font-weight: 700;">
                      +{{ (metrics.best_daily_return * 100).toFixed(2) }}% ({{ metrics.best_daily_return_date }})
                    </td>
                  </tr>
                  <tr>
                    <td>Worst Daily Return</td>
                    <td class="text-right negative-text" style="font-weight: 700;">
                      {{ (metrics.worst_daily_return * 100).toFixed(2) }}% ({{ metrics.worst_daily_return_date }})
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <h4 class="mb-24">Risk & Distribution Analytics</h4>
            <div class="table-container">
              <table>
                <tbody>
                  <tr>
                    <td>Annualized Volatility</td>
                    <td class="text-right" style="font-weight: 700;">{{ (metrics.annualized_volatility * 100).toFixed(2) }}%</td>
                  </tr>
                  <tr>
                    <td>Downside Deviation (Semi-Vol)</td>
                    <td class="text-right" style="font-weight: 700;">{{ (metrics.downside_deviation * 100).toFixed(2) }}%</td>
                  </tr>
                  <tr>
                    <td>Skewness (Asymmetry)</td>
                    <td class="text-right" style="font-weight: 700;">{{ metrics.skewness.toFixed(3) }}</td>
                  </tr>
                  <tr>
                    <td>Kurtosis (Fat Tails)</td>
                    <td class="text-right" style="font-weight: 700;">{{ metrics.kurtosis.toFixed(3) }}</td>
                  </tr>
                  <tr>
                    <td>Benchmark Beta (vs SPY)</td>
                    <td class="text-right" style="font-weight: 700;">{{ metrics.beta ? metrics.beta.toFixed(2) : 'N/A' }}</td>
                  </tr>
                  <tr>
                    <td>Benchmark Alpha (Annualized)</td>
                    <td class="text-right" style="font-weight: 700;">{{ metrics.alpha ? (metrics.alpha * 100).toFixed(2) + '%' : 'N/A' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import { assetsApi } from '../api';
import DataChart from '../components/DataChart.vue';

export default {
  name: 'AssetAnalyzer',
  components: { DataChart },
  setup() {
    const filters = ref({
      symbol: 'SPY',
      startDate: '2015-01-01',
      endDate: '2025-01-01',
      interval: '1d',
    });

    const analyzing = ref(false);
    const metrics = ref(null);
    const error = ref(null);

    // Chart Data Refs
    const priceChartData = ref(null);
    const returnsChartData = ref(null);
    const drawdownChartData = ref(null);
    const volChartData = ref(null);

    const chartOptions = {
      plugins: {
        legend: { display: false },
      },
      elements: {
        point: { radius: 0 },
        line: { borderWidth: 1.5 },
      },
    };

    const drawdownChartOptions = {
      ...chartOptions,
      scales: {
        y: {
          ticks: {
            callback: function(value) {
              return (value * 100).toFixed(0) + '%';
            },
            color: '#9ca3af',
          },
          grid: { color: '#24272f' },
        },
        x: { grid: { display: false }, ticks: { color: '#9ca3af' } },
      },
    };

    const runAnalysis = async () => {
      analyzing.value = true;
      error.value = null;
      try {
        const [metricsRes, returnsRes, ddRes, volRes, priceRes] = await Promise.all([
          assetsApi.getMetrics(filters.value.symbol, filters.value.startDate, filters.value.endDate, filters.value.interval),
          assetsApi.getReturns(filters.value.symbol, filters.value.startDate, filters.value.endDate, filters.value.interval),
          assetsApi.getDrawdown(filters.value.symbol, filters.value.startDate, filters.value.endDate, filters.value.interval),
          assetsApi.getRollingVol(filters.value.symbol, 21, filters.value.startDate, filters.value.endDate, filters.value.interval),
          assetsApi.getPrice(filters.value.symbol, filters.value.startDate, filters.value.endDate, filters.value.interval),
        ]);

        metrics.value = metricsRes.data;

        // Populate Chart Data structures
        priceChartData.value = {
          labels: priceRes.data.dates,
          datasets: [{
            label: 'Adjusted Close ($)',
            data: priceRes.data.prices,
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            fill: true,
          }],
        };

        returnsChartData.value = {
          labels: returnsRes.data.dates,
          datasets: [{
            label: 'Cumulative Compounded Growth',
            data: returnsRes.data.cumulative_returns,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.05)',
            fill: true,
          }],
        };

        drawdownChartData.value = {
          labels: ddRes.data.dates,
          datasets: [{
            label: 'Drawdown (%)',
            data: ddRes.data.drawdown,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            fill: true,
          }],
        };

        volChartData.value = {
          labels: volRes.data.dates,
          datasets: [{
            label: '21-Day Volatility',
            data: volRes.data.rolling_volatility,
            borderColor: '#f59e0b',
            fill: false,
          }],
        };

      } catch (err) {
        error.value = 'Failed to analyze ticker. Ensure it exists in database and range is correct. Info: ' + (err.response?.data?.detail || err.message);
        metrics.value = null;
      } finally {
        analyzing.value = false;
      }
    };

    onMounted(() => {
      runAnalysis();
    });

    return {
      filters,
      analyzing,
      metrics,
      error,
      priceChartData,
      returnsChartData,
      drawdownChartData,
      volChartData,
      chartOptions,
      drawdownChartOptions,
      runAnalysis,
    };
  },
};
</script>
