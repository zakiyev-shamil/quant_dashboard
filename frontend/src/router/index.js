import { createRouter, createWebHistory } from 'vue-router';
import Home from '../pages/Home.vue';
import AssetAnalyzer from '../pages/AssetAnalyzer.vue';
import PortfolioAnalyzer from '../pages/PortfolioAnalyzer.vue';
import PortfolioOptimizer from '../pages/PortfolioOptimizer.vue';
import Backtester from '../pages/Backtester.vue';
import RiskDashboard from '../pages/RiskDashboard.vue';
import DataManager from '../pages/DataManager.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/asset-analyzer', name: 'AssetAnalyzer', component: AssetAnalyzer },
  { path: '/portfolio-analyzer', name: 'PortfolioAnalyzer', component: PortfolioAnalyzer },
  { path: '/portfolio-optimizer', name: 'PortfolioOptimizer', component: PortfolioOptimizer },
  { path: '/backtester', name: 'Backtester', component: Backtester },
  { path: '/risk-dashboard', name: 'RiskDashboard', component: RiskDashboard },
  { path: '/data-manager', name: 'DataManager', component: DataManager },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
