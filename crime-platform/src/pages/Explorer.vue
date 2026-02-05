<script setup>
import { ref, onMounted } from 'vue'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import { useTranslations } from '@/composables/useTranslations'
import CrimeFilters from '@/components/filters/CrimeFilters.vue'
import CrimeTrendChart from '@/components/charts/CrimeTrendChart.vue'
import CriminalFingerprintHeatmap from '@/components/charts/CriminalFingerprintHeatmap.vue'
import YearToYearChangeHeatmap from '@/components/charts/YearToYearChangeHeatmap.vue'

const { t } = useI18n()
const filtersStore = useFiltersStore()
const { getCrimeNameByCode } = useTranslations()

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

@media (max-width: 768px) {
  .content-wrapper {
    padding: 1.5rem;
    gap: 1.5rem;
  }

  .card-header {
    padding: 1.25rem 1.25rem 0;
  }

  .card-content {
    padding: 1.25rem;
  }
}
</style>
