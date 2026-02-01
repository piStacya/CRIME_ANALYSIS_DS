<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFiltersStore } from '@/stores/filters'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const filtersStore = useFiltersStore()

const loading = ref(true)
const crimeData = ref(null)
const countriesMetadata = ref(null)
const sortColumn = ref('value')
const sortAsc = ref(false)


const tableData = computed(() => {
  if (!crimeData.value || !countriesMetadata.value) return []

  const yearData = crimeData.value[filtersStore.selectedYear]
  if (!yearData) return []

  const crimeTypeData = yearData[filtersStore.selectedCrimeType]
  if (!crimeTypeData) return []

  const unitKey = filtersStore.metric === 'per100k' ? 'per100k' : 'absolute'
  const values = crimeTypeData[unitKey] || {}

  const rows = Object.entries(values)
    .filter(([code, value]) => value !== null)
    .map(([code, value]) => {
      const country = countriesMetadata.value.find(c => c.code === code)
      return {
        code,
        name: country ? country.name : code,
        value: value
      }
    })


  rows.sort((a, b) => {
    let cmp = 0
    if (sortColumn.value === 'name') {
      cmp = a.name.localeCompare(b.name)
    } else {
      cmp = a.value - b.value
    }
    return sortAsc.value ? cmp : -cmp
  })

  return rows
})


const toggleSort = (column) => {
  if (sortColumn.value === column) {
    sortAsc.value = !sortAsc.value
  } else {
    sortColumn.value = column
    sortAsc.value = column === 'name'
  }
}


const getSortIcon = (column) => {
  if (sortColumn.value !== column) return '↕'
  return sortAsc.value ? '↑' : '↓'
}


onMounted(async () => {
  try {
    const base = import.meta.env.BASE_URL
    const [crimeRes, countriesRes] = await Promise.all([
      fetch(`${base}data/map-data.json`),
      fetch(`${base}data/countries.json`)
    ])

    crimeData.value = await crimeRes.json()
    countriesMetadata.value = await countriesRes.json()
    loading.value = false
  } catch (err) {
    console.error('Error loading table data:', err)
    loading.value = false
  }
})
</script>

<template>
  <div class="data-table-container">
    <div v-if="loading" class="table-loading">
      <p>{{ t('common.loading') }}</p>
    </div>
    <div v-else-if="tableData.length === 0" class="table-empty">
      <p>{{ t('common.noData') }}</p>
    </div>
    <div v-else class="table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th class="rank-col">#</th>
            <th class="country-col" @click="toggleSort('name')">
              Country <span class="sort-icon">{{ getSortIcon('name') }}</span>
            </th>
            <th class="value-col" @click="toggleSort('value')">
              Value <span class="sort-icon">{{ getSortIcon('value') }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in tableData" :key="row.code">
            <td class="rank-col">{{ index + 1 }}</td>
            <td class="country-col">
              <span class="country-code">{{ row.code }}</span>
              {{ row.name }}
            </td>
            <td class="value-col">
              {{ row.value.toLocaleString(undefined, { maximumFractionDigits: 2 }) }}
              <span class="value-unit">
                {{ filtersStore.metric === 'per100k' ? 'per 100k' : '' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.data-table-container {
  width: 100%;
}

.table-loading,
.table-empty {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #718096;
}

.table-wrapper {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  position: sticky;
  top: 0;
  background: #1a1a2e;
  z-index: 10;
}

.data-table th {
  color: white;
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  user-select: none;
}

.data-table th:hover {
  background: #2d2d44;
}

.sort-icon {
  margin-left: 0.5rem;
  opacity: 0.7;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.data-table tbody tr:hover {
  background: #f7fafc;
}

.rank-col {
  width: 50px;
  text-align: center;
  color: #718096;
}

.country-col {
  min-width: 200px;
}

.country-code {
  display: inline-block;
  background: #e2e8f0;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  margin-right: 0.5rem;
  color: #4a5568;
}

.value-col {
  text-align: right;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.data-table th.value-col {
  text-align: right;
}

.value-unit {
  font-weight: 400;
  color: #718096;
  font-size: 0.75rem;
  margin-left: 0.25rem;
}
</style>
