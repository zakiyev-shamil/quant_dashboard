<template>
  <div class="app-container">
    <aside class="sidebar">
      <div class="logo-container">
        <span style="font-size: 24px;">🔬</span>
        <span class="logo-text">QuantLab Lite</span>
      </div>
      <nav style="flex-grow: 1;">
        <ul class="nav-links">
          <li>
            <router-link to="/" class="nav-link" exact-active-class="router-link-active">
              <span>🏠</span> Home Dashboard
            </router-link>
          </li>
          <li>
            <router-link to="/asset-analyzer" class="nav-link">
              <span>📈</span> Asset Analyzer
            </router-link>
          </li>
          <li>
            <router-link to="/portfolio-analyzer" class="nav-link">
              <span>💼</span> Portfolio Analyzer
            </router-link>
          </li>
          <li>
            <router-link to="/portfolio-optimizer" class="nav-link">
              <span>⚡</span> Portfolio Optimizer
            </router-link>
          </li>
          <li>
            <router-link to="/backtester" class="nav-link">
              <span>🔬</span> Backtesting Lab
            </router-link>
          </li>
          <li>
            <router-link to="/risk-dashboard" class="nav-link">
              <span>⚠️</span> Risk Dashboard
            </router-link>
          </li>
          <li>
            <router-link to="/data-manager" class="nav-link">
              <span>⚙️</span> Data Manager
            </router-link>
          </li>
        </ul>
      </nav>
      <div style="border-top: 1px solid var(--border-color); padding-top: 16px; font-size: 12px; color: var(--text-muted); text-align: center;">
        v0.6.0 | Open Source Research
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>
