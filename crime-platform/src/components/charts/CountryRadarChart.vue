<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import { externalTooltipHandler, hiddenCanvasTooltip } from '@/utils/chartTooltip'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

const props = defineProps({
  countryCode: {
    type: String,
    default: 'EE'
  }
})

const { t } = useI18n()
const filtersStore = useFiltersStore()

const loading = ref(true)
const crimeData = ref(null)
const crimesMetadata = ref(null)
const countriesMetadata = ref(null)


const countryName = computed(() => {
  if (!countriesMetadata.value) return props.countryCode
  const country = countriesMetadata.value.find(c => c.code === props.countryCode)
  return country ? country.name : props.countryCode
})


const calculateEuropeAverage = (crimeCode) => {
  if (!crimeData.value) return 0

  const recentYears = [2019, 2020, 2021, 2022, 2023]
  let total = 0
  let count = 0

  for (const year of recentYears) {
    const yearData = crimeData.value[year]
    if (!yearData) continue

    const crimeTypeData = yearData[crimeCode]
    if (!crimeTypeData) continue

    const values = Object.values(crimeTypeData.per100k || {})
    for (const value of values) {
      if (value !== null && value !== undefined) {
        total += value
        count++
      }
    }
  }

  return count > 0 ? total / count : 0
}

const calculateCountryAverage = (crimeCode) => {
  if (!crimeData.value) return 0

  const recentYears = [2019, 2020, 2021, 2022, 2023]
  let total = 0
  let count = 0

  for (const year of recentYears) {
    const yearData = crimeData.value[year]
    if (!yearData) continue

    const crimeTypeData = yearData[crimeCode]
    if (!crimeTypeData) continue

    const value = crimeTypeData.per100k?.[props.countryCode]
    if (value !== null && value !== undefined) {
      total += value
      count++
    }
  }

  return count > 0 ? total / count : null
}

const getTopCrimeTypes = () => {
  if (!crimesMetadata.value || !crimeData.value) return []

  const scores = crimesMetadata.value
    .map(crime => {
      const countryAvg = calculateCountryAverage(crime.code)
      const europeAvg = calculateEuropeAverage(crime.code)

      if (countryAvg === null || europeAvg === 0) return null

      return {
        code: crime.code,
        name: crime.name,
        countryValue: countryAvg,
        europeAvg: europeAvg,
        indexScore: countryAvg / europeAvg
      }
    })
    .filter(s => s !== null)
    .sort((a, b) => b.countryValue - a.countryValue)
    .slice(0, 10)

  return scores
}

const chartData = computed(() => {
  const topCrimes = getTopCrimeTypes()

  if (topCrimes.length === 0) {
    return { labels: [], datasets: [] }
  }


  const cappedScores = topCrimes.map(c => Math.min(c.indexScore, 3.5))

  return {
    labels: topCrimes.map(c => c.name.length > 20 ? c.name.substring(0, 20) + '...' : c.name),
    datasets: [
      {
        label: countryName.value,
        data: cappedScores,
        backgroundColor: 'rgba(215, 48, 39, 0.2)',
        borderColor: '#d73027',
        borderWidth: 2,
        pointBackgroundColor: '#d73027',
        pointRadius: 4,
        pointHitRadius: 20
      },
      {
        label: 'European Average',
        data: topCrimes.map(() => 1),
        backgroundColor: 'rgba(69, 117, 180, 0.1)',
        borderColor: '#4575b4',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 0,
        pointHitRadius: 0
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: {
        usePointStyle: true,
        padding: 15
      }
    },
    tooltip: {
      enabled: true,
      ...hiddenCanvasTooltip,
      external: externalTooltipHandler,
      callbacks: {
        label: (context) => {
          if (context.datasetIndex === 1) return 'European Average: 1.0x'
          const value = context.parsed.r
          return `${context.dataset.label}: ${value?.toFixed(2) ?? '—'}x average`
        }
      }
    }
  },
  interaction: { mode: 'nearestByAngle', intersect: false },
  scales: {
    r: {
      beginAtZero: true,
      max: 3.5,
      ticks: {
        stepSize: 1,
        callback: (value) => value === 1 ? 'AVG' : `${value}x`
      },
      pointLabels: {
        font: {
          size: 10
        }
      },
      grid: {
        color: '#e2e8f0'
      }
    }
  }
}

onMounted(async () => {
  try {
    const base = import.meta.env.BASE_URL
    const [crimeRes, crimesRes, countriesRes] = await Promise.all([
      fetch(`${base}data/map-data.json`),
      fetch(`${base}data/crimes.json`),
      fetch(`${base}data/countries.json`)
    ])

    crimeData.value = await crimeRes.json()
    crimesMetadata.value = await crimesRes.json()
    countriesMetadata.value = await countriesRes.json()
    loading.value = false
  } catch (err) {
    console.error('Error loading radar chart data:', err)
    loading.value = false
  }
})
</script>

<template>
  <div class="country-radar-chart">
    <div v-if="loading" class="chart-loading">
      <p>{{ t('common.loading') }}</p>
    </div>
    <div v-else class="chart-container">
      <Radar :data="chartData" :options="chartOptions" />
    </div>
    <p class="chart-note">
      Values show how many times above/below the European average (1.0 = average)
    </p>
  </div>
</template>

<style scoped>
.country-radar-chart {
  width: 100%;
}

.chart-loading {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
}

.chart-container {
  height: 400px;
}

.chart-note {
  text-align: center;
  font-size: 0.75rem;
  color: #718096;
  margin-top: 0.5rem;
}
</style>
