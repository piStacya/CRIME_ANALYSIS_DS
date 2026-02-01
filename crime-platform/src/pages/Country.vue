<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import { Line, Radar, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
)

const route = useRoute()
const { t } = useI18n()
const filtersStore = useFiltersStore()

const loading = ref(true)
const countryCode = computed(() => route.params.code)
const countryData = ref(null)
const crimeData = ref(null)
const crimesMetadata = ref(null)
const countriesMetadata = ref(null)

const countryName = computed(() => {
  if (!countriesMetadata.value) return countryCode.value
  const country = countriesMetadata.value.find(c => c.code === countryCode.value)
  return country ? country.name : countryCode.value
})

const colors = ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850', '#4575b4', '#74add1']

const calculateEuropeAverage = (crimeCode, year) => {
  if (!crimeData.value) return 0
  const yearData = crimeData.value[year]
  if (!yearData) return 0
  const crimeTypeData = yearData[crimeCode]
  if (!crimeTypeData) return 0
  const values = Object.values(crimeTypeData.per100k || {}).filter(v => v !== null)
  return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0
}

const getCountryValue = (crimeCode, year) => {
  if (!crimeData.value) return null
  const yearData = crimeData.value[year]
  if (!yearData) return null
  const crimeTypeData = yearData[crimeCode]
  if (!crimeTypeData) return null
  return crimeTypeData.per100k?.[countryCode.value] ?? null
}

const topCrimes = computed(() => {
  if (!crimesMetadata.value || !crimeData.value) return []

  return crimesMetadata.value
    .map(crime => {
      const value = getCountryValue(crime.code, filtersStore.selectedYear)
      const europeAvg = calculateEuropeAverage(crime.code, filtersStore.selectedYear)
      const indexScore = europeAvg > 0 && value !== null ? Math.min(value / europeAvg, 3.5) : 0
      return { ...crime, value, europeAvg, indexScore }
    })
    .filter(c => c.value !== null)
    .sort((a, b) => b.value - a.value)
    .slice(0, 5)
})

const topCrimesForRadar = computed(() => {
  return [...topCrimes.value].sort((a, b) => b.indexScore - a.indexScore)
})

const chartColors = ['#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850']

const barChartData = computed(() => ({
  labels: topCrimes.value.map(c => {
    const words = c.name.split(' ')
    if (words.length <= 3) return c.name
    const mid = Math.ceil(words.length / 2)
    return [words.slice(0, mid).join(' '), words.slice(mid).join(' ')]
  }),
  datasets: [{
    label: `${countryName.value} (${filtersStore.selectedYear})`,
    data: topCrimes.value.map(c => c.value),
    backgroundColor: chartColors,
    borderRadius: 4
  }]
}))

const barChartOptions = computed(() => ({
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        title: (ctx) => topCrimes.value[ctx[0].dataIndex]?.name || '',
        label: (ctx) => `${ctx.parsed.x.toFixed(2)} per 100k`
      }
    }
  },
  scales: {
    x: { beginAtZero: true, grid: { color: '#e2e8f0' } },
    y: {
      grid: { display: false },
      ticks: {
        font: { size: 11 },
        autoSkip: false
      }
    }
  }
}))

const trendChartData = computed(() => {
  if (!crimeData.value) return { labels: [], datasets: [] }

  const countryValues = filtersStore.years.map(year => getCountryValue(filtersStore.selectedCrimeType, year))
  const europeValues = filtersStore.years.map(year => calculateEuropeAverage(filtersStore.selectedCrimeType, year))

  return {
    labels: filtersStore.years,
    datasets: [
      {
        label: countryName.value,
        data: countryValues,
        borderColor: '#d73027',
        backgroundColor: '#d73027',
        tension: 0.3,
        pointRadius: 4
      },
      {
        label: 'European Average',
        data: europeValues,
        borderColor: '#4575b4',
        backgroundColor: '#4575b4',
        borderDash: [5, 5],
        tension: 0.3,
        pointRadius: 2
      }
    ]
  }
})

const trendChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' },
    tooltip: {
      callbacks: {
        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y?.toFixed(2) ?? 'No data'} per 100k`
      }
    }
  },
  scales: {
    x: { grid: { display: false } },
    y: { beginAtZero: true, grid: { color: '#e2e8f0' } }
  }
}

const radarChartData = computed(() => {
  if (!topCrimesForRadar.value.length) return { labels: [], datasets: [] }

  return {
    labels: topCrimesForRadar.value.map(c => {
      const words = c.name.split(' ')
      if (words.length <= 2) return c.name
      const mid = Math.ceil(words.length / 2)
      return [words.slice(0, mid).join(' '), words.slice(mid).join(' ')]
    }),
    datasets: [
      {
        label: countryName.value,
        data: topCrimesForRadar.value.map(c => c.indexScore),
        backgroundColor: 'rgba(215, 48, 39, 0.2)',
        borderColor: '#d73027',
        borderWidth: 2,
        pointBackgroundColor: '#d73027'
      },
      {
        label: 'European Average',
        data: topCrimesForRadar.value.map(() => 1),
        backgroundColor: 'rgba(69, 117, 180, 0.1)',
        borderColor: '#4575b4',
        borderDash: [5, 5],
        pointRadius: 0
      }
    ]
  }
})

const radarChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' },
    tooltip: {
      callbacks: {
        title: (ctx) => topCrimesForRadar.value[ctx[0].dataIndex]?.name || '',
        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.r.toFixed(2)}x`
      }
    }
  },
  scales: {
    r: {
      beginAtZero: true,
      max: 3.5,
      ticks: { stepSize: 1, callback: (v) => v === 1 ? 'AVG' : `${v}x` },
      pointLabels: {
        font: { size: 10 }
      }
    }
  }
}))

const allCrimesTable = computed(() => {
  if (!crimesMetadata.value || !crimeData.value) return []

  return crimesMetadata.value
    .map(crime => {
      const value = getCountryValue(crime.code, filtersStore.selectedYear)
      const europeAvg = calculateEuropeAverage(crime.code, filtersStore.selectedYear)
      const ratio = europeAvg > 0 && value !== null ? value / europeAvg : null
      return { ...crime, value, europeAvg, ratio }
    })
    .filter(c => c.value !== null)
    .sort((a, b) => b.value - a.value)
})

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
    console.error('Error loading data:', err)
    loading.value = false
  }
})
</script>

<template>
  <div class="country-page">
    <div v-if="loading" class="loading">Loading...</div>

    <template v-else>
      <header class="country-header">
        <router-link to="/" class="back-link">← Back to Map</router-link>
        <div class="header-row">
          <h1>{{ countryName }}</h1>
          <div class="year-selector">
            <label>Year:</label>
            <select :value="filtersStore.selectedYear" @change="filtersStore.setYear(Number($event.target.value))">
              <option v-for="year in filtersStore.years" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
        </div>
        <p class="subtitle">Detailed crime statistics and analysis</p>
      </header>

      <div class="content-grid">
        <section class="viz-section bar-section">
          <h2>Top 5 Most Common Crimes</h2>
          <p class="description">
            The most frequently recorded crime types in {{ countryName }} in {{ filtersStore.selectedYear }},
            measured per 100,000 inhabitants.
          </p>
          <div class="chart-container bar-chart">
            <Bar :data="barChartData" :options="barChartOptions" />
          </div>
        </section>

        <section class="viz-section">
          <h2>Crime Profile vs European Average - {{ filtersStore.selectedYear }}</h2>
          <p class="description">
            How {{ countryName }}'s top 5 crimes compare to the European average.
            Values above 1.0 mean higher than average, below 1.0 means lower.
          </p>
          <div class="chart-container radar-chart">
            <Radar :data="radarChartData" :options="radarChartOptions" />
          </div>
        </section>

        <section class="viz-section full-width">
          <h2>All Crime Types - {{ filtersStore.selectedYear }}</h2>
          <p class="description">
            Complete list of all recorded crime types in {{ countryName }}, showing the rate per 100,000 inhabitants
            and comparison to European average.
          </p>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Crime Type</th>
                  <th>Rate (per 100k)</th>
                  <th>EU Average</th>
                  <th>vs EU</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="crime in allCrimesTable" :key="crime.code">
                  <td>{{ crime.name }}</td>
                  <td>{{ crime.value.toFixed(2) }}</td>
                  <td>{{ crime.europeAvg.toFixed(2) }}</td>
                  <td class="ratio" :class="{ high: crime.ratio > 1.2, low: crime.ratio < 0.8 }">
                    {{ crime.ratio ? (crime.ratio > 1 ? '+' : '') + ((crime.ratio - 1) * 100).toFixed(0) + '%' : '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="viz-section full-width">
          <h2>Crime Trend Over Time</h2>
          <p class="description">
            How the selected crime type has changed in {{ countryName }} from 2008 to 2023,
            compared to the European average.
          </p>
          <div class="crime-selector">
            <label>Select crime type:</label>
            <select :value="filtersStore.selectedCrimeType" @change="filtersStore.setCrimeType($event.target.value)">
              <option v-for="crime in crimesMetadata" :key="crime.code" :value="crime.code">
                {{ crime.name }}
              </option>
            </select>
          </div>
          <div class="chart-container trend-chart">
            <Line :data="trendChartData" :options="trendChartOptions" />
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.country-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.loading {
  text-align: center;
  padding: 4rem;
  color: #718096;
}

.country-header {
  margin-bottom: 2rem;
}

.back-link {
  color: #4575b4;
  text-decoration: none;
  font-size: 0.875rem;
}

.back-link:hover {
  text-decoration: underline;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  margin: 0.5rem 0 0.25rem;
}

.country-header h1 {
  font-size: 2.5rem;
  color: #1a1a2e;
  margin: 0;
}

.subtitle {
  color: #718096;
  margin: 0;
}

.year-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: #f7fafc;
  border-radius: 0.5rem;
}

.year-selector label {
  font-weight: 600;
  color: #4a5568;
  white-space: nowrap;
}

.year-selector select {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 1rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: stretch;
}

.viz-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.viz-section.bar-section {
  display: flex;
  flex-direction: column;
}

.viz-section.bar-section .chart-container {
  flex: 1;
  min-height: 0;
}

.viz-section.full-width {
  grid-column: 1 / -1;
}

.viz-section h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
  margin: 0 0 0.5rem;
}

.description {
  color: #718096;
  font-size: 0.875rem;
  margin: 0 0 1rem;
  line-height: 1.5;
}

.chart-container {
  position: relative;
}

.bar-chart { height: 100%; min-height: 220px; }
.radar-chart { height: 350px; }
.trend-chart { height: 300px; }

.crime-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.crime-selector label {
  font-size: 0.875rem;
  color: #4a5568;
}

.crime-selector select {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  min-width: 250px;
}

.table-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  position: sticky;
  top: 0;
  background: #1a1a2e;
  color: white;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.data-table th:first-child {
  text-align: left;
}

.data-table th:nth-child(2) {
  text-align: right;
  padding-right: 0.5rem;
}

.data-table th:nth-child(3) {
  text-align: right;
  padding-right: 0.8rem;
}

.data-table th:nth-child(4) {
  text-align: right;
  padding-right: 1.2rem;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.data-table td:first-child {
  text-align: left;
}

.data-table td:nth-child(2),
.data-table td:nth-child(3) {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.data-table .ratio {
  text-align: right;
  font-weight: 600;
}

.ratio.high { color: #d73027; }
.ratio.low { color: #1a9850; }

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
