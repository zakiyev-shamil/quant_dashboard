<template>
  <div>
    <div class="header-container">
      <div>
        <h1 class="header-title">Risk Dashboard</h1>
        <p class="header-subtitle">Evaluate portfolio Value at Risk (VaR), Conditional VaR, and stress scenarios</p>
      </div>
    </div>

    <!-- Filters panel -->
    <div class="card mb-24">
      <form @submit.prevent="runRiskAnalysis" class="flex align-center gap-16" style="flex-wrap: wrap;">
        <div class="form-group" style="margin-bottom: 0;">
          <label>Symbol</label>
          <input type="text" v-model="filters.symbol" placeholder="e.g. SPY" required style="width: 120px;" />
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label>Confidence Level</label>
          <select v-model.number="filters.confidence" style="width: 140px;">
            <option :value="0.90">90%</option>
            <option :value="0.95">95%</option>
            <option :value="0.99">99% (Strict)</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label>Start Date</label>
          <input type="date" v-model="filters.startDate" style="width: 160px;" />
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label>End Date</label>
          <input type="date" v-model="filters.endDate" style="width: 160px;" />
        </div>
        <button type="submit" class="btn btn-primary" style="align-self: flex-end;" :disabled="loading">
          {{ loading ? 'Calculating...' : 'Run Risk Analysis' }}
        </button>
      </form>
    </div>

    <div v-if="error" class="card mb-24" style="border-color: var(--accent-danger); background-color: rgba(239, 68, 68, 0.05);">
      <p class="negative-text" style="font-weight: 600;">{{ error }}</p>
    </div>

    <div v-if="loading" class="loader"></div>

    <div v-if="report && !loading" style="display: flex; flex-direction: column; gap: 24px;">
      <!-- Risk Metrics Grid -->
      <div class="grid-3">
        <div class="card" style="border-left: 4px solid var(--accent-danger);">
          <p class="metric-label">Historical VaR ({{ (filters.confidence * 100).toFixed(0) }}%)</p>
          <p class="metric-value negative">{{ (report.var_historical * 100).toFixed(2) }}%</p>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Potential loss limit at this probability</p>
        </div>
        <div class="card" style="border-left: 4px solid var(--accent-danger);">
          <p class="metric-label">Conditional VaR / CVaR</p>
          <p class="metric-value negative">{{ (report.cvar_historical * 100).toFixed(2) }}%</p>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Average loss if VaR is breached</p>
        </div>
        <div class="card" style="border-left: 4px solid var(--accent-warning);">
          <p class="metric-label">Probability of Loss</p>
          <p class="metric-value" style="color: var(--accent-warning);">{{ (report.probability_of_loss * 100).toFixed(1) }}%</p>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Percentage of down trading days</p>
        </div>
      </div>

      <!-- Worst/Best days list -->
      <div class="grid-2">
        <div class="card">
          <h3 class="mb-24 negative-text">⚠️ 5 Worst Historical Return Days</h3>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Daily Return</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(val, idx) in report.worst_5_days" :key="idx">
                  <td>#{{ idx + 1 }}</td>
                  <td style="font-weight: 700;" class="negative-text">{{ (val * 100).toFixed(2) }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <h3 class="mb-24 positive-text">📈 5 Best Historical Return Days</h3>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Daily Return</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(val, idx) in report.best_5_days" :key="idx">
                  <td>#{{ idx + 1 }}</td>
                  <td style="font-weight: 700;" class="positive-text">+{{ (val * 100).toFixed(2) }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Stress test builder -->
      <div class="card">
        <h3>Fixed Shock Stress Simulation</h3>
        <p style="font-size: 14px; color: var(--text-secondary); margin-top: 8px;" class="mb-24">
          Determine the impact of specific market-wide shocks on a portfolio.
        </p>

        <div class="flex gap-16 align-center mb-24" style="flex-wrap: wrap;">
          <div class="form-group" style="margin-bottom: 0;">
            <label>Shock Percentage</label>
            <select v-model.number="stressParams.shock" style="width: 160px;">
              <option :value="-0.05">-5% (Minor Shock)</option>
              <option :value="-0.10">-10% (Correction)</option>
              <option :value="-0.20">-20% (Bear Market)</option>
              <option :value="-0.30">-30% (Severe Crisis)</option>
            </select>
          </div>
          <button @click="runStressTest" class="btn btn-secondary" style="align-self: flex-end;" :disabled="stressing">
            {{ stressing ? 'Stressing...' : 'Simulate Stress' }}
          </button>
        </div>

        <div v-if="stressResult" class="table-container">
          <table>
            <thead>
              <tr>
                <th>Shock Scenario</th>
                <th>Portfolio Loss Impact</th>
                <th>Outcome Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="font-weight: 700;">{{ (stressParams.shock * 100).toFixed(0) }}% Market Shock</td>
                <td style="font-weight: 700;" class="negative-text">
                  {{ (stressResult.portfolio_loss * 100).toFixed(2) }}%
                </td>
                <td>
                  <span v-if="stressResult.portfolio_loss < -0.15" class="badge badge-danger">High Risk</span>
                  <span v-else class="badge badge-warning">Moderate Risk</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="!report && !loading" class="card" style="text-align: center; padding: 60px 0;">
      <p style="color: var(--text-secondary); font-size: 16px;">Specify asset filters on the left and run analysis</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { riskApi } from '../api';

export default {
  name: 'RiskDashboard',
  setup() {
    const filters = ref({
      symbol: 'SPY',
      confidence: 0.95,
      startDate: '2015-01-01',
      endDate: '2025-01-01',
    });

    const stressParams = ref({
      shock: -0.10,
    });

    const loading = ref(false);
    const stressing = ref(false);
    const report = ref(null);
    const stressResult = ref(null);
    const error = ref(null);

    const runRiskAnalysis = async () => {
      loading.value = true;
      error.value = null;
      report.value = null;
      stressResult.value = null;
      try {
        const res = await riskApi.getReport(
          filters.value.symbol.toUpperCase().trim(),
          filters.value.confidence,
          filters.value.startDate,
          filters.value.endDate
        );
        report.value = res.data;
      } catch (err) {
        error.value = 'Failed to fetch risk report. Make sure local data exists. Info: ' + (err.response?.data?.detail || err.message);
      } finally {
        loading.value = false;
      }
    };

    const runStressTest = async () => {
      stressing.value = true;
      try {
        const sym = filters.value.symbol.toUpperCase().trim();
        const res = await riskApi.stressTest(
          [sym],
          [1.0], // single asset at 100% weight
          stressParams.value.shock,
          filters.value.startDate,
          filters.value.endDate
        );
        stressResult.value = res.data;
      } catch (err) {
        alert('Stress test failed: ' + (err.response?.data?.detail || err.message));
      } finally {
        stressing.value = false;
      }
    };

    return {
      filters,
      stressParams,
      loading,
      stressing,
      report,
      stressResult,
      error,
      runRiskAnalysis,
      runStressTest,
    };
  },
};
</script>
