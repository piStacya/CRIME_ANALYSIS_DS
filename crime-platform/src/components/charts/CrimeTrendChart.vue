<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import { useTranslations } from '@/composables/useTranslations'
import { externalTooltipHandler, hiddenCanvasTooltip } from '@/utils/chartTooltip'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps({
  countries: {
    type: Array,
    default: () => []
  }
})

const { t } = useI18n()
const filtersStore = useFiltersStore()
const { getCountryNameByCode } = useTranslations()

const loading = ref(true)
const crimeData = ref(null)
const countriesMetadata = ref(null)

const colors = [
  '#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850',
  '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#313695'
]

const getCountryName = (code) => {
  return getCountryNameByCode(code, countriesMetadata.value)
}

const getTopCountries = () => {
  if (!crimeData.value) return []

  const countryTotals = {}
  const countryCounts = {}

  for (const year of filtersStore.years) {
    const yearData = crimeData.value[year]
    if (!yearData) continue

    const crimeTypeData = yearData[filtersStore.selectedCrimeType]
    if (!crimeTypeData) continue

    const unitKey = filtersStore.metric === 'per100k' ? 'per100k' : 'absolute'
    const values = crimeTypeData[unitKey] || {}

    for (const [country, value] of Object.entries(values)) {
      if (value !== null) {
        countryTotals[country] = (countryTotals[country] || 0) + value
        countryCounts[country] = (countryCounts[country] || 0) + 1
      }
    }
  }

  const averages = Object.entries(countryTotals)
    .map(([code, total]) => ({
      code,
      avg: total / countryCounts[code]
    }))
    .sort((a, b) => b.avg - a.avg)
    .slice(0, 5)
    .map(c => c.code)

  return averages
}

const chartData = computed(() => {
  if (!crimeData.value) return { labels: [], datasets: [] }

  const selectedCountries = props.countries.length > 0
    ? props.countries
    : getTopCountries()

  const datasets = selectedCountries.map((countryCode, index) => {
    const data = filtersStore.years.map(year => {
      const yearData = crimeData.value[year]
      if (!yearData) return null

      const crimeTypeData = yearData[filtersStore.selectedCrimeType]
      if (!crimeTypeData) return null

      const unitKey = filtersStore.metric === 'per100k' ? 'per100k' : 'absolute'
      return crimeTypeData[unitKey]?.[countryCode] ?? null
    })

    return {
      label: getCountryName(countryCode),
      data,
      borderColor: colors[index % colors.length],
      backgroundColor: colors[index % colors.length],
      tension: 0.3,
      pointRadius: 3,
      pointHoverRadius: 6
    }
  })

  return {
    labels: filtersStore.years.map(String),
    datasets
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 0 },
  plugins: {
    legend: {
      position: 'top',
      labels: {
        usePointStyle: true,
        padding: 20
      }
    },
    tooltip: {
      enabled: true,
      ...hiddenCanvasTooltip,
      external: externalTooltipHandler,
      callbacks: {
        label: (context) => {
          const value = context.parsed.y
          if (value === null) return `${context.dataset.label}: No data`
          const formatted = value.toLocaleString(undefined, { maximumFractionDigits: 2 })
          const unit = filtersStore.metric === 'per100k' ? ' per 100k' : ''
          return `${context.dataset.label}: ${formatted}${unit}`
        }
      }
    }
  },
  scales: {
    x: {
      type: 'category',
      grid: {
        display: false
      }
    },
    y: {
      beginAtZero: true,
      grid: {
        color: '#e2e8f0'
      },
      ticks: {
        callback: (value) => value.toLocaleString()
      }
    }
  },
  interaction: {
    mode: 'index',
    axis: 'x',
    intersect: false
  },
  hover: { animationDuration: 0 }
}))

onMounted(async () => {
  try {
    const base = import.meta.env.BASE_URL
    const [crimeRes, countriesRes] = await Promise.all([
      fetch(`${base}data/map-data.json`),
      fetch(`${base}data/countries.json`)
    ])

    crimeData.value = await crimeRes.json()
    countriesMetadata.value = await countriesRes.json()
    loading.value = false
  } catch (err) {
    console.error('Error loading chart data:', err)
    loading.value = false
  }
})
</script>

<template>
  <div class="crime-trend-chart">
    <div v-if="loading" class="chart-loading">
      <p>{{ t('common.loading') }}</p>
    </div>
    <div v-else class="chart-container">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.crime-trend-chart {
  width: 100%;
}

.chart-loading {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
}

.chart-container {
  height: 350px;
}
</style>
