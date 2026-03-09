<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
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
import { externalTooltipHandler, hiddenCanvasTooltip } from '@/utils/chartTooltip'
import CountryYearToYearHeatmap from '@/components/charts/CountryYearToYearHeatmap.vue'
import RegionalMap from '@/components/maps/RegionalMap.vue'
import AppSelect from '@/components/filters/AppSelect.vue'
import { getCountryInsights } from '@/data/insights'

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
const hasRegionalData = ref(false)

const countryInsights = computed(() => getCountryInsights(countryCode.value))

const categoryColors = {
  declining: '#1a9850',
  rising: '#d73027',
  shift: '#4575b4',
  context: '#8856a7'
}

const showCrimeDropdown = ref(false)
const crimeSearch = ref('')

const filteredCrimes = computed(() => {
  if (!crimesMetadata.value) return []
  if (!crimeSearch.value) return crimesMetadata.value
  const search = crimeSearch.value.toLowerCase()
  return crimesMetadata.value.filter(crime =>
    getCrimeName(crime).toLowerCase().includes(search)
  )
})

const selectedCrimeName = computed(() => {
  if (!crimesMetadata.value) return ''
  const crime = crimesMetadata.value.find(c => c.code === filtersStore.selectedCrimeType)
  return crime ? getCrimeName(crime) : ''
})

const selectCrime = (code) => {
  filtersStore.setCrimeType(code)
  showCrimeDropdown.value = false
  crimeSearch.value = ''
}

const handleClickOutside = (e) => {
  if (!e.target.closest('.crime-dropdown-wrapper')) {
    showCrimeDropdown.value = false
  }
}

const countryName = computed(() => {
  if (!countriesMetadata.value) return countryCode.value
  const country = countriesMetadata.value.find(c => c.code === countryCode.value)
  return country ? getTranslatedCountryName(country) : countryCode.value
})

const yearOptions = computed(() => filtersStore.years.map(y => ({ value: y, label: String(y) })))
const onYearChange = (val) => filtersStore.setYear(Number(val))

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
  animation: { duration: 0 },
  plugins: {
    legend: { display: false },
    tooltip: {
      enabled: true,
      ...hiddenCanvasTooltip,
      external: externalTooltipHandler,
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
  },
  interaction: { mode: 'index', axis: 'y', intersect: false },
  hover: { animationDuration: 0 }
}))

const trendChartData = computed(() => {
  if (!crimeData.value) return { labels: [], datasets: [] }

  const countryValues = filtersStore.years.map(year => getCountryValue(filtersStore.selectedCrimeType, year))
  const europeValues = filtersStore.years.map(year => calculateEuropeAverage(filtersStore.selectedCrimeType, year))

  return {
    labels: filtersStore.years.map(String),
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
  animation: { duration: 0 },
  plugins: {
    legend: { position: 'top' },
    tooltip: {
      enabled: true,
      ...hiddenCanvasTooltip,
      external: externalTooltipHandler,
      callbacks: {
        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y?.toFixed(2) ?? 'No data'} per 100k`
      }
    }
  },
  scales: {
    x: { type: 'category', grid: { display: false } },
    y: { beginAtZero: true, grid: { color: '#e2e8f0' } }
  },
  interaction: { mode: 'index', axis: 'x', intersect: false },
  hover: { animationDuration: 0 }
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
        pointBackgroundColor: '#d73027',
        pointRadius: 4,
        pointHitRadius: 20
      },
      {
        label: t('common.europeanAverage'),
        data: topCrimesForRadar.value.map(() => 1),
        backgroundColor: 'rgba(69, 117, 180, 0.1)',
        borderColor: '#4575b4',
        borderDash: [5, 5],
        pointRadius: 0,
        pointHitRadius: 0
      }
    ]
  }
})

const radarChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 0 },
  plugins: {
    legend: { position: 'top' },
    tooltip: {
      enabled: true,
      ...hiddenCanvasTooltip,
      external: externalTooltipHandler,
      callbacks: {
        title: (ctx) => getCrimeName(topCrimesForRadar.value[ctx[0].dataIndex]) || '',
        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.r?.toFixed(2) ?? '—'}x`
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
  },
  interaction: { mode: 'nearestByAngle', intersect: false },
  hover: { animationDuration: 0 }
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

const activeLegendCodes = computed(() => {
  const codesInChart = new Set(crimeOfTheYear.value.map(c => c.code))
  return crimeCodesWithColors.filter(code => codesInChart.has(code))
})

const crimeOfYearChartData = computed(() => {
  if (!crimeOfTheYear.value.length) return { labels: [], datasets: [] }

  return {
    labels: crimeOfTheYear.value.map(c => String(c.year)),
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
  animation: { duration: 0 },
  plugins: {
    legend: { display: false },
    tooltip: {
      enabled: true,
      ...hiddenCanvasTooltip,
      external: externalTooltipHandler,
      callbacks: {
        title: (ctx) => `${t('common.year')} ${crimeOfTheYear.value[ctx[0].dataIndex]?.year}`,
        label: (ctx) => {
          const entry = crimeOfTheYear.value[ctx.dataIndex]
          const crime = crimesMetadata.value?.find(c => c.code === entry?.code)
          const crimeName = crime ? getCrimeName(crime) : entry?.crime
          return [`${t('filters.crimeType')}: ${crimeName}`, `${t('country.rateHeader')}: ${entry?.value?.toFixed(2)}`]
        }
      }
    }
  },
  scales: {
    x: { type: 'category', grid: { display: false } },
    y: { beginAtZero: true, grid: { color: '#e2e8f0' } }
  },
  interaction: { mode: 'index', axis: 'x', intersect: false },
  hover: { animationDuration: 0 }
}))

const hasData = computed(() => {
  if (!crimeData.value || !crimesMetadata.value) return false
  return crimesMetadata.value.some(crime => {
    return filtersStore.years.some(year => {
      const val = getCountryValue(crime.code, year)
      return val !== null
    })
  })
})

const hasSelectedYearData = computed(() => {
  if (!crimeData.value || !crimesMetadata.value) return false
  return crimesMetadata.value.some(crime => {
    const val = getCountryValue(crime.code, filtersStore.selectedYear)
    return val !== null
  })
})

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
  document.addEventListener('click', handleClickOutside)
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

    try {
      const manifestRes = await fetch(`${base}data/regions/manifest.json`)
      if (manifestRes.ok) {
        const manifest = await manifestRes.json()
        hasRegionalData.value = manifest.includes(countryCode.value)
      }
    } catch (e) {}
  } catch (err) {
    console.error('Error loading data:', err)
    loading.value = false
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
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
            <AppSelect
              :modelValue="filtersStore.selectedYear"
              @update:modelValue="onYearChange"
              :options="yearOptions"
            />
          </div>
        </div>
        <p class="subtitle">{{ t('country.subtitle') }}</p>
        <hr class="header-divider" />
      </header>

      <div v-if="!hasData" class="no-data-message">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <h2>{{ t('common.noData') }}</h2>
        <p>{{ t('country.noDataDesc', { country: countryName }) }}</p>
        <router-link to="/" class="back-btn">← {{ t('common.backToMap') }}</router-link>
      </div>

      <template v-else>

      <div v-if="countryInsights.length" class="country-insights">
        <div class="insights-disclaimer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>{{ t('insights.countryNote') }}</span>
        </div>
        <div
          v-for="insight in countryInsights"
          :key="insight.id"
          class="country-insight-card"
        >
          <span
            class="insight-badge"
            :style="{ backgroundColor: categoryColors[insight.category] }"
          >
            {{ t(`insights.${insight.category}`) }}
          </span>
          <div class="country-insight-text">
            <h3>{{ t(`insights.${insight.id}.title`) }}</h3>
            <p>{{ t(`insights.${insight.id}.description`) }}</p>
          </div>
        </div>
      </div>

      <div class="content-grid">
        <section v-if="hasRegionalData" class="viz-section full-width">
          <h2>{{ t('country.regionalTitle') }}</h2>
          <p class="description">
            {{ t('country.regionalDesc', { country: countryName }) }}
          </p>
          <RegionalMap :countryCode="countryCode" />
        </section>

        <template v-if="hasSelectedYearData">
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
        </template>

        <div v-else class="no-year-data">
          <p>{{ t('country.noYearData', { country: countryName, year: filtersStore.selectedYear }) }}</p>
        </div>

        <hr class="section-divider" />

        <section class="viz-section full-width">
          <h2>{{ t('country.trendTitle') }}</h2>
          <p class="description">
            {{ t('country.trendDesc', { country: countryName }) }}
          </p>
          <div class="crime-selector">
            <label>{{ t('country.selectCrime') }}</label>
            <div class="crime-dropdown-wrapper">
              <button
                class="crime-dropdown-trigger"
                @click.stop="showCrimeDropdown = !showCrimeDropdown"
              >
                <span class="selected-crime">{{ selectedCrimeName }}</span>
                <span class="dropdown-arrow">▼</span>
              </button>
              <div v-if="showCrimeDropdown" class="crime-dropdown">
                <input
                  v-model="crimeSearch"
                  type="text"
                  :placeholder="t('compare.searchPlaceholder')"
                  class="crime-search"
                  @click.stop
                />
                <div class="crime-list">
                  <button
                    v-for="crime in filteredCrimes"
                    :key="crime.code"
                    class="crime-option"
                    :class="{ active: crime.code === filtersStore.selectedCrimeType }"
                    @click="selectCrime(crime.code)"
                  >
                    {{ getCrimeName(crime) }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="chart-container trend-chart">
            <Line :data="trendChartData" :options="trendChartOptions" />
          </div>
        </section>

        <section class="viz-section full-width">
          <h2>{{ t('country.crimeOfYear') }}</h2>
          <p class="description">
            {{ t('country.crimeOfYearDesc', { country: countryName }) }}
          </p>
          <div class="crime-legend">
            <span v-for="code in activeLegendCodes" :key="code" class="legend-item">
              <span class="legend-color" :style="{ backgroundColor: crimeColorsByCode[code] }"></span>
              {{ crimesMetadata?.find(c => c.code === code) ? getCrimeName(crimesMetadata.find(c => c.code === code)) : code }}
            </span>
          </div>
          <div class="chart-container coty-chart">
            <Bar :data="crimeOfYearChartData" :options="crimeOfYearChartOptions" />
          </div>
        </section>

        <section class="viz-section full-width">
          <h2>{{ t('country.yearToYearTitle') }}</h2>
          <p class="description">
            {{ t('country.yearToYearDesc', { country: countryName }) }}
          </p>
          <div class="heatmap-content">
            <CountryYearToYearHeatmap :countryCode="countryCode" />
          </div>
        </section>
      </div>
      </template>
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

.no-data-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  color: #718096;
}

.no-data-message svg {
  color: #cbd5e1;
}

.no-data-message h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
  margin: 0;
}

.no-data-message p {
  max-width: 400px;
  line-height: 1.6;
  margin: 0;
}

.back-btn {
  display: inline-block;
  margin-top: 0.5rem;
  padding: 0.5rem 1.25rem;
  background: #1a1a2e;
  color: white;
  text-decoration: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #2d2d4a;
}

.no-year-data {
  grid-column: 1 / -1;
  text-align: center;
  padding: 2.5rem 1.5rem;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 0.75rem;
  color: #64748b;
  font-size: 0.925rem;
  line-height: 1.6;
}

.no-year-data p {
  margin: 0;
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

.header-divider {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 1rem 0 0;
}

.section-divider {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 0.5rem 0;
  grid-column: 1 / -1;
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


.country-insights {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.insights-disclaimer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #92400e;
}

.insights-disclaimer svg {
  flex-shrink: 0;
  color: #d97706;
}

.country-insight-card {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: white;
  border-radius: 0.75rem;
  padding: 1rem 1.25rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border-left: 3px solid #e2e8f0;
}

.insight-badge {
  flex-shrink: 0;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.65rem;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin-top: 2px;
}

.country-insight-text h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 0.375rem;
}

.country-insight-text p {
  font-size: 0.825rem;
  color: #4a5568;
  line-height: 1.6;
  margin: 0;
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

.heatmap-content {
  overflow-x: auto;
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

.crime-dropdown-wrapper {
  position: relative;
}

.crime-dropdown-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  min-width: 300px;
  max-width: 400px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #1a1a2e;
  cursor: pointer;
  text-align: left;
}

.crime-dropdown-trigger:hover {
  border-color: #4575b4;
}

.selected-crime {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-arrow {
  font-size: 0.625rem;
  color: #718096;
}

.crime-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  min-width: 300px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
  z-index: 100;
  overflow: hidden;
}

.crime-search {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: none;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
  outline: none;
}

.crime-search:focus {
  background: #f8fafc;
}

.crime-list {
  max-height: 200px;
  overflow-y: auto;
}

.crime-option {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: none;
  border: none;
  font-size: 0.8125rem;
  text-align: left;
  cursor: pointer;
  color: #334155;
}

.crime-option:hover {
  background: #f1f5f9;
}

.crime-option.active {
  background: #e0f2fe;
  color: #0369a1;
  font-weight: 500;
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
  .country-page {
    padding: 1rem;
    overflow-x: hidden;
  }

  .country-header h1 {
    font-size: 1.5rem;
  }

  .header-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .year-selector {
    padding: 0;
    background: none;
    border-radius: 0;
    gap: 0.5rem;
  }

  .year-selector label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
  }

  .content-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .viz-section {
    padding: 1rem;
    overflow: hidden;
    max-width: 100%;
  }

  .viz-section h2 {
    font-size: 1rem;
  }

  .chart-container {
    max-width: 100%;
  }

  .chart-container.radar-chart {
    height: 300px;
  }

  .chart-container.coty-chart {
    height: 250px;
  }

  .chart-container.trend-chart {
    height: 280px;
  }

  .table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .data-table {
    min-width: 450px;
  }

  .heatmap-content {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .regional-map {
    height: 280px;
  }

  .crime-selector {
    flex-direction: column;
    align-items: flex-start;
  }

  .crime-dropdown-wrapper {
    width: 100%;
  }

  .crime-dropdown-trigger {
    width: 100%;
    min-width: 0;
    padding: 0.4rem 0.75rem;
    font-size: 0.8rem;
    font-weight: 500;
    border: 1px solid #e2e8f0;
    border-radius: 0.375rem;
  }

  .crime-dropdown-trigger:hover {
    border-color: #4575b4;
  }

  .crime-dropdown {
    width: 100%;
    min-width: 0;
  }

  .crime-legend {
    gap: 0.5rem;
    padding: 0.5rem;
  }

  .legend-item {
    font-size: 0.65rem;
  }

  .country-insight-card {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
