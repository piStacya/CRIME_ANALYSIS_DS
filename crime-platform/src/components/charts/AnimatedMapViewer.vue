<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const filtersStore = useFiltersStore()

const crimesMetadata = ref([])

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

const currentGifUrl = computed(() => {
  const filename = gifMapping[filtersStore.selectedCrimeType]
  if (!filename) return null
  const base = import.meta.env.BASE_URL
  return `${base}gifs/${encodeURIComponent(filename)}`
})

const currentCrimeName = computed(() => {
  const crime = crimesMetadata.value.find(c => c.code === filtersStore.selectedCrimeType)
  return crime ? crime.name : filtersStore.selectedCrimeType
})


const hasGif = computed(() => {
  return gifMapping[filtersStore.selectedCrimeType] !== undefined
})


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
  <div class="animated-map-viewer">
    <div v-if="hasGif" class="gif-container">
      <img
        :src="currentGifUrl"
        :alt="`Animated map: ${currentCrimeName}`"
        class="animated-gif"
      />
      <p class="gif-caption">
        {{ currentCrimeName }} - Animated timeline (2008-2023)
      </p>
    </div>
    <div v-else class="no-gif">
      <p>No animated map available for this crime type</p>
    </div>
  </div>
</template>

<style scoped>
.animated-map-viewer {
  width: 100%;
}

.gif-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.animated-gif {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.gif-caption {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #4a5568;
  text-align: center;
}

.no-gif {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7fafc;
  border: 2px dashed #cbd5e0;
  border-radius: 0.5rem;
  color: #718096;
}
</style>
