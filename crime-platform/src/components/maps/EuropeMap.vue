<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import { useTranslations } from '@/composables/useTranslations'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  height: {
    type: String,
    default: '500px'
  }
})

const emit = defineEmits(['countryClick', 'countryHover'])

// Expose map methods for parent component
const zoomToCountry = (countryCode) => {
  if (!geoJsonLayer.value || !map.value) return

  geoJsonLayer.value.eachLayer((layer) => {
    const code = layer.feature.properties.id || layer.feature.properties.code
    if (code === countryCode) {
      const bounds = layer.getBounds()
      const center = bounds.getCenter()
      map.value.flyTo(center, 5, {
        duration: 1.2,
        easeLinearity: 0.5
      })
    }
  })
}

const resetZoom = () => {
  if (!map.value) return
  map.value.flyTo([54, 15], 4, {
    duration: 1,
    easeLinearity: 0.5
  })
}

defineExpose({ zoomToCountry, resetZoom })

const { t } = useI18n()
const filtersStore = useFiltersStore()
const { getCountryNameByCode } = useTranslations()

const mapContainer = ref(null)
const map = ref(null)
const geoJsonLayer = ref(null)
const loading = ref(true)
const error = ref(null)

const geoData = ref(null)
const crimeData = ref(null)
const countriesMetadata = ref(null)

const hoverInfo = ref(null)

const getColor = (value, min, max) => {
  if (value === null || value === undefined) return '#cccccc'

  const range = max - min
  const normalized = range > 0 ? (value - min) / range : 0.5

  const colors = [
    '#1a9850',
    '#91cf60',
    '#d9ef8b',
    '#fee08b',
    '#fc8d59',
    '#d73027'
  ]

  const index = Math.min(Math.floor(normalized * (colors.length - 1)), colors.length - 1)
  return colors[index]
}

const getCountryName = (code) => {
  return getCountryNameByCode(code, countriesMetadata.value)
}

const getCrimeValue = (countryCode) => {
  if (!crimeData.value) return null

  const yearData = crimeData.value[filtersStore.selectedYear]
  if (!yearData) return null

  const crimeTypeData = yearData[filtersStore.selectedCrimeType]
  if (!crimeTypeData) return null

  const unitKey = filtersStore.metric === 'per100k' ? 'per100k' : 'absolute'
  return crimeTypeData[unitKey]?.[countryCode] ?? null
}

const getMinMax = () => {
  if (!crimeData.value) return { min: 0, max: 100 }

  const yearData = crimeData.value[filtersStore.selectedYear]
  if (!yearData) return { min: 0, max: 100 }

  const crimeTypeData = yearData[filtersStore.selectedCrimeType]
  if (!crimeTypeData) return { min: 0, max: 100 }

  const unitKey = filtersStore.metric === 'per100k' ? 'per100k' : 'absolute'
  const values = Object.values(crimeTypeData[unitKey] || {}).filter(v => v !== null)

  if (values.length === 0) return { min: 0, max: 100 }

  return {
    min: Math.min(...values),
    max: Math.max(...values)
  }
}

const getFeatureStyle = (feature) => {
  const countryCode = feature.properties.id || feature.properties.code
  const value = getCrimeValue(countryCode)
  const { min, max } = getMinMax()

  return {
    fillColor: getColor(value, min, max),
    weight: 1,
    opacity: 1,
    color: '#ffffff',
    fillOpacity: 0.7
  }
}

const highlightStyle = {
  weight: 2,
  color: '#333',
  fillOpacity: 0.85
}

const onEachFeature = (feature, layer) => {
  const countryCode = feature.properties.id || feature.properties.code
  const countryName = getCountryName(countryCode) || feature.properties.name

  layer.on({
    mouseover: (e) => {
      const layer = e.target
      layer.setStyle(highlightStyle)
      layer.bringToFront()

      const value = getCrimeValue(countryCode)
      const { min, max } = getMinMax()
      const avg = (min + max) / 2

      hoverInfo.value = {
        name: countryName,
        code: countryCode,
        value: value,
        comparison: value !== null && avg > 0
          ? ((value - avg) / avg * 100).toFixed(1)
          : null
      }

      emit('countryHover', { code: countryCode, name: countryName, value })
    },
    mouseout: (e) => {
      geoJsonLayer.value.resetStyle(e.target)
      hoverInfo.value = null
    },
    click: (e) => {
      const value = getCrimeValue(countryCode)
      emit('countryClick', { code: countryCode, name: countryName, value })
    }
  })
}

const updateMapColors = () => {
  if (geoJsonLayer.value) {
    geoJsonLayer.value.setStyle(getFeatureStyle)
  }
}

watch(
  () => [filtersStore.selectedYear, filtersStore.selectedCrimeType, filtersStore.metric],
  () => {
    updateMapColors()
  }
)

onMounted(async () => {
  try {
    loading.value = true

    const base = import.meta.env.BASE_URL
    const [geoResponse, crimeResponse, countriesResponse] = await Promise.all([
      fetch(`${base}data/geo/europe-countries-alt.geojson`),
      fetch(`${base}data/map-data.json`),
      fetch(`${base}data/countries.json`)
    ])

    geoData.value = await geoResponse.json()
    crimeData.value = await crimeResponse.json()
    countriesMetadata.value = await countriesResponse.json()

    const europeBounds = L.latLngBounds(
      L.latLng(34, -12),
      L.latLng(72, 45)
    )

    map.value = L.map(mapContainer.value, {
      center: [54, 15],
      zoom: 4,
      minZoom: 3,
      maxZoom: 8,
      zoomControl: true,
      attributionControl: false,
      maxBounds: europeBounds,
      maxBoundsViscosity: 1.0
    })

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
    }).addTo(map.value)

    geoJsonLayer.value = L.geoJSON(geoData.value, {
      style: getFeatureStyle,
      onEachFeature: onEachFeature
    }).addTo(map.value)

    map.value.fitBounds(geoJsonLayer.value.getBounds(), {
      padding: [20, 20]
    })

    loading.value = false
  } catch (err) {
    console.error('Error loading map data:', err)
    error.value = err.message
    loading.value = false
  }
})
</script>

<template>
  <div class="europe-map-container" :style="{ height }">
    <div v-if="loading" class="map-loading">
      <div class="spinner"></div>
      <p>{{ t('common.loading') }}</p>
    </div>

    <div v-else-if="error" class="map-error">
      <p>{{ t('common.error') }}: {{ error }}</p>
    </div>

    <div ref="mapContainer" class="map-element"></div>

    <div v-if="hoverInfo" class="map-tooltip">
      <strong>{{ hoverInfo.name }}</strong>
      <div v-if="hoverInfo.value !== null" class="tooltip-value">
        {{ hoverInfo.value.toLocaleString() }}
        <span class="tooltip-unit">
          {{ filtersStore.metric === 'per100k' ? t('common.per100k') : '' }}
        </span>
      </div>
      <div v-else class="tooltip-no-data">
        {{ t('common.noData') }}
      </div>
      <div v-if="hoverInfo.comparison !== null" class="tooltip-comparison"
           :class="{ positive: hoverInfo.comparison > 0, negative: hoverInfo.comparison < 0 }">
        {{ hoverInfo.comparison > 0 ? '+' : '' }}{{ hoverInfo.comparison }}% {{ t('common.vsAvg') }}
      </div>
      <div class="tooltip-hint">{{ t('common.clickToExplore') }}</div>
    </div>

    <div class="map-legend">
      <div class="legend-title">{{ t('filters.metric') }}</div>
      <div class="legend-scale">
        <div class="legend-bar"></div>
        <div class="legend-labels">
          <span>{{ t('common.low') }}</span>
          <span>{{ t('common.high') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.europe-map-container {
  position: relative;
  width: 100%;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #f0f4f8;
}

.map-element {
  width: 100%;
  height: 100%;
}

.map-loading,
.map-error {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f7fafc;
  z-index: 1000;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #4fd1c5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.map-tooltip {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: white;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 150px;
}

.map-tooltip strong {
  display: block;
  margin-bottom: 0.25rem;
  color: #1a1a2e;
}

.tooltip-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
}

.tooltip-unit {
  font-size: 0.75rem;
  font-weight: 400;
  color: #718096;
}

.tooltip-no-data {
  color: #a0aec0;
  font-style: italic;
}

.tooltip-comparison {
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.tooltip-comparison.positive {
  color: #e53e3e;
}

.tooltip-comparison.negative {
  color: #38a169;
}

.tooltip-hint {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e2e8f0;
  font-size: 0.75rem;
  color: #1a1a2e;
  font-weight: 600;
  background: #f0f9ff;
  margin: 0.5rem -1rem -0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 0 0 0.5rem 0.5rem;
  text-align: center;
}

.map-legend {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  background: white;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.legend-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.legend-scale {
  width: 120px;
}

.legend-bar {
  height: 10px;
  border-radius: 2px;
  background: linear-gradient(to right, #1a9850, #91cf60, #d9ef8b, #fee08b, #fc8d59, #d73027);
}

.legend-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #718096;
  margin-top: 0.25rem;
}
</style>
