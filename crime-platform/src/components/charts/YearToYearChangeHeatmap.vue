<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTranslations } from '@/composables/useTranslations'

const { t } = useI18n()
const { getCrimeName } = useTranslations()

const loading = ref(true)
const crimeData = ref(null)
const crimesMetadata = ref(null)

const tooltip = ref({
  show: false,
  x: 0,
  y: 0,
  crime: '',
  year: '',
  ratio: null,
  prevValue: null,
  currValue: null
})

const showTooltip = (event, crime, year, ratio, prevValue, currValue) => {
  const rect = event.target.getBoundingClientRect()
  tooltip.value = {
    show: true,
    x: rect.left + rect.width / 2,
    y: rect.top - 10,
    crime,
    year,
    ratio,
    prevValue,
    currValue
  }
}

const hideTooltip = () => {
  tooltip.value.show = false
}

const years = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

const calculateEuropeAverage = (crimeCode, year) => {
  if (!crimeData.value) return null
  const yearData = crimeData.value[year]
  if (!yearData) return null
  const crimeTypeData = yearData[crimeCode]
  if (!crimeTypeData) return null
  const values = Object.values(crimeTypeData.per100k || {}).filter(v => v !== null)
  return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : null
}

const heatmapData = computed(() => {
  if (!crimeData.value || !crimesMetadata.value) {
    return { crimes: [], years: [], matrix: [], values: [] }
  }

  const crimes = crimesMetadata.value.slice(0, 15)
  const matrix = []
  const values = []

  for (const crime of crimes) {
    const row = []
    const valueRow = []

    for (let i = 0; i < years.length; i++) {
      const year = years[i]
      const currAvg = calculateEuropeAverage(crime.code, year)

      if (i === 0) {
        row.push(1)
        valueRow.push({ prev: null, curr: currAvg })
      } else {
        const prevYear = years[i - 1]
        const prevAvg = calculateEuropeAverage(crime.code, prevYear)

        if (currAvg !== null && prevAvg !== null && prevAvg > 0) {
          const ratio = currAvg / prevAvg
          row.push(ratio)
          valueRow.push({ prev: prevAvg, curr: currAvg })
        } else {
          row.push(null)
          valueRow.push({ prev: prevAvg, curr: currAvg })
        }
      }
    }

    matrix.push(row)
    values.push(valueRow)
  }

  return {
    crimes: crimes.map(c => getCrimeName(c)),
    years,
    matrix,
    values
  }
})

const getCellColor = (value) => {
  if (value === null) return '#f0f0f0'
  if (value === 1) return '#ffffff'

  if (value < 0.85) return '#1a9850'
  if (value < 0.95) return '#91cf60'
  if (value < 1.0) return '#d9ef8b'
  if (value <= 1.0) return '#ffffbf'
  if (value < 1.05) return '#fee08b'
  if (value < 1.15) return '#fc8d59'
  return '#d73027'
}

const getTextColor = (value) => {
  if (value === null) return '#999'
  if (value < 0.85 || value > 1.15) return 'white'
  return '#333'
}

const formatRatio = (value) => {
  if (value === null) return '-'
  if (value === 1) return '—'
  const percent = ((value - 1) * 100).toFixed(0)
  return percent > 0 ? `+${percent}%` : `${percent}%`
}

onMounted(async () => {
  try {
    const base = import.meta.env.BASE_URL
    const [crimeRes, crimesRes] = await Promise.all([
      fetch(`${base}data/map-data.json`),
      fetch(`${base}data/crimes.json`)
    ])

    crimeData.value = await crimeRes.json()
    crimesMetadata.value = await crimesRes.json()
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
                v-for="year in heatmapData.years"
                :key="year"
                class="year-header"
              >
                {{ year }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(crime, crimeIdx) in heatmapData.crimes" :key="crimeIdx">
              <td class="crime-label">{{ crime }}</td>
              <td
                v-for="(value, yearIdx) in heatmapData.matrix[crimeIdx]"
                :key="yearIdx"
                class="heatmap-cell"
                :style="{
                  backgroundColor: getCellColor(value),
                  color: getTextColor(value)
                }"
                @mouseenter="showTooltip(
                  $event,
                  crime,
                  heatmapData.years[yearIdx],
                  value,
                  heatmapData.values[crimeIdx][yearIdx].prev,
                  heatmapData.values[crimeIdx][yearIdx].curr
                )"
                @mouseleave="hideTooltip"
              >
                {{ formatRatio(value) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="heatmap-legend">
        <span class="legend-label">{{ t('common.decrease') }}</span>
        <div class="legend-scale">
          <div class="legend-bar"></div>
        </div>
        <span class="legend-label">{{ t('common.increase') }}</span>
      </div>

      <Teleport to="body">
        <div
          v-if="tooltip.show"
          class="heatmap-tooltip"
          :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
        >
          <div class="tooltip-header">
            <span class="tooltip-year">{{ tooltip.year }}</span>
            <span
              class="tooltip-value"
              :class="{ increase: tooltip.ratio > 1, decrease: tooltip.ratio < 1 }"
            >
              {{ tooltip.ratio !== null ? formatRatio(tooltip.ratio) : '—' }}
            </span>
          </div>
          <div class="tooltip-crime">{{ tooltip.crime }}</div>
          <div v-if="tooltip.prevValue !== null" class="tooltip-details">
            {{ tooltip.prevValue?.toFixed(1) }} → {{ tooltip.currValue?.toFixed(1) }} per 100k
          </div>
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
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
}

.heatmap-wrapper {
  overflow: hidden;
}

.heatmap-scroll {
  overflow-x: auto;
}

.heatmap-table {
  border-collapse: collapse;
  width: 100%;
  table-layout: fixed;
}

.crime-header {
  background: #1a1a2e;
  color: white;
  padding: 0.5rem 0.75rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  width: 220px;
  position: sticky;
  left: 0;
  z-index: 1;
}

.year-header {
  background: #1a1a2e;
  color: white;
  padding: 0.5rem 0.25rem;
  text-align: center;
  font-weight: 500;
  font-size: 0.7rem;
  min-width: 50px;
}

.crime-label {
  background: #f8fafc;
  padding: 0.5rem 0.75rem;
  font-weight: 500;
  font-size: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-bottom: 1px solid #e2e8f0;
  width: 220px;
  position: sticky;
  left: 0;
}

.heatmap-cell {
  padding: 0.4rem 0.25rem;
  text-align: center;
  font-size: 0.65rem;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.5);
  cursor: default;
  min-width: 50px;
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
  background: linear-gradient(to right, #1a9850, #91cf60, #d9ef8b, #ffffbf, #fee08b, #fc8d59, #d73027);
}

.heatmap-tooltip {
  position: fixed;
  transform: translate(-50%, -100%);
  background: #1a1a2e;
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 9999;
  pointer-events: none;
  font-size: 0.8rem;
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
  gap: 0.75rem;
  margin-bottom: 0.25rem;
}

.tooltip-year {
  font-weight: 600;
}

.tooltip-value {
  font-weight: 700;
}

.tooltip-value.increase {
  color: #fc8d59;
}

.tooltip-value.decrease {
  color: #91cf60;
}

.tooltip-crime {
  font-size: 0.7rem;
  color: #a0aec0;
}

.tooltip-details {
  font-size: 0.65rem;
  color: #718096;
  margin-top: 0.25rem;
}
</style>
