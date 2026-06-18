<template>
  <div class="chart-container" style="position: relative; width: 100%; height: 350px;">
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<script>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default {
  name: 'DataChart',
  props: {
    type: {
      type: String,
      default: 'line',
    },
    data: {
      type: Object,
      required: true,
    },
    options: {
      type: Object,
      default: () => ({}),
    },
  },
  setup(props) {
    const canvasRef = ref(null);
    let chartInstance = null;

    const buildChart = () => {
      if (chartInstance) {
        chartInstance.destroy();
      }

      if (!canvasRef.value) return;

      const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: {
              color: '#9ca3af',
              font: {
                family: "'Outfit', sans-serif",
              },
            },
          },
        },
        scales: props.type === 'scatter' ? {
          x: {
            grid: { color: '#24272f' },
            ticks: { color: '#9ca3af' },
          },
          y: {
            grid: { color: '#24272f' },
            ticks: { color: '#9ca3af' },
          },
        } : {
          x: {
            grid: { display: false },
            ticks: { color: '#9ca3af' },
          },
          y: {
            grid: { color: '#24272f' },
            ticks: { color: '#9ca3af' },
          },
        },
      };

      const mergedOptions = { ...defaultOptions, ...props.options };

      chartInstance = new Chart(canvasRef.value, {
        type: props.type,
        data: props.data,
        options: mergedOptions,
      });
    };

    onMounted(() => {
      buildChart();
    });

    onBeforeUnmount(() => {
      if (chartInstance) {
        chartInstance.destroy();
      }
    });

    watch(() => props.data, () => {
      buildChart();
    }, { deep: true });

    return {
      canvasRef,
    };
  },
};
</script>

<style scoped>
.chart-container {
  margin-top: 16px;
  background-color: #121418;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #24272f;
}
</style>
