<script setup>
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  countryCode: { type: String, required: true }
})

const { t } = useI18n()

const mapContainer = ref(null)
const map = ref(null)
const geoJsonLayer = ref(null)
const loading = ref(true)
const noData = ref(false)

const geoData = ref(null)
const regionalData = ref(null)

const hoverInfo = ref(null)

const availableCrimes = [
  { code: 'ICCS0101', key: 'intentionalHomicide' },
  { code: 'ICCS02011', key: 'assault' },
  { code: 'ICCS0401', key: 'robbery' },
  { code: 'ICCS0501', key: 'burglary' },
  { code: 'ICCS05012', key: 'burglaryResidential' },
  { code: 'ICCS0502', key: 'theft' },
  { code: 'ICCS050211', key: 'theftMotorVehicle' }
]

const selectedCrime = ref('ICCS0502')
const selectedYear = ref(2023)

const years = []
for (let y = 2008; y <= 2023; y++) years.push(y)

const filteredCrimes = computed(() => {
  if (!regionalData.value) return []
  return availableCrimes.filter(c => regionalData.value.crimes[c.code])
})

const getColor = (value, min, max) => {
  if (value === null || value === undefined) return '#cccccc'
  const range = max - min
  const normalized = range > 0 ? (value - min) / range : 0.5
  const colors = ['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027']
  const index = Math.min(Math.floor(normalized * (colors.length - 1)), colors.length - 1)
  return colors[index]
}

const getRegionValue = (nutsId) => {
  if (!regionalData.value) return null
  const crimeData = regionalData.value.crimes[selectedCrime.value]
  if (!crimeData) return null
  const regionData = crimeData[nutsId]
  if (!regionData) return null
  return regionData[String(selectedYear.value)] ?? null
}

const getMinMax = () => {
  if (!regionalData.value) return { min: 0, max: 100 }
  const crimeData = regionalData.value.crimes[selectedCrime.value]
  if (!crimeData) return { min: 0, max: 100 }

  const values = []
  for (const nutsId of Object.keys(crimeData)) {
    const val = crimeData[nutsId][String(selectedYear.value)]
    if (val !== null && val !== undefined) values.push(val)
  }

  if (values.length === 0) return { min: 0, max: 100 }
  return { min: Math.min(...values), max: Math.max(...values) }
}

const getRegionName = (feature) => {
  return feature.properties.name || feature.properties.NAME_LATN || feature.properties.NUTS_ID
}

const getFeatureStyle = (feature) => {
  const nutsId = feature.properties.NUTS_ID
  const value = getRegionValue(nutsId)
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
  const nutsId = feature.properties.NUTS_ID
  const regionName = getRegionName(feature)

  layer.on({
    mouseover: (e) => {
      e.target.setStyle(highlightStyle)
      e.target.bringToFront()

      const value = getRegionValue(nutsId)
      hoverInfo.value = {
        name: regionName,
        nutsId,
        value
      }
    },
    mouseout: (e) => {
      geoJsonLayer.value.resetStyle(e.target)
      hoverInfo.value = null
    }
  })
}

const updateMapColors = () => {
  if (geoJsonLayer.value) {
    geoJsonLayer.value.setStyle(getFeatureStyle)
  }
}

watch(
  () => [selectedCrime.value, selectedYear.value],
  () => updateMapColors()
)

onMounted(async () => {
  try {
    loading.value = true
    const base = import.meta.env.BASE_URL

    const [geoRes, dataRes] = await Promise.all([
      fetch(`${base}data/regions/geo/${props.countryCode}.geojson`),
      fetch(`${base}data/regions/data/${props.countryCode}.json`)
    ])

    if (!geoRes.ok || !dataRes.ok) {
      noData.value = true
      loading.value = false
      return
    }

    geoData.value = await geoRes.json()
    regionalData.value = await dataRes.json()

    if (filteredCrimes.value.length && !regionalData.value.crimes[selectedCrime.value]) {
      selectedCrime.value = filteredCrimes.value[0].code
    }

    const crimeD = regionalData.value.crimes[selectedCrime.value]
    if (crimeD) {
      const firstRegion = Object.values(crimeD)[0]
      if (firstRegion) {
        const availYears = Object.keys(firstRegion).map(Number).sort((a, b) => b - a)
        if (availYears.length) selectedYear.value = availYears[0]
      }
    }

    loading.value = false
    await nextTick()

    map.value = L.map(mapContainer.value, {
      zoomControl: true,
      scrollWheelZoom: true,
      attributionControl: false
    })

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
      maxZoom: 12
    }).addTo(map.value)

    geoJsonLayer.value = L.geoJSON(geoData.value, {
      style: getFeatureStyle,
      onEachFeature
    }).addTo(map.value)

    const bounds = geoJsonLayer.value.getBounds()
    map.value.fitBounds(bounds, { padding: [20, 20] })
  } catch (err) {
    console.error('Error loading regional data:', err)
    noData.value = true
    loading.value = false
  }
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
    map.value = null
  }
})
</script>

<template>
  <div class="regional-map-container">
    <div v-if="loading" class="regional-loading">
      <p>{{ t('common.loading') }}</p>
    </div>
    <div v-else-if="noData" class="regional-loading">
      <p>{{ t('common.noData') }}</p>
    </div>
    <template v-else>
      <div class="regional-controls">
        <div class="control-group">
          <label>{{ t('filters.crimeType') }}:</label>
          <select v-model="selectedCrime">
            <option
              v-for="crime in filteredCrimes"
              :key="crime.code"
              :value="crime.code"
            >
              {{ t(`regionalCrimes.${crime.key}`) }}
            </option>
          </select>
        </div>
        <div class="control-group">
          <label>{{ t('common.year') }}:</label>
          <select v-model="selectedYear">
            <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
      </div>

      <div class="map-wrapper">
        <div ref="mapContainer" class="regional-map"></div>

        <div v-if="hoverInfo" class="region-tooltip">
          <div class="tooltip-name">{{ hoverInfo.name }}</div>
          <div class="tooltip-value">
            {{ hoverInfo.value !== null ? hoverInfo.value.toFixed(2) + ' ' + t('common.per100k') : t('common.noData') }}
          </div>
        </div>

        <div class="regional-legend">
          <span class="legend-label">{{ t('common.low') }}</span>
          <div class="legend-bar"></div>
          <span class="legend-label">{{ t('common.high') }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.regional-map-container {
  width: 100%;
}

.regional-loading {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
}

.regional-controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: #4a5568;
  white-space: nowrap;
}

.control-group select {
  padding: 0.375rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.85rem;
  background: white;
}

.map-wrapper {
  position: relative;
}

.regional-map {
  height: 400px;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  z-index: 0;
}

.region-tooltip {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #1a1a2e;
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  pointer-events: none;
  font-size: 0.8rem;
}

.tooltip-name {
  font-weight: 600;
  margin-bottom: 0.125rem;
}

.tooltip-value {
  color: #a0aec0;
  font-size: 0.75rem;
}

.regional-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.legend-label {
  font-size: 0.75rem;
  color: #718096;
}

.legend-bar {
  width: 120px;
  height: 10px;
  border-radius: 2px;
  background: linear-gradient(to right, #1a9850, #91cf60, #d9ef8b, #fee08b, #fc8d59, #d73027);
}

@media (max-width: 768px) {
  .regional-map {
    height: 280px;
  }

  .regional-controls {
    flex-direction: column;
    gap: 0.5rem;
  }

  .control-group {
    width: 100%;
  }

  .control-group select {
    flex: 1;
    width: 100%;
  }
}
</style>
