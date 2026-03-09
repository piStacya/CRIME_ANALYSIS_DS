<script setup>
import { ref, onMounted, computed } from 'vue'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'
import { useTranslations } from '@/composables/useTranslations'
import AppSelect from '@/components/filters/AppSelect.vue'

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

const crimeGroups = computed(() => {
  return Object.values(groupedCrimes.value)
    .filter(g => g.crimes.length > 0)
    .map(g => ({
      label: g.label,
      items: g.crimes.map(c => ({ value: c.code, label: getCrimeName(c) }))
    }))
})

const yearOptions = computed(() => {
  return filtersStore.years.map(y => ({ value: y, label: String(y) }))
})

const onCrimeChange = (val) => filtersStore.setCrimeType(val)
const onYearChange = (val) => filtersStore.setYear(Number(val))

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
      <AppSelect
        :modelValue="filtersStore.selectedCrimeType"
        @update:modelValue="onCrimeChange"
        :groups="crimeGroups"
      />
    </div>

    <div v-if="!hideYear" class="filter-group">
      <label class="filter-label">{{ t('filters.year') }}</label>
      <AppSelect
        :modelValue="filtersStore.selectedYear"
        @update:modelValue="onYearChange"
        :options="yearOptions"
      />
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

:deep(.app-select-wrapper) {
  min-width: 200px;
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
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: flex-end;
  }

  .filter-group:first-child {
    flex: 1;
    min-width: 0;
  }

  .filter-group:first-child :deep(.app-select-wrapper) {
    width: 100%;
  }

  .filter-group:last-child {
    flex-shrink: 0;
  }

  .filter-group:last-child .filter-label {
    display: none;
  }

  .metric-toggle {
    border-color: #e2e8f0;
    border-radius: 0.375rem;
  }

  .toggle-btn {
    padding: 0.3rem 0.625rem;
    font-size: 0.75rem;
    font-weight: 500;
  }
}
</style>
