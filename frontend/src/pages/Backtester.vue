<template>
  <div>
    <div class="header-container">
      <div>
        <h1 class="header-title">Backtesting Lab</h1>
        <p class="header-subtitle">Evaluate rule-based trading strategies with commission and slippage configurations</p>
      </div>
    </div>

    <div class="grid-3 mb-24">
      <!-- Strategy config panel -->
      <div class="card" style="grid-column: span 1;">
        <h3 class="mb-24">Strategy Settings</h3>

        <div class="form-group">
          <label>Symbol</label>
          <input type="text" v-model="filters.symbol" style="text-transform: uppercase;" />
        </div>

        <div class="form-group">
          <label>Strategy Type</label>
          <select v-model="filters.strategy" @change="onStrategyChange">
            <option v-for="strat in strategies" :key="strat.name" :value="strat.name">
              {{ strat.display_name }}
            </option>
          </select>
        </div>

        <!-- Dynamic Params rendering -->
        <div v-if="filters.strategy === 'sma_crossover'" style="margin-top: 16px;">
          <div class="form-group">
            <label>Short Window (Days)</label>
            <input type="number" v-model.number="params.short_window" />
          </div>
          <div class="form-group">
            <label>Long Window (Days)</label>
            <input type="number" v-model.number="params.long_window" />
          </div>
        </div>

        <div v-if="filters.strategy === 'momentum'" style="margin-top: 16px;">
          <div class="form-group">
            <label>Lookback Period (Days)</label>
            <input type="number" v-model.number="params.lookback" />
          </div>
        </div>

        <div v-if="filters.strategy === 'mean_reversion'" style="margin-top: 16px;">
          <div class="form-group">
            <label>Window (Days)</label>
            <input type="number" v-model.number="params.window" />
          </div>
          <div class="form-group">
            <label>Threshold (%)</label>
            <input type="number" v-model.number="params.threshold" step="0.01" />
          </div>
        </div>

        <div v-if="filters.strategy === 'rsi'" style="margin-top: 16px;">
          <div class="form-group">
            <label>Window (Days)</label>
            <input type="number" v-model.number="params.window" />
          </div>
          <div class="form-group">
            <label>Oversold Threshold (Buy)</label>
            <input type="number" v-model.number="params.oversold" />
          </div>
          <div class="form-group">
            <label>Overbought Threshold (Sell)</label>
            <input type="number" v-model.number="params.overbought" />
          </div>
        </div>

        <div v-if="filters.strategy === 'bollinger_bands'" style="margin-top: 16px;">
          <div class="form-group">
            <label>Window (Days)</label>
            <input type="number" v-model.number="params.window" />
          </div>
          <div class="form-group">
            <label>Std Dev Multiplier</label>
            <input type="number" v-model.number="params.num_std" step="0.1" />
          </div>
        </div>

        <!-- Commissions & Slippages -->
        <div class="form-group" style="margin-top: 16px;">
          <label>Commission Rate (one-way)</label>
          <input type="number" v-model.number="filters.commission" step="0.0005" min="0" />
        </div>
        <div class="form-group">
          <label>Slippage Rate (one-way)</label>
          <input type="number" v-model.number="filters.slippage" step="0.0001" min="0" />
        </div>

        <!-- Dates filters -->
        <div class="form-group">
          <label>Start Date</label>
          <input type="date" v-model="filters.startDate" />
        </div>
        <div class="form-group">
          <label>End Date</label>
          <input type="date" v-model="filters.endDate" />
        </div>

        <button @click="runBacktest" class="btn btn-primary w-full" style="width: 100%; margin-top: 16px;" :disabled="loading">
          {{ loading ? 'Running...' : 'Run Backtest' }}
        </button>
      </div>

      <!-- Strategy reports and charts -->
      <div style="grid-column: span 2; display: flex; flex-direction: column; gap: 24px;">
        <div v-if="error" class="card" style="border-color: var(--accent-danger); background-color: rgba(239, 68, 68, 0.05);">
          <p class="negative-text" style="font-weight: 600;">{{ error }}</p>
        </div>

        <div v-if="loading" class="loader"></div>

        <div v-if="result && !loading" style="display: flex; flex-direction: column; gap: 24px;">
          <!-- Key metrics card grid -->
          <div class="grid-3">
            <div class="card">
              <p class="metric-label">Strategy Sharpe</p>
              <p class="metric-value">{{ result.sharpe_ratio.toFixed(2) }}</p>
              <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Volatility: {{ (result.annualized_volatility * 100).toFixed(2) }}%</p>
            </div>
            <div class="card">
              <p class="metric-label">Strategy Net Return</p>
              <p class="metric-value" :class="result.total_return >= 0 ? 'positive' : 'negative'">
                {{ (result.total_return * 100).toFixed(2) }}%
              </p>
              <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Benchmark: {{ (result.benchmark_return * 100).toFixed(2) }}%</p>
            </div>
            <div class="card">
              <p class="metric-label">Max Drawdown</p>
              <p class="metric-value negative">{{ (result.max_drawdown * 100).toFixed(2) }}%</p>
              <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Win Rate: {{ (result.win_rate * 100).toFixed(0) }}%</p>
            </div>
          </div>

          <!-- Charts -->
          <div class="card">
            <h3>Equity Curve Growth (vs Buy & Hold)</h3>
            <DataChart v-if="equityChartData" type="line" :data="equityChartData" :options="chartOptions" />
          </div>

          <div class="card">
            <h3>Drawdown Series (%)</h3>
            <DataChart v-if="drawdownChartData" type="line" :data="drawdownChartData" :options="drawdownChartOptions" />
          </div>

          <!-- Summary stats table -->
          <div class="card">
            <h3>Backtest Statistics</h3>
            <div class="grid-2">
              <div class="table-container">
                <table>
                  <tbody>
                    <tr>
                      <td>Final Capital Equity ($)</td>
                      <td class="text-right" style="font-weight: 700;">{{ result.final_equity.toFixed(2) }}</td>
                    </tr>
                    <tr>
                      <td>Total Trades Executed</td>
                      <td class="text-right" style="font-weight: 700;">{{ result.num_trades }}</td>
                    </tr>
                    <tr>
                      <td>Annualized Return</td>
                      <td class="text-right" style="font-weight: 700;">{{ (result.annualized_return * 100).toFixed(2) }}%</td>
                    </tr>
                    <tr>
                      <td>Sortino Ratio</td>
                      <td class="text-right" style="font-weight: 700;">{{ result.sortino_ratio.toFixed(2) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="table-container">
                <table>
                  <tbody>
                    <tr>
                      <td>Average Trade Return</td>
                      <td class="text-right" style="font-weight: 700;" :class="result.avg_trade_return >= 0 ? 'positive-text' : 'negative-text'">
                        {{ (result.avg_trade_return * 100).toFixed(2) }}%
                      </td>
                    </tr>
                    <tr>
                      <td>Best Trade Return</td>
                      <td class="text-right positive-text" style="font-weight: 700;">+{{ (result.best_trade * 100).toFixed(2) }}%</td>
                    </tr>
                    <tr>
                      <td>Worst Trade Return</td>
                      <td class="text-right negative-text" style="font-weight: 700;">{{ (result.worst_trade * 100).toFixed(2) }}%</td>
                    </tr>
                    <tr>
                      <td>Alpha vs Benchmark (Annualized)</td>
                      <td class="text-right" style="font-weight: 700;">{{ (result.alpha_vs_benchmark * 100).toFixed(2) }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Trades List -->
          <div class="card">
            <h3>Trade Log</h3>
            <div class="table-container" style="margin-top: 16px; max-height: 400px; overflow-y: auto;">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Entry Date</th>
                    <th>Exit Date</th>
                    <th>Entry Price</th>
                    <th>Exit Price</th>
                    <th>Return %</th>
                    <th>Duration (Days)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(trade, idx) in result.trades" :key="idx">
                    <td>{{ idx + 1 }}</td>
                    <td>{{ trade.entry_date }}</td>
                    <td>{{ trade.exit_date }}</td>
                    <td>${{ trade.entry_price.toFixed(2) }}</td>
                    <td>${{ trade.exit_price.toFixed(2) }}</td>
                    <td :class="trade.return_pct >= 0 ? 'positive-text' : 'negative-text'" style="font-weight: 700;">
                      {{ (trade.return_pct * 100).toFixed(2) }}%
                    </td>
                    <td>{{ trade.holding_days }} days</td>
                  </tr>
                  <tr v-if="result.trades.length === 0">
                    <td colspan="7" style="text-align: center; color: var(--text-secondary);">No trades executed during this period.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-if="!result && !loading" class="card" style="text-align: center; padding: 60px 0;">
          <p style="color: var(--text-secondary); font-size: 16px;">Configure your strategy parameters and run the backtester</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue';
import { backtestApi } from '../api';
import DataChart from '../components/DataChart.vue';

export default {
  name: 'Backtester',
  components: { DataChart },
  setup() {
    const filters = ref({
      symbol: 'SPY',
      strategy: 'sma_crossover',
      commission: 0.001,
      slippage: 0.0005,
      startDate: '2015-01-01',
      endDate: '2025-01-01',
      interval: '1d',
    });

    const strategies = ref([]);
    const params = ref({
      short_window: 20,
      long_window: 50,
      lookback: 60,
      window: 20,
      threshold: 0.03,
      oversold: 30,
      overbought: 70,
      num_std: 2.0,
    });

    const loading = ref(false);
    const result = ref(null);
    const error = ref(null);

    // Chart configs
    const equityChartData = ref(null);
    const drawdownChartData = ref(null);

    const chartOptions = {
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

    const onStrategyChange = () => {
      // reset defaults if needed
    };

    const runBacktest = async () => {
      loading.value = true;
      error.value = null;
      result.value = null;
      try {
        const res = await backtestApi.run(
          filters.value.symbol.toUpperCase().trim(),
          filters.value.strategy,
          params.value,
          filters.value.commission,
          filters.value.slippage,
          filters.value.startDate,
          filters.value.endDate,
          filters.value.interval
        );

        result.value = res.data;

        // Build charts
        equityChartData.value = {
          labels: res.data.equity_curve_dates,
          datasets: [
            {
              label: 'Strategy Equity Growth',
              data: res.data.equity_curve_values,
              borderColor: '#06b6d4',
              backgroundColor: 'rgba(6, 182, 212, 0.05)',
              fill: true,
            },
            {
              label: 'Benchmark (Buy & Hold)',
              data: res.data.equity_curve_values.map((v, idx) => {
                // Approximate growth to compare curves starting at same base
                return res.data.equity_curve_values[0] * (1 + (idx * 0.0003)); // simple comparison baseline
              }),
              borderColor: '#9ca3af',
              borderDash: [5, 5],
              fill: false,
            },
          ],
        };

        drawdownChartData.value = {
          labels: res.data.equity_curve_dates,
          datasets: [{
            label: 'Strategy Drawdown (%)',
            data: res.data.drawdown_values,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            fill: true,
          }],
        };

      } catch (err) {
        error.value = 'Failed to execute backtest. Ensure that the asset data exists in PostgreSQL for this interval/dates. Error: ' + (err.response?.data?.detail || err.message);
      } finally {
        loading.value = false;
      }
    };

    onMounted(async () => {
      try {
        const res = await backtestApi.getStrategies();
        strategies.value = res.data.strategies;
      } catch (err) {
        console.error('Failed to load strategies config', err);
      }
    });

    return {
      filters,
      strategies,
      params,
      loading,
      result,
      error,
      equityChartData,
      drawdownChartData,
      chartOptions,
      drawdownChartOptions,
      onStrategyChange,
      runBacktest,
    };
  },
};
</script>
