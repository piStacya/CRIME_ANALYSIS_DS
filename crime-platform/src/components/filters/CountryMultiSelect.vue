<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  countries: {
    type: Array,
    default: () => []
  },
  min: {
    type: Number,
    default: 2
  },
  max: {
    type: Number,
    default: 10
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()
const isOpen = ref(false)
const searchQuery = ref('')
const dropdownRef = ref(null)

const filteredCountries = computed(() => {
  if (!searchQuery.value) return props.countries
  const query = searchQuery.value.toLowerCase()
  return props.countries.filter(c =>
    c.name.toLowerCase().includes(query) ||
    c.code.toLowerCase().includes(query)
  )
})

const selectedCountries = computed(() => {
  return props.countries.filter(c => props.modelValue.includes(c.code))
})

const isSelected = (code) => props.modelValue.includes(code)

const toggleCountry = (code) => {
  const current = [...props.modelValue]
  const index = current.indexOf(code)

  if (index > -1) {
    if (current.length > props.min) {
      current.splice(index, 1)
      emit('update:modelValue', current)
    }
  } else {
    if (current.length < props.max) {
      current.push(code)
      emit('update:modelValue', current)
    }
  }
}

const removeCountry = (code) => {
  if (props.modelValue.length > props.min) {
    const updated = props.modelValue.filter(c => c !== code)
    emit('update:modelValue', updated)
  }
}

const clearAll = () => {
  emit('update:modelValue', [])
}

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const colors = [
  '#d73027', '#fc8d59', '#fee08b', '#91cf60', '#1a9850',
  '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#313695'
]

const getColorForIndex = (code) => {
  const index = props.modelValue.indexOf(code)
  return index >= 0 ? colors[index % colors.length] : '#718096'
}
</script>

<template>
  <div class="country-multi-select" :class="{ compact }" ref="dropdownRef">
    <label v-if="!compact" class="select-label">{{ t('compare.selectCountries') }}</label>

    <div class="compact-row" v-if="compact">
      <div class="selected-chips">
        <span
          v-for="country in selectedCountries"
          :key="country.code"
          class="country-chip"
          :style="{ borderColor: getColorForIndex(country.code), backgroundColor: getColorForIndex(country.code) + '15' }"
        >
          <span class="chip-color" :style="{ backgroundColor: getColorForIndex(country.code) }"></span>
          {{ country.name }}
          <button
            @click.stop="removeCountry(country.code)"
            class="remove-btn"
            :disabled="modelValue.length <= min"
            :title="modelValue.length <= min ? t('compare.minCountries') : ''"
          >
            &times;
          </button>
        </span>
      </div>
      <div class="dropdown-container">
        <button
          class="dropdown-trigger compact-trigger"
          @click="isOpen = !isOpen"
          type="button"
        >
          <span>+</span>
        </button>
      </div>
    </div>

    <template v-if="!compact">
      <div class="selected-countries" v-if="selectedCountries.length > 0">
        <span
          v-for="country in selectedCountries"
          :key="country.code"
          class="country-chip"
          :style="{ borderColor: getColorForIndex(country.code), backgroundColor: getColorForIndex(country.code) + '20' }"
        >
          <span class="chip-color" :style="{ backgroundColor: getColorForIndex(country.code) }"></span>
          {{ country.name }}
          <button
            @click.stop="removeCountry(country.code)"
            class="remove-btn"
            :disabled="modelValue.length <= min"
            :title="modelValue.length <= min ? t('compare.minCountries') : ''"
          >
            &times;
          </button>
        </span>
      </div>

      <div class="dropdown-container">
        <button
          class="dropdown-trigger"
          @click="isOpen = !isOpen"
          type="button"
        >
          <span v-if="modelValue.length === 0">{{ t('compare.selectCountries') }}...</span>
          <span v-else>{{ t('compare.selectedCount', { count: modelValue.length }) }}</span>
          <span class="arrow" :class="{ open: isOpen }">&#9662;</span>
        </button>
      </div>
    </template>

      <div v-if="isOpen" class="dropdown-menu">
        <div class="search-container">
          <input
            type="text"
            v-model="searchQuery"
            :placeholder="t('compare.searchPlaceholder')"
            class="search-input"
            @click.stop
          />
        </div>

        <div class="dropdown-actions" v-if="modelValue.length > 0">
          <button @click="clearAll" class="clear-btn">{{ t('compare.clearAll') }}</button>
        </div>

        <div class="countries-list">
          <label
            v-for="country in filteredCountries"
            :key="country.code"
            class="country-option"
            :class="{ selected: isSelected(country.code), disabled: !isSelected(country.code) && modelValue.length >= max }"
          >
            <input
              type="checkbox"
              :checked="isSelected(country.code)"
              @change="toggleCountry(country.code)"
              :disabled="!isSelected(country.code) && modelValue.length >= max"
            />
            <span class="country-name">{{ country.name }}</span>
            <span class="country-code">{{ country.code }}</span>
          </label>
        </div>

        <div v-if="modelValue.length >= max" class="limit-warning">
          {{ t('compare.maxCountries') }}
        </div>
      </div>
  </div>
</template>

<style scoped>
.country-multi-select {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  position: relative;
}

/* Compact mode styles */
.country-multi-select.compact {
  flex-direction: row;
  gap: 0;
}

.compact-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.selected-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.compact .country-chip {
  padding: 0.25rem 0.375rem 0.25rem 0.25rem;
  font-size: 0.8125rem;
  border-width: 1px;
}

.compact .chip-color {
  width: 8px;
  height: 8px;
}

.compact .remove-btn {
  font-size: 0.875rem;
  padding: 0 0.125rem;
  margin-left: 0.125rem;
}

.compact-trigger {
  width: 28px;
  height: 28px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.375rem;
  font-size: 1rem;
  font-weight: 500;
  color: #4575b4;
}

.compact .dropdown-container {
  position: static;
  max-width: none;
}

.compact .dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 280px;
  margin-top: 0.5rem;
}

.select-label {
  font-weight: 600;
  color: #1a1a2e;
  font-size: 1rem;
}

.selected-countries {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.country-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.5rem 0.375rem 0.375rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  border: 2px solid;
}

.chip-color {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.remove-btn {
  background: none;
  border: none;
  color: #718096;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0 0.25rem;
  margin-left: 0.25rem;
}

.remove-btn:hover:not(:disabled) {
  color: #d73027;
}

.remove-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.dropdown-container {
  position: relative;
  max-width: 280px;
}

.dropdown-trigger {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  background: white;
  cursor: pointer;
  font-size: 1rem;
  color: #4a5568;
}

.dropdown-trigger:hover {
  border-color: #4575b4;
}

.arrow {
  transition: transform 0.2s;
}

.arrow.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.25rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 100;
  max-height: 400px;
  display: flex;
  flex-direction: column;
}

.search-container {
  padding: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.search-input:focus {
  outline: none;
  border-color: #4575b4;
}

.dropdown-actions {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
}

.clear-btn {
  background: none;
  border: none;
  color: #4575b4;
  cursor: pointer;
  font-size: 0.75rem;
  text-decoration: underline;
}

.clear-btn:hover {
  color: #d73027;
}

.countries-list {
  overflow-y: auto;
  max-height: 280px;
  padding: 0.5rem 0;
}

.country-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
}

.country-option:hover:not(.disabled) {
  background: #f7fafc;
}

.country-option.selected {
  background: #ebf8ff;
}

.country-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.country-option input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: inherit;
}

.country-name {
  flex: 1;
  font-size: 0.875rem;
}

.country-code {
  color: #718096;
  font-size: 0.75rem;
  font-family: monospace;
}

.limit-warning {
  padding: 0.5rem 0.75rem;
  background: #fff5f5;
  color: #c53030;
  font-size: 0.75rem;
  text-align: center;
  border-top: 1px solid #e2e8f0;
}
</style>
