<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTranslations } from '@/composables/useTranslations'

const { t } = useI18n()
const { getCrimeName, getCountryName } = useTranslations()

const loading = ref(true)
const crimeData = ref(null)
const crimesMetadata = ref(null)
const countriesMetadata = ref(null)

const tooltip = ref({
  show: false,
  x: 0,
  y: 0,
  crime: '',
  country: '',
  value: null
})

const getZoom = () => parseFloat(getComputedStyle(document.body).zoom) || 1

const showTooltip = (event, crime, country, value) => {
  const zoom = getZoom()
  tooltip.value = {
    show: true,
    x: event.clientX / zoom,
    y: event.clientY / zoom - 12,
    crime,
    country,
    value
  }
}

const moveTooltip = (event) => {
  if (tooltip.value.show) {
    const zoom = getZoom()
    tooltip.value.x = event.clientX / zoom
    tooltip.value.y = event.clientY / zoom - 12
  }
}

const hideTooltip = () => {
  tooltip.value.show = false
}

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

const calculateCountryAverage = (crimeCode, countryCode) => {
  if (!crimeData.value) return null

  const recentYears = [2019, 2020, 2021, 2022, 2023]
  let total = 0
  let count = 0

  for (const year of recentYears) {
    const yearData = crimeData.value[year]
    if (!yearData) continue

    const crimeTypeData = yearData[crimeCode]
    if (!crimeTypeData) continue

    const value = crimeTypeData.per100k?.[countryCode]
    if (value !== null && value !== undefined) {
      total += value
      count++
    }
  }

  return count > 0 ? total / count : null
}

const heatmapData = computed(() => {
  if (!crimeData.value || !crimesMetadata.value || !countriesMetadata.value) {
    return { crimes: [], countries: [], matrix: [] }
  }

  const crimes = crimesMetadata.value

  const countryCodes = countriesMetadata.value.map(c => c.code)

  const matrix = []

  for (const crime of crimes) {
    const europeAvg = calculateEuropeAverage(crime.code)
    const row = []

    for (const countryCode of countryCodes) {
      const countryAvg = calculateCountryAverage(crime.code, countryCode)

      if (countryAvg === null || europeAvg === 0) {
        row.push(null)
      } else {
        row.push(Math.min(countryAvg / europeAvg, 3))
      }
    }

    matrix.push(row)
  }

  return {
    crimes: crimes.map(c => getCrimeName(c)),
    countries: countryCodes.map(code => {
      const country = countriesMetadata.value.find(c => c.code === code)
      return country ? getCountryName(country) : code
    }),
    countryCodes,
    matrix
  }
})

const getCellColor = (value) => {
  if (value === null) return '#f0f0f0'

  if (value < 0.5) return '#1a9850'
  if (value < 0.75) return '#91cf60'
  if (value < 1.0) return '#d9ef8b'
  if (value < 1.25) return '#fee08b'
  if (value < 1.75) return '#fc8d59'
  if (value < 2.5) return '#d73027'
  return '#a50026'
}

const getTextColor = (value) => {
  if (value === null) return '#999'
  if (value < 0.75 || value > 1.75) return 'white'
  return '#333'
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
    console.error('Error loading heatmap data:', err)
    loading.value = false
  }
})
</script>

<template>
  <div class="heatmap-container">
    <div v-if="loading" class="heatmap-loading">
      <p>{{ t('common.loading') }}</p>
    </div>
    <div v-else class="heatmap-wrapper">
      <div class="heatmap-scroll">
        <table class="heatmap-table">
          <thead>
            <tr>
              <th class="crime-header">{{ t('common.crimeTypeHeader') }}</th>
              <th
                v-for="(country, idx) in heatmapData.countries"
                :key="idx"
                class="country-header"
              >
                {{ country }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(crime, crimeIdx) in heatmapData.crimes" :key="crimeIdx">
              <td class="crime-label">{{ crime }}</td>
              <td
                v-for="(value, countryIdx) in heatmapData.matrix[crimeIdx]"
                :key="countryIdx"
                class="heatmap-cell"
                :style="{
                  backgroundColor: getCellColor(value),
                  color: getTextColor(value)
                }"
                @mouseenter="showTooltip($event, crime, heatmapData.countries[countryIdx], value)"
                @mousemove="moveTooltip($event)"
                @mouseleave="hideTooltip"
              >
                {{ value !== null ? value.toFixed(1) : '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="heatmap-legend">
        <span class="legend-label">{{ t('common.belowAvg') }}</span>
        <div class="legend-scale">
          <div class="legend-bar"></div>
        </div>
        <span class="legend-label">{{ t('common.aboveAvg') }}</span>
      </div>

      <Teleport to="body">
        <div
          v-if="tooltip.show"
          class="heatmap-tooltip"
          :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
        >
          <div class="tooltip-header">
            <span class="tooltip-country">{{ tooltip.country }}</span>
            <span class="tooltip-value" :class="{ 'above-avg': tooltip.value > 1, 'below-avg': tooltip.value < 1 }">
              {{ tooltip.value !== null ? tooltip.value.toFixed(2) + 'x' : '—' }}
            </span>
          </div>
          <div class="tooltip-crime">{{ tooltip.crime }}</div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<style scoped>
.heatmap-container {
  width: 100%;
}

.heatmap-loading {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
}

.heatmap-wrapper {
  overflow: hidden;
}

.heatmap-scroll {
  overflow: visible;
}

.heatmap-table {
  border-collapse: collapse;
  width: 100%;
  table-layout: fixed;
}

.crime-header {
  background: #1a1a2e;
  color: white;
  padding: 0.25rem 0.4rem;
  text-align: left;
  font-size: 0.65rem;
  font-weight: 600;
  width: 160px;
}

.country-header {
  background: #1a1a2e;
  color: white;
  padding: 0.15rem;
  text-align: center;
  font-weight: 500;
  font-size: 0.55rem;
  writing-mode: vertical-lr;
  transform: rotate(180deg);
  height: 90px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.crime-label {
  background: #f8fafc;
  padding: 0.25rem 0.4rem;
  font-weight: 500;
  font-size: 0.65rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-bottom: 1px solid #e2e8f0;
  width: 160px;
}

.heatmap-cell {
  padding: 0.15rem;
  text-align: center;
  font-size: 0.55rem;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.6);
  cursor: default;
  height: 18px;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 0.375rem;
}

.legend-label {
  font-size: 0.75rem;
  color: #4a5568;
}

.legend-scale {
  width: 150px;
}

.legend-bar {
  height: 12px;
  border-radius: 2px;
  background: linear-gradient(to right, #1a9850, #91cf60, #d9ef8b, #fee08b, #fc8d59, #d73027, #a50026);
}

.heatmap-tooltip {
  position: fixed;
  transform: translate(-50%, -100%);
  background: #1a1a2e;
  color: white;
  padding: 0.4rem 0.6rem;
  border-radius: 0.375rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  pointer-events: none;
  font-size: 0.75rem;
  white-space: nowrap;
}

.heatmap-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: #1a1a2e;
}

.tooltip-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.2rem;
}

.tooltip-country {
  font-weight: 600;
  color: #fff;
}

.tooltip-value {
  font-weight: 700;
  color: #fee08b;
}

.tooltip-value.above-avg {
  color: #fc8d59;
}

.tooltip-value.below-avg {
  color: #91cf60;
}

.tooltip-crime {
  font-size: 0.65rem;
  color: #a0aec0;
  max-width: 200px;
  white-space: normal;
  line-height: 1.2;
}
</style>
