<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import { useTranslations } from '@/composables/useTranslations'
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
const { getCountryName: getTranslatedCountryName, getCrimeName } = useTranslations()

const loading = ref(true)
const countryCode = computed(() => route.params.code)
const countryData = ref(null)
const crimeData = ref(null)
const crimesMetadata = ref(null)
const countriesMetadata = ref(null)

const countryName = computed(() => {
  if (!countriesMetadata.value) return countryCode.value
  const country = countriesMetadata.value.find(c => c.code === countryCode.value)
  return country ? getTranslatedCountryName(country) : countryCode.value
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
    .slice(0, 15)
})

const crimeOfTheYear = computed(() => {
  if (!crimesMetadata.value || !crimeData.value) return []

  return filtersStore.years.map(year => {
    let maxCrime = null
    let maxValue = -1

    for (const crime of crimesMetadata.value) {
      const value = getCountryValue(crime.code, year)
      if (value !== null && value > maxValue) {
        maxValue = value
        maxCrime = { year, crime: crime.name, code: crime.code, value }
      }
    }

    return maxCrime
  }).filter(c => c !== null)
})

const chartColors = ['#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850']

const barChartData = computed(() => ({
  labels: topCrimes.value.map(c => {
    const name = getCrimeName(c)
    const words = name.split(' ')
    if (words.length <= 3) return name
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
        title: (ctx) => getCrimeName(topCrimes.value[ctx[0].dataIndex]) || '',
        label: (ctx) => `${ctx.parsed.x.toFixed(2)} ${t('common.per100k')}`
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
        label: t('common.europeanAverage'),
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
      const name = getCrimeName(c)
      const words = name.split(' ')
      if (words.length <= 2) return name
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
        label: t('common.europeanAverage'),
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
        title: (ctx) => getCrimeName(topCrimesForRadar.value[ctx[0].dataIndex]) || '',
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
        font: { size: 9 }
      }
    }
  }
}))

const crimeColorsByCode = {
  'ICCS0502': '#1a9850',
  'ICCS0501': '#91cf60',
  'ICCS0601': '#d9ef8b',
  'ICCS0701': '#fee08b',
  'ICCS0401': '#fc8d59',
  'ICCS020111': '#d73027',
  'ICCS0301': '#a50026',
  'ICCS0101': '#4575b4'
}

const getColorForCrime = (crimeCode) => {
  return crimeColorsByCode[crimeCode] || '#718096'
}

const crimeCodesWithColors = Object.keys(crimeColorsByCode)

const crimeOfYearChartData = computed(() => {
  if (!crimeOfTheYear.value.length) return { labels: [], datasets: [] }

  return {
    labels: crimeOfTheYear.value.map(c => c.year),
    datasets: [{
      label: t('country.crimeOfYear'),
      data: crimeOfTheYear.value.map(c => c.value),
      backgroundColor: crimeOfTheYear.value.map(c => getColorForCrime(c.code)),
      borderRadius: 4
    }]
  }
})

const crimeOfYearChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        title: (ctx) => `${t('common.year')} ${crimeOfTheYear.value[ctx[0].dataIndex]?.year}`,
        label: (ctx) => {
          const crimeData = crimeOfTheYear.value[ctx.dataIndex]
          const crime = crimesMetadata.value?.find(c => c.code === crimeData?.code)
          const crimeName = crime ? getCrimeName(crime) : crimeData?.crime
          return [`${t('filters.crimeType')}: ${crimeName}`, `${t('country.rateHeader')}: ${crimeData?.value?.toFixed(2)}`]
        }
      }
    }
  },
  scales: {
    x: { grid: { display: false } },
    y: { beginAtZero: true, grid: { color: '#e2e8f0' } }
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
        <router-link to="/" class="back-link">← {{ t('common.backToMap') }}</router-link>
        <div class="header-row">
          <h1>{{ countryName }}</h1>
          <div class="year-selector">
            <label>{{ t('common.year') }}:</label>
            <select :value="filtersStore.selectedYear" @change="filtersStore.setYear(Number($event.target.value))">
              <option v-for="year in filtersStore.years" :key="year" :value="year">{{ year }}</option>
            </select>
          </div>
        </div>
        <p class="subtitle">{{ t('country.subtitle') }}</p>
      </header>

      <div class="content-grid">
        <section class="viz-section bar-section">
          <h2>{{ t('country.topCrimes') }}</h2>
          <p class="description">
            {{ t('country.topCrimesDesc', { country: countryName, year: filtersStore.selectedYear }) }}
          </p>
          <div class="chart-container bar-chart">
            <Bar :data="barChartData" :options="barChartOptions" />
          </div>
        </section>

        <section class="viz-section">
          <h2>{{ t('country.fingerprint') }} - {{ filtersStore.selectedYear }}</h2>
          <p class="description">
            {{ t('country.fingerprintDesc', { country: countryName }) }}
          </p>
          <div class="chart-container radar-chart">
            <Radar :data="radarChartData" :options="radarChartOptions" />
          </div>
        </section>

        <section class="viz-section full-width">
          <h2>{{ t('country.allCrimes') }} - {{ filtersStore.selectedYear }}</h2>
          <p class="description">
            {{ t('country.allCrimesDesc', { country: countryName }) }}
          </p>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>{{ t('compare.crimeType') }}</th>
                  <th>{{ t('country.rateHeader') }}</th>
                  <th>{{ t('compare.euAverage') }}</th>
                  <th>{{ t('country.vsEU') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="crime in allCrimesTable" :key="crime.code">
                  <td>{{ getCrimeName(crime) }}</td>
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
          <h2>{{ t('country.crimeOfYear') }}</h2>
          <p class="description">
            {{ t('country.crimeOfYearDesc', { country: countryName }) }}
          </p>
          <div class="crime-legend">
            <span v-for="code in crimeCodesWithColors" :key="code" class="legend-item">
              <span class="legend-color" :style="{ backgroundColor: crimeColorsByCode[code] }"></span>
              {{ crimesMetadata?.find(c => c.code === code) ? getCrimeName(crimesMetadata.find(c => c.code === code)) : code }}
            </span>
          </div>
          <div class="chart-container coty-chart">
            <Bar :data="crimeOfYearChartData" :options="crimeOfYearChartOptions" />
          </div>
        </section>

        <section class="viz-section full-width">
          <h2>{{ t('country.trendTitle') }}</h2>
          <p class="description">
            {{ t('country.trendDesc', { country: countryName }) }}
          </p>
          <div class="crime-selector">
            <label>{{ t('country.selectCrime') }}</label>
            <select :value="filtersStore.selectedCrimeType" @change="filtersStore.setCrimeType($event.target.value)">
              <option v-for="crime in crimesMetadata" :key="crime.code" :value="crime.code">
                {{ getCrimeName(crime) }}
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
  margin-bottom: 20px;
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
  font-size: 2rem;
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
.radar-chart { height: 400px; }
.trend-chart { height: 300px; }
.coty-chart { height: 280px; }

.crime-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: #4a5568;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

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
