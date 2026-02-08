<script setup>
import { ref, onMounted, computed } from 'vue'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import { useTranslations } from '@/composables/useTranslations'

const props = defineProps({
  hideYear: {
    type: Boolean,
    default: false
  }
})

const { t } = useI18n()
const filtersStore = useFiltersStore()
const { getCrimeName, getCategoryLabel } = useTranslations()

const crimesMetadata = ref([])
const categoriesMetadata = ref({})

const groupedCrimes = computed(() => {
  const groups = {}

  for (const [key, category] of Object.entries(categoriesMetadata.value)) {
    groups[key] = {
      label: getCategoryLabel(category),
      crimes: crimesMetadata.value.filter(c => c.category === key)
    }
  }

  return groups
})

onMounted(async () => {
  try {
    const base = import.meta.env.BASE_URL
    const [crimesRes, categoriesRes] = await Promise.all([
      fetch(`${base}data/crimes.json`),
      fetch(`${base}data/categories.json`)
    ])

    crimesMetadata.value = await crimesRes.json()
    categoriesMetadata.value = await categoriesRes.json()

    if (filtersStore.selectedCrimeType === 'all' && crimesMetadata.value.length > 0) {
      filtersStore.setCrimeType(crimesMetadata.value[0].code)
    }
  } catch (err) {
    console.error('Error loading filter metadata:', err)
  }
})
</script>

<template>
  <div class="crime-filters">
    <div class="filter-group">
      <label class="filter-label">{{ t('filters.crimeType') }}</label>
      <select
        class="filter-select"
        :value="filtersStore.selectedCrimeType"
        @change="filtersStore.setCrimeType($event.target.value)"
      >
        <optgroup
          v-for="(category, key) in groupedCrimes"
          :key="key"
          :label="category.label"
        >
          <option
            v-for="crime in category.crimes"
            :key="crime.code"
            :value="crime.code"
          >
            {{ getCrimeName(crime) }}
          </option>
        </optgroup>
      </select>
    </div>

    <div v-if="!hideYear" class="filter-group">
      <label class="filter-label">{{ t('filters.year') }}</label>
      <select
        class="filter-select"
        :value="filtersStore.selectedYear"
        @change="filtersStore.setYear(Number($event.target.value))"
      >
        <option
          v-for="year in filtersStore.years"
          :key="year"
          :value="year"
        >
          {{ year }}
        </option>
      </select>
    </div>

    <div class="filter-group">
      <label class="filter-label">{{ t('filters.metric') }}</label>
      <div class="metric-toggle">
        <button
          :class="['toggle-btn', { active: filtersStore.metric === 'per100k' }]"
          @click="filtersStore.setMetric('per100k')"
        >
          {{ t('filters.per100k') }}
        </button>
        <button
          :class="['toggle-btn', { active: filtersStore.metric === 'absolute' }]"
          @click="filtersStore.setMetric('absolute')"
        >
          {{ t('filters.absolute') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.crime-filters {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.filter-select {
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  background: white;
  font-size: 0.875rem;
  color: #1a202c;
  min-width: 200px;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23718096' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
}

.filter-select:hover {
  border-color: #cbd5e0;
}

.filter-select:focus {
  outline: none;
  border-color: #4fd1c5;
  box-shadow: 0 0 0 3px rgba(79, 209, 197, 0.1);
}

.metric-toggle {
  display: flex;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  overflow: hidden;
}

.toggle-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: none;
  font-size: 0.875rem;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn:first-child {
  border-right: 1px solid #e2e8f0;
}

.toggle-btn:hover:not(.active) {
  background: #f7fafc;
}

.toggle-btn.active {
  background: #1a1a2e;
  color: white;
}

@media (max-width: 768px) {
  .crime-filters {
    flex-direction: column;
    gap: 0.75rem;
  }

  .filter-select {
    min-width: 0;
    width: 100%;
  }
}
</style>
