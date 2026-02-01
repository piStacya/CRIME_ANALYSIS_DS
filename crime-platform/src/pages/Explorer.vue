<script setup>
import { ref, onMounted } from 'vue'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import CrimeFilters from '@/components/filters/CrimeFilters.vue'
import CrimeTrendChart from '@/components/charts/CrimeTrendChart.vue'
import CriminalFingerprintHeatmap from '@/components/charts/CriminalFingerprintHeatmap.vue'

const { t } = useI18n()
const filtersStore = useFiltersStore()

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
  const crime = crimesMetadata.value.find(c => c.code === filtersStore.selectedCrimeType)
  return crime ? crime.name : ''
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
    <header class="page-header">
      <h1>European Crime Data Explorer</h1>
      <p>Analyze crime patterns and trends across all European countries. Use the filters to explore different crime types, years, and metrics.</p>
    </header>

    <section class="filters-section">
      <CrimeFilters :hideYear="true" />
    </section>

    <div class="content">

      <section class="section">
        <div class="section-header">
          <h2>Crime Trends Over Time (2008-2023)</h2>
          <p class="section-description">
            This chart shows how the selected crime type has changed over 16 years across the <strong>top 5 countries</strong>
            with the highest average rates. The lines help identify long-term trends — whether crime is increasing,
            decreasing, or remaining stable in different regions.
          </p>
        </div>
        <div class="section-content">
          <CrimeTrendChart :key="filtersStore.selectedCrimeType + filtersStore.metric" />
        </div>
      </section>

      <section v-if="hasGif()" class="section section-gif">
        <div class="section-header">
          <h2>Animated Timeline: {{ currentCrimeName() }}</h2>
          <p class="section-description">
            Watch how {{ currentCrimeName().toLowerCase() }} rates have evolved across Europe from 2008 to 2023.
            Darker colors indicate higher crime rates per 100,000 inhabitants.
            This animation helps visualize geographical patterns and how they shift over time.
          </p>
        </div>
        <div class="gif-container">
          <img
            :src="currentGifUrl()"
            :alt="`Animated map: ${currentCrimeName()}`"
            class="animated-gif"
          />
        </div>
      </section>

    </div>

    <section class="section section-wide heatmap-section">
      <div class="section-header">
        <h2>Criminal Fingerprints: Country vs European Average</h2>
        <p class="section-description">
          This heatmap compares each country's crime rates to the European average (2019-2023 data).
          <strong>Green</strong> means below average, <strong>red</strong> means above average.
          Values show how many times higher or lower than the EU average (1.0 = exactly average).
          This visualization reveals each country's unique "criminal fingerprint" — their distinctive pattern of crime types.
        </p>
      </div>
      <div class="section-content heatmap-content">
        <CriminalFingerprintHeatmap />
      </div>
    </section>
  </div>
</template>

<style scoped>
.explorer {
  min-height: 100vh;
  background: #f7fafc;
}

.page-header {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 2rem 1rem;
}

.page-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 0.5rem;
}

.page-header p {
  color: #718096;
  font-size: 0.95rem;
  margin: 0;
  line-height: 1.5;
}

.filters-section {
  max-width: 1200px;
  margin: 0 auto 1.5rem;
  padding: 0 2rem;
}

.filters-section > :deep(*) {
  background: white;
  padding: 1.25rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.section {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.section-header {
  padding: 1.5rem 1.5rem 0;
}

.section-header h2 {
  font-size: 1.35rem;
  color: #1a1a2e;
  margin: 0 0 0.75rem;
}

.section-description {
  color: #4a5568;
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0;
}

.section-description strong {
  color: #1a1a2e;
}

.section-content {
  padding: 1.5rem;
}

.heatmap-section {
  max-width: 1200px;
  margin: 0 auto 2rem;
  margin-left: auto;
  margin-right: auto;
  padding: 0 2rem;
  box-sizing: content-box;
}

.heatmap-section .section-header {
  max-width: none;
}

.section-wide .heatmap-content {
  padding: 1rem;
  overflow-x: auto;
}

.section-gif {
  background: white;
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
  .page-header {
    padding: 1.5rem 1rem 1rem;
  }

  .filters-section {
    padding: 0 1rem;
  }

  .content {
    padding: 1rem;
  }

  .heatmap-section {
    margin: 0 1rem 1rem;
  }

  .section-header {
    padding: 1rem 1rem 0;
  }

  .section-content {
    padding: 1rem;
  }
}
</style>
