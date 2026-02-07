<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import { useTranslations } from '@/composables/useTranslations'
import { Bar, Radar, Line } from 'vue-chartjs'
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
import CrimeTrendChart from '@/components/charts/CrimeTrendChart.vue'
import { externalTooltipHandler, hiddenCanvasTooltip } from '@/utils/chartTooltip'

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

const { t } = useI18n()
const route = useRoute()
const filtersStore = useFiltersStore()
const { getCountryNameByCode, getCrimeName } = useTranslations()

const loading = ref(true)
const crimeData = ref(null)
const crimesMetadata = ref(null)
const countriesMetadata = ref(null)


const getInitialCountries = () => {
  const queryCountries = route.query.countries
  if (queryCountries) {
    const codes = queryCountries.split(',').filter(c => c.length === 2)
    if (codes.length >= 2) return codes.slice(0, 5)
  }
  return ['EE', 'FI']
}
const selectedCountries = ref(getInitialCountries())
const showCountryPicker = ref(false)
const countrySearch = ref('')
const showCrimeDropdown = ref(false)
const crimeSearch = ref('')

const addCountry = (code) => {
  if (selectedCountries.value.length < 5 && !selectedCountries.value.includes(code)) {
    selectedCountries.value.push(code)
  }
  showCountryPicker.value = false
  countrySearch.value = ''
}

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
  if (!e.target.closest('.add-country-wrapper')) {
    showCountryPicker.value = false
  }
  if (!e.target.closest('.crime-dropdown-wrapper')) {
    showCrimeDropdown.value = false
  }
}

const colors = [
  '#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850',
  '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#313695'
]

const getCountryName = (code) => {
  return getCountryNameByCode(code, countriesMetadata.value)
}

const calculateEuropeAverage = (crimeCode, year) => {
  if (!crimeData.value) return 0
  const yearData = crimeData.value[year]
  if (!yearData) return 0
  const crimeTypeData = yearData[crimeCode]
  if (!crimeTypeData) return 0
  const values = Object.values(crimeTypeData.per100k || {}).filter(v => v !== null)
  return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0
}

const getCountryValue = (countryCode, crimeCode, year) => {
  if (!crimeData.value) return null
  const yearData = crimeData.value[year]
  if (!yearData) return null
  const crimeTypeData = yearData[crimeCode]
  if (!crimeTypeData) return null
  return crimeTypeData.per100k?.[countryCode] ?? null
}


const topCrimesComparison = computed(() => {
  if (!crimesMetadata.value || !crimeData.value || selectedCountries.value.length < 2) return []

  const crimesWithAvg = crimesMetadata.value.map(crime => {
    const values = selectedCountries.value.map(code =>
      getCountryValue(code, crime.code, filtersStore.selectedYear)
    ).filter(v => v !== null)

    const avg = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0
    return { ...crime, avgValue: avg }
  })

  return crimesWithAvg
    .filter(c => c.avgValue > 0)
    .sort((a, b) => b.avgValue - a.avgValue)
    .slice(0, 5)
})


const barChartData = computed(() => {
  if (!topCrimesComparison.value.length) return { labels: [], datasets: [] }

  const labels = topCrimesComparison.value.map(c => {
    const name = getCrimeName(c)
    const words = name.split(' ')
    if (words.length <= 3) return name
    const mid = Math.ceil(words.length / 2)
    return [words.slice(0, mid).join(' '), words.slice(mid).join(' ')]
  })

  const datasets = selectedCountries.value.map((countryCode, index) => ({
    label: getCountryName(countryCode),
    data: topCrimesComparison.value.map(crime =>
      getCountryValue(countryCode, crime.code, filtersStore.selectedYear) ?? 0
    ),
    backgroundColor: colors[index % colors.length],
    borderRadius: 4
  }))

  return { labels, datasets }
})

const barChartOptions = computed(() => ({
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 0 },
  plugins: {
    legend: {
      position: 'top',
      labels: { usePointStyle: true, padding: 15 }
    },
    tooltip: {
      enabled: true,
      ...hiddenCanvasTooltip,
      external: externalTooltipHandler,
      callbacks: {
        title: (ctx) => getCrimeName(topCrimesComparison.value[ctx[0].dataIndex]) || '',
        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.x?.toFixed(2) ?? 'N/A'} ${t('common.per100k')}`
      }
    }
  },
  scales: {
    x: { beginAtZero: true, grid: { color: '#e2e8f0' } },
    y: {
      grid: { display: false },
      ticks: { font: { size: 11 }, autoSkip: false }
    }
  },
  interaction: { mode: 'index', axis: 'y', intersect: false },
  hover: { animationDuration: 0 }
}))


const topCrimesForRadar = computed(() => {
  if (!crimesMetadata.value || !crimeData.value) return []

  const crimesWithIndex = crimesMetadata.value
    .map(crime => {
      const europeAvg = calculateEuropeAverage(crime.code, filtersStore.selectedYear)

      const indices = selectedCountries.value.map(code => {
        const value = getCountryValue(code, crime.code, filtersStore.selectedYear)
        return europeAvg > 0 && value !== null ? value / europeAvg : 0
      }).filter(v => v > 0)
      const avgIndex = indices.length > 0 ? indices.reduce((a, b) => a + b, 0) / indices.length : 0
      return { ...crime, europeAvg, avgIndex }
    })
    .filter(c => c.avgIndex > 0)
    .sort((a, b) => b.avgIndex - a.avgIndex)
    .slice(0, 12)


  if (crimesWithIndex.length < 3) return crimesWithIndex

  const sorted = [...crimesWithIndex].sort((a, b) => a.avgIndex - b.avgIndex)
  const result = []
  let left = 0, right = sorted.length - 1
  let addFromRight = true

  while (left <= right) {
    if (addFromRight) {
      result.push(sorted[right--])
    } else {
      result.push(sorted[left++])
    }
    addFromRight = !addFromRight
  }

  return result
})

const radarChartData = computed(() => {
  if (!topCrimesForRadar.value.length) return { labels: [], datasets: [] }

  const labels = topCrimesForRadar.value.map(c => {
    const name = getCrimeName(c)
    const words = name.split(' ')
    if (words.length <= 2) return name
    const mid = Math.ceil(words.length / 2)
    return [words.slice(0, mid).join(' '), words.slice(mid).join(' ')]
  })

  const datasets = selectedCountries.value.map((countryCode, index) => {
    const data = topCrimesForRadar.value.map(crime => {
      const value = getCountryValue(countryCode, crime.code, filtersStore.selectedYear)
      return crime.europeAvg > 0 && value !== null
        ? Math.min(value / crime.europeAvg, 3.5)
        : 0
    })

    return {
      label: getCountryName(countryCode),
      data,
      backgroundColor: colors[index % colors.length] + '30',
      borderColor: colors[index % colors.length],
      borderWidth: 2,
      pointBackgroundColor: colors[index % colors.length],
      pointRadius: 3,
      pointHitRadius: 20
    }
  })


  datasets.push({
    label: t('compare.euAverage'),
    data: topCrimesForRadar.value.map(() => 1),
    backgroundColor: 'rgba(100, 100, 100, 0.05)',
    borderColor: '#718096',
    borderDash: [5, 5],
    pointRadius: 0,
    pointHitRadius: 0,
    borderWidth: 1
  })

  return { labels, datasets }
})

const radarChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 0 },
  plugins: {
    legend: {
      position: 'top',
      labels: { usePointStyle: true, padding: 15 }
    },
    tooltip: {
      enabled: true,
      ...hiddenCanvasTooltip,
      external: externalTooltipHandler,
      callbacks: {
        title: (ctx) => getCrimeName(topCrimesForRadar.value[ctx[0].dataIndex]) || '',
        label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.r?.toFixed(2) ?? 'N/A'}x ${t('compare.euAverage')}`
      }
    }
  },
  scales: {
    r: {
      beginAtZero: true,
      max: 3.5,
      ticks: {
        stepSize: 1,
        callback: (v) => v === 1 ? 'AVG' : `${v}x`
      },
      pointLabels: { font: { size: 9 } }
    }
  },
  interaction: { mode: 'nearestByAngle', intersect: false },
  hover: { animationDuration: 0 }
}))


const comparisonTableData = computed(() => {
  if (!crimesMetadata.value || !crimeData.value) return []

  return crimesMetadata.value
    .map(crime => {
      const europeAvg = calculateEuropeAverage(crime.code, filtersStore.selectedYear)
      const countryValues = {}

      for (const code of selectedCountries.value) {
        const value = getCountryValue(code, crime.code, filtersStore.selectedYear)
        const ratio = europeAvg > 0 && value !== null ? value / europeAvg : null
        countryValues[code] = { value, ratio }
      }


      const hasData = Object.values(countryValues).some(v => v.value !== null)
      return { ...crime, europeAvg, countryValues, hasData }
    })
    .filter(c => c.hasData)
    .sort((a, b) => {

      const aVal = a.countryValues[selectedCountries.value[0]]?.value ?? 0
      const bVal = b.countryValues[selectedCountries.value[0]]?.value ?? 0
      return bVal - aVal
    })
})

const tableSortColumn = ref(null)
const tableSortAsc = ref(false)

const sortedTableData = computed(() => {
  if (!tableSortColumn.value) return comparisonTableData.value

  return [...comparisonTableData.value].sort((a, b) => {
    let aVal, bVal

    if (tableSortColumn.value === 'name') {
      aVal = a.name
      bVal = b.name
      return tableSortAsc.value ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
    } else if (tableSortColumn.value === 'euAvg') {
      aVal = a.europeAvg
      bVal = b.europeAvg
    } else {
      aVal = a.countryValues[tableSortColumn.value]?.value ?? -1
      bVal = b.countryValues[tableSortColumn.value]?.value ?? -1
    }

    return tableSortAsc.value ? aVal - bVal : bVal - aVal
  })
})

const sortTable = (column) => {
  if (tableSortColumn.value === column) {
    tableSortAsc.value = !tableSortAsc.value
  } else {
    tableSortColumn.value = column
    tableSortAsc.value = false
  }
}

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
  <div class="compare-page">
    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>

    <template v-else>
      <header class="compare-header">
        <h1>{{ t('compare.title') }}</h1>
        <p class="subtitle">{{ t('compare.subtitle') }}</p>
      </header>

      <section class="filters-bar">
        <div class="countries-area">
          <span
            v-for="country in countriesMetadata?.filter(c => selectedCountries.includes(c.code))"
            :key="country.code"
            class="country-tag"
            :style="{ '--tag-color': colors[selectedCountries.indexOf(country.code) % colors.length] }"
          >
            <span class="tag-dot"></span>
            {{ country.name }}
            <button
              v-if="selectedCountries.length > 2"
              @click="selectedCountries = selectedCountries.filter(c => c !== country.code)"
              class="tag-remove"
            >&times;</button>
          </span>
          <div class="add-country-wrapper">
            <button class="add-country-btn" @click.stop="showCountryPicker = !showCountryPicker">
              + {{ t('compare.addCountry') }}
            </button>
            <div v-if="showCountryPicker" class="country-picker">
              <input
                v-model="countrySearch"
                type="text"
                :placeholder="t('compare.searchPlaceholder')"
                class="picker-search"
                @click.stop
              />
              <div class="picker-list">
                <button
                  v-for="country in countriesMetadata?.filter(c =>
                    !selectedCountries.includes(c.code) &&
                    (c.name.toLowerCase().includes(countrySearch.toLowerCase()) || c.code.toLowerCase().includes(countrySearch.toLowerCase()))
                  )"
                  :key="country.code"
                  class="picker-item"
                  :class="{ disabled: selectedCountries.length >= 5 }"
                  @click="addCountry(country.code)"
                >
                  {{ country.name }}
                  <span class="picker-code">{{ country.code }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="year-area">
          <select class="year-dropdown" :value="filtersStore.selectedYear" @change="filtersStore.setYear(Number($event.target.value))">
            <option v-for="year in filtersStore.years" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
      </section>

      <div v-if="selectedCountries.length < 2" class="min-warning">
        {{ t('compare.minCountries') }}
      </div>

      <template v-if="selectedCountries.length >= 2">

        <div class="content-grid">
          <!-- Top Crimes Comparison -->
          <section class="viz-section">
            <h2>{{ t('compare.topCrimes') }}</h2>
            <p class="description">
              {{ t('compare.topCrimesDesc', { year: filtersStore.selectedYear }) }}
            </p>
            <div class="chart-container bar-chart">
              <Bar :data="barChartData" :options="barChartOptions" />
            </div>
          </section>

          <!-- Criminal Fingerprint Comparison -->
          <section class="viz-section">
            <h2>{{ t('compare.fingerprints') }}</h2>
            <p class="description">
              {{ t('compare.fingerprintsDesc') }}
            </p>
            <div class="chart-container radar-chart">
              <Radar :data="radarChartData" :options="radarChartOptions" />
            </div>
          </section>

          <!-- Crime Trend Over Time -->
          <section class="viz-section full-width">
            <h2>{{ t('compare.trends') }}</h2>
            <p class="description">
              {{ t('compare.trendsDesc') }}
            </p>
            <div class="crime-selector">
              <label>{{ t('filters.crimeType') }}:</label>
              <select :value="filtersStore.selectedCrimeType" @change="filtersStore.setCrimeType($event.target.value)">
                <option v-for="crime in crimesMetadata" :key="crime.code" :value="crime.code">
                  {{ getCrimeName(crime) }}
                </option>
              </select>
            </div>
            <div class="chart-container trend-chart">
              <CrimeTrendChart :countries="selectedCountries" />
            </div>
          </section>

          <!-- Comparison Table -->
          <section class="viz-section full-width">
            <h2>{{ t('compare.dataTable') }}</h2>
            <p class="description">
              {{ t('compare.dataTableDesc') }}
            </p>
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th @click="sortTable('name')" class="sortable">
                      {{ t('compare.crimeType') }}
                      <span v-if="tableSortColumn === 'name'" class="sort-indicator">{{ tableSortAsc ? '▲' : '▼' }}</span>
                    </th>
                    <th
                      v-for="code in selectedCountries"
                      :key="code"
                      @click="sortTable(code)"
                      class="sortable country-col"
                      :style="{ borderTopColor: colors[selectedCountries.indexOf(code) % colors.length] }"
                    >
                      {{ getCountryName(code) }}
                      <span v-if="tableSortColumn === code" class="sort-indicator">{{ tableSortAsc ? '▲' : '▼' }}</span>
                    </th>
                    <th @click="sortTable('euAvg')" class="sortable eu-avg-col">
                      {{ t('compare.euAverage') }}
                      <span v-if="tableSortColumn === 'euAvg'" class="sort-indicator">{{ tableSortAsc ? '▲' : '▼' }}</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="crime in sortedTableData" :key="crime.code">
                    <td class="crime-name">{{ getCrimeName(crime) }}</td>
                    <td
                      v-for="code in selectedCountries"
                      :key="code"
                      class="value-cell"
                    >
                      <template v-if="crime.countryValues[code]?.value !== null">
                        <span class="value">{{ crime.countryValues[code].value.toFixed(2) }}</span>
                        <span
                          class="ratio"
                          :class="{
                            high: crime.countryValues[code].ratio > 1.2,
                            low: crime.countryValues[code].ratio < 0.8
                          }"
                        >
                          {{ crime.countryValues[code].ratio > 1 ? '+' : '' }}{{ ((crime.countryValues[code].ratio - 1) * 100).toFixed(0) }}%
                        </span>
                      </template>
                      <span v-else class="no-data">{{ t('compare.noData') }}</span>
                    </td>
                    <td class="eu-avg">{{ crime.europeAvg.toFixed(2) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.compare-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.loading {
  text-align: center;
  padding: 4rem;
  color: #718096;
}

.compare-header {
  margin-bottom: 20px;
}

.compare-header h1 {
  font-size: 2rem;
  color: #1a1a2e;
  margin: 0 0 0.25rem;
}

.subtitle {
  color: #718096;
  margin: 0;
}

.filters-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: white;
  border-radius: 0.5rem;
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.countries-area {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 1;
}

.country-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-left: 3px solid var(--tag-color);
  border-radius: 0.25rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #334155;
  white-space: nowrap;
}

.tag-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--tag-color);
}

.tag-remove {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
  margin-left: 0.25rem;
}

.tag-remove:hover {
  color: #ef4444;
}

.add-country-wrapper {
  position: relative;
}

.add-country-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background: white;
  border: 1px dashed #cbd5e1;
  border-radius: 0.25rem;
  font-size: 0.8125rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
}

.add-country-btn:hover {
  border-color: #4575b4;
  color: #4575b4;
  background: #f8fafc;
}

.country-picker {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  width: 220px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1);
  z-index: 100;
  overflow: hidden;
}

.picker-search {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: none;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.8125rem;
  outline: none;
}

.picker-search:focus {
  background: #f8fafc;
}

.picker-list {
  max-height: 200px;
  overflow-y: auto;
}

.picker-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: none;
  border: none;
  font-size: 0.8125rem;
  text-align: left;
  cursor: pointer;
  color: #334155;
}

.picker-item:hover:not(.disabled) {
  background: #f1f5f9;
}

.picker-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.picker-code {
  font-size: 0.6875rem;
  color: #94a3b8;
  font-family: monospace;
}

.year-area {
  flex-shrink: 0;
}

.year-dropdown {
  padding: 0.375rem 1.75rem 0.375rem 0.75rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #334155;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2364748b' d='M3 4.5L6 7.5L9 4.5'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
}

.year-dropdown:hover {
  border-color: #94a3b8;
}

.year-dropdown:focus {
  outline: none;
  border-color: #4575b4;
}

.min-warning {
  text-align: center;
  padding: 3rem;
  background: #fff5f5;
  border-radius: 0.75rem;
  color: #c53030;
  font-size: 1.125rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.viz-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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

.bar-chart { height: 400px; }
.radar-chart { height: 450px; }
.trend-chart { height: 350px; }

.crime-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.crime-selector label {
  font-size: 0.875rem;
  color: #4a5568;
  font-weight: 600;
}

.crime-selector select {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  min-width: 250px;
}

.table-container {
  max-height: 500px;
  overflow: auto;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.data-table th {
  position: sticky;
  top: 0;
  background: #1a1a2e;
  color: white;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  text-align: left;
  white-space: nowrap;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background: #2d2d4a;
}

.data-table th.country-col {
  border-top: 4px solid;
  text-align: right;
}

.data-table th.eu-avg-col {
  text-align: right;
}

.sort-indicator {
  margin-left: 0.5rem;
  font-size: 0.75rem;
}

.data-table td {
  padding: 0.625rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.875rem;
}

.crime-name {
  font-weight: 500;
}

.value-cell {
  text-align: right;
}

.value {
  font-variant-numeric: tabular-nums;
}

.ratio {
  display: inline-block;
  margin-left: 0.5rem;
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  background: #f0f0f0;
}

.ratio.high {
  background: #fed7d7;
  color: #c53030;
}

.ratio.low {
  background: #c6f6d5;
  color: #276749;
}

.no-data {
  color: #a0aec0;
  font-style: italic;
}

.eu-avg {
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: #718096;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .compare-page {
    padding: 1rem;
  }

  .compare-header h1 {
    font-size: 1.75rem;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .countries-area {
    justify-content: flex-start;
  }

  .year-area {
    align-self: flex-end;
  }
}
</style>
