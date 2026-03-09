<script setup>
import { ref, onMounted } from 'vue'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import { useTranslations } from '@/composables/useTranslations'
import CrimeFilters from '@/components/filters/CrimeFilters.vue'
import CrimeTrendChart from '@/components/charts/CrimeTrendChart.vue'
import CriminalFingerprintHeatmap from '@/components/charts/CriminalFingerprintHeatmap.vue'
import YearToYearChangeHeatmap from '@/components/charts/YearToYearChangeHeatmap.vue'
import { getExplorerInsights } from '@/data/insights'

const { t } = useI18n()
const filtersStore = useFiltersStore()
const { getCrimeNameByCode } = useTranslations()
const baseUrl = import.meta.env.BASE_URL
const explorerInsights = getExplorerInsights()
const expandedInsight = ref(null)

const toggleInsight = (id) => {
  expandedInsight.value = expandedInsight.value === id ? null : id
}

const categoryColors = {
  declining: '#1a9850',
  rising: '#d73027',
  shift: '#4575b4',
  context: '#8856a7'
}

const gifMapping = {
  'ICCS0101': 'Intentional homicide.gif',
  'ICCS0102': 'Attempted intentional homicide.gif',
  'ICCS020111': 'Serious assault.gif',
  'ICCS020221': 'Kidnapping.gif',
  'ICCS0301': 'Sexual violence.gif',
  'ICCS03011': 'Rape.gif',
  'ICCS03012': 'Sexual Assault.gif',
  'ICCS030221': 'Child pornography.gif',
  'ICCS0302': 'Sexual exploitation.gif',
  'ICCS0401': 'Robbery.gif',
  'ICCS0501': 'Burglary.gif',
  'ICCS05012': 'Burglary of private residential premises.gif',
  'ICCS0502': 'Theft.gif',
  'ICCS05021': 'Theft of a motorized vehicle or parts thereof.gif',
  'ICCS0601': 'Unlawful acts involving controlled drugs.gif',
  'ICCS0701': 'Fraud.gif',
  'ICCS0703': 'Corruption.gif',
  'ICCS07031': 'Bribery.gif',
  'ICCS07041': 'Money laundering.gif',
  'ICCS0903': 'Acts against computer systems.gif',
  'ICCS09051': 'Participation in an organized criminal group.gif',
  'ICCS1001': 'Acts that cause environmental pollution or degradation.gif',
  'ICCS1002': 'Acts involving the movement or dumping of waste.gif',
  'ICCS1003': 'Trade or possession of protected or prohibited species of fauna and flora.gif',
  'ICCS1004': 'Acts that result in the depletion or degradation of natural resources.gif'
}

const crimesMetadata = ref([])

const currentGifUrl = () => {
  const filename = gifMapping[filtersStore.selectedCrimeType]
  if (!filename) return null
  const base = import.meta.env.BASE_URL
  return `${base}gifs/${encodeURIComponent(filename)}`
}

const currentCrimeName = () => {
  return getCrimeNameByCode(filtersStore.selectedCrimeType, crimesMetadata.value)
}

const hasGif = () => gifMapping[filtersStore.selectedCrimeType] !== undefined

onMounted(async () => {
  try {
    const base = import.meta.env.BASE_URL
    const res = await fetch(`${base}data/crimes.json`)
    crimesMetadata.value = await res.json()
  } catch (err) {
    console.error('Error loading crimes metadata:', err)
  }
})
</script>

<template>
  <div class="explorer">
    <div class="content-wrapper">
      <header class="page-header">
        <h1>{{ t('explorer.title') }}</h1>
        <p>{{ t('explorer.subtitle') }}</p>
      </header>
      <section class="filters-section">
        <CrimeFilters :hideYear="true" />
      </section>

      <section class="card">
        <div class="card-header">
          <h2>{{ t('insights.title') }}</h2>
          <p>{{ t('insights.subtitle') }}</p>
        </div>
        <div class="card-content insights-content">
          <div class="insights-disclaimer">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
            <span>{{ t('insights.disclaimer') }}</span>
          </div>
          <div class="insights-grid">
            <div
              v-for="insight in explorerInsights"
              :key="insight.id"
              class="insight-card"
              :class="{ expanded: expandedInsight === insight.id }"
              @click="toggleInsight(insight.id)"
            >
              <div class="insight-header">
                <span
                  class="insight-badge"
                  :style="{ backgroundColor: categoryColors[insight.category] }"
                >
                  {{ t(`insights.${insight.category}`) }}
                </span>
                <h3 class="insight-title">{{ t(`insights.${insight.id}.title`) }}</h3>
                <svg
                  class="insight-chevron"
                  :class="{ rotated: expandedInsight === insight.id }"
                  width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                >
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </div>
              <div v-if="expandedInsight === insight.id" class="insight-body">
                <p>{{ t(`insights.${insight.id}.description`) }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <a
        :href="`${baseUrl}Analysis_Poster.pdf`"
        target="_blank"
        rel="noopener noreferrer"
        class="poster-link"
      >
        <div class="poster-link-content">
          <div class="poster-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <div class="poster-text">
            <span class="poster-title">{{ t('explorer.posterTitle') }}</span>
            <span class="poster-desc">{{ t('explorer.posterDesc') }}</span>
          </div>
          <svg class="poster-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
            <polyline points="15 3 21 3 21 9"/>
            <line x1="10" y1="14" x2="21" y2="3"/>
          </svg>
        </div>
      </a>

      <section class="card">
        <div class="card-header">
          <h2>{{ t('explorer.trends') }} (2008-2023)</h2>
          <p>{{ t('explorer.trendsDesc') }}</p>
        </div>
        <div class="card-content">
          <CrimeTrendChart :key="filtersStore.selectedCrimeType + filtersStore.metric" />
        </div>
      </section>

      <section v-if="hasGif()" class="card">
        <div class="card-header">
          <h2>{{ t('explorer.animatedMaps') }}: {{ currentCrimeName() }}</h2>
          <p>{{ t('explorer.animatedDesc', { crime: currentCrimeName().toLowerCase() }) }}</p>
        </div>
        <div class="gif-container">
          <img
            :src="currentGifUrl()"
            :alt="`Animated map: ${currentCrimeName()}`"
            class="animated-gif"
          />
        </div>
      </section>

      <section class="card">
        <div class="card-header">
          <h2>{{ t('explorer.yearToYear') }}</h2>
          <p>{{ t('explorer.yearToYearDesc') }}</p>
        </div>
        <div class="card-content heatmap-content">
          <YearToYearChangeHeatmap />
        </div>
      </section>

      <section class="card">
        <div class="card-header">
          <h2>{{ t('explorer.fingerprints') }}</h2>
          <p>{{ t('explorer.fingerprintsDesc') }}</p>
        </div>
        <div class="card-content heatmap-content">
          <CriminalFingerprintHeatmap />
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
.explorer {
  min-height: calc(100vh - 64px);
  background: #f7fafc;
}

.page-header {
  margin-bottom: -10px;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 0.25rem;
}

.page-header p {
  color: #718096;
  margin: 0;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.filters-section {
  background: white;
  padding: 1.25rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 1.5rem 1.5rem 0;
}

.card-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 0.75rem;
}

.card-header p {
  color: #4a5568;
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
}

.card-header p strong {
  color: #1a1a2e;
}

.card-content {
  padding: 1.5rem;
}

.heatmap-content {
  overflow-x: auto;
}

.gif-container {
  padding: 0.5rem;
  display: flex;
  justify-content: center;
  overflow: hidden;
}

.animated-gif {
  width: 100%;
  max-width: 850px;
  height: auto;
  border-radius: 0.5rem;
  margin: -145px 0;
  clip-path: inset(145px 0 145px 0);
}

.insights-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.insights-disclaimer {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 0.375rem;
  font-size: 0.8rem;
  color: #92400e;
  line-height: 1.5;
}

.insights-disclaimer svg {
  flex-shrink: 0;
  margin-top: 1px;
  color: #d97706;
}

.insights-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.insight-card {
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.insight-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.insight-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
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
}

.insight-title {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.insight-chevron {
  flex-shrink: 0;
  color: #a0aec0;
  transition: transform 0.2s;
}

.insight-chevron.rotated {
  transform: rotate(180deg);
}

.insight-body {
  padding: 0 1rem 1rem;
  border-top: 1px solid #f1f5f9;
}

.insight-body p {
  margin: 0.75rem 0 0;
  font-size: 0.85rem;
  color: #4a5568;
  line-height: 1.7;
}

.poster-link {
  display: block;
  text-decoration: none;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.poster-link:hover {
  border-color: #4575b4;
  box-shadow: 0 2px 8px rgba(69, 117, 180, 0.15);
}

.poster-link-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
}

.poster-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f4ff;
  border-radius: 0.5rem;
  color: #4575b4;
}

.poster-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.poster-title {
  font-weight: 600;
  font-size: 0.925rem;
  color: #1a1a2e;
}

.poster-desc {
  font-size: 0.8rem;
  color: #718096;
}

.poster-arrow {
  flex-shrink: 0;
  color: #a0aec0;
  transition: color 0.2s;
}

.poster-link:hover .poster-arrow {
  color: #4575b4;
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 1rem;
    gap: 1rem;
    overflow-x: hidden;
  }

  .card {
    overflow: hidden;
    max-width: 100%;
  }

  .card-header {
    padding: 1rem 1rem 0;
  }

  .card-header h2 {
    font-size: 1.1rem;
  }

  .card-content {
    padding: 1rem;
    overflow: hidden;
  }

  .heatmap-content {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .filters-section {
    padding: 0.75rem;
  }

  .gif-container {
    padding: 0.25rem;
  }

  .animated-gif {
    max-width: 100%;
    margin: -17% 0;
    clip-path: inset(17% 0 17% 0);
  }

  .insight-header {
    gap: 0.5rem;
    padding: 0.75rem;
  }

  .insight-title {
    font-size: 0.8rem;
  }

  .insight-body {
    padding: 0 0.75rem 0.75rem;
  }

  .poster-link-content {
    padding: 0.75rem 1rem;
  }
}
</style>
