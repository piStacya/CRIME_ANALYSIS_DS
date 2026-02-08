<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useFiltersStore } from '@/stores/filters'
import EuropeMap from '@/components/maps/EuropeMap.vue'
import CrimeFilters from '@/components/filters/CrimeFilters.vue'

const { t, locale } = useI18n()
const router = useRouter()
const filtersStore = useFiltersStore()

const selectedCountry = ref(null)
const showModal = ref(false)

const countries = ref([])
const showCountryDropdown = ref(false)
const countryQuery = ref('')
const countryInputRef = ref(null)
const countryWrapperRef = ref(null)

onMounted(async () => {
  try {
    const base = import.meta.env.BASE_URL
    const res = await fetch(`${base}data/countries.json`)
    countries.value = await res.json()
  } catch (e) {}
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})

const handleOutsideClick = (e) => {
  if (countryWrapperRef.value && !countryWrapperRef.value.contains(e.target)) {
    showCountryDropdown.value = false
  }
}

const filteredCountries = computed(() => {
  const sorted = [...countries.value].sort((a, b) => {
    const nameA = locale.value === 'et' ? (a.nameEt || a.name) : a.name
    const nameB = locale.value === 'et' ? (b.nameEt || b.name) : b.name
    return nameA.localeCompare(nameB)
  })
  if (!countryQuery.value) return sorted
  const q = countryQuery.value.toLowerCase()
  return sorted.filter(c => {
    const name = locale.value === 'et' ? (c.nameEt || c.name) : c.name
    return name.toLowerCase().includes(q) || c.code.toLowerCase().includes(q)
  })
})

const getCountryName = (c) => {
  return locale.value === 'et' ? (c.nameEt || c.name) : c.name
}

const onInputFocus = () => {
  showCountryDropdown.value = true
}

const goToCountry = (code) => {
  showCountryDropdown.value = false
  countryQuery.value = ''
  router.push(`/country/${code}`)
}

const handleCountryClick = (country) => {
  selectedCountry.value = country
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedCountry.value = null
}
</script>

<template>
  <div class="home">
    <section class="welcome-banner">
      <h1>{{ t('home.title') }}</h1>
      <p>{{ t('home.subtitle') }}</p>
    </section>

    <section class="filters-section">
      <div class="filters-row">
        <CrimeFilters />
        <div class="explore-country-wrapper" ref="countryWrapperRef">
          <div class="explore-country-input-wrap">
            <label class="explore-label">{{ t('home.exploreCountry') }}</label>
            <div class="explore-input-inner">
              <svg class="explore-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input
                ref="countryInputRef"
                v-model="countryQuery"
                type="text"
                :placeholder="t('home.exploreCountryPlaceholder')"
                class="explore-country-input"
                @focus="onInputFocus"
                @click.stop
              />
            </div>
          </div>
          <div v-if="showCountryDropdown" class="explore-country-dropdown">
            <button
              v-for="c in filteredCountries"
              :key="c.code"
              class="explore-country-item"
              @click="goToCountry(c.code)"
            >
              {{ getCountryName(c) }}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
            <div v-if="filteredCountries.length === 0" class="explore-country-empty">
              {{ t('common.noData') }}
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="map-section">
      <EuropeMap
        height="550px"
        @country-click="handleCountryClick"
      />
    </section>

    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
          <div class="modal-box">
            <button class="modal-close" @click="closeModal">&times;</button>
            <h2>{{ selectedCountry?.name }}</h2>
            <div class="modal-stat">
              <span class="stat-label">{{ t('common.crimeRate') }}</span>
              <span class="stat-value">
                {{ selectedCountry?.value?.toLocaleString() ?? t('common.noData') }}
                <span v-if="selectedCountry?.value && filtersStore.metric === 'per100k'" class="stat-unit">{{ t('common.per100k') }}</span>
              </span>
            </div>
            <div class="modal-actions">
              <router-link
                :to="`/country/${selectedCountry?.code}`"
                class="btn primary"
              >
                {{ t('common.viewDetails') }}
              </router-link>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.home {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.welcome-banner {
  margin-bottom: 20px;
}

.welcome-banner h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 0.25rem;
}

.welcome-banner p {
  color: #718096;
  margin: 0;
}

.filters-section {
  background: white;
  padding: 1.25rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.filters-row {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
}

.explore-country-wrapper {
  position: relative;
  flex-shrink: 0;
  margin-left: auto;
}

.explore-country-input-wrap {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.explore-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #4575b4;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.explore-input-inner {
  position: relative;
  display: flex;
  align-items: center;
}

.explore-icon {
  position: absolute;
  left: 0.625rem;
  color: #4575b4;
  pointer-events: none;
}

.explore-country-input {
  padding: 0.5rem 0.75rem 0.5rem 2rem;
  border: 2px solid #4575b4;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  width: 200px;
  outline: none;
  background: #f0f4ff;
  color: #1a1a2e;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.explore-country-input::placeholder {
  color: #4575b4;
  font-weight: 600;
}

.explore-country-input:focus {
  border-color: #2b5a9e;
  box-shadow: 0 0 0 3px rgba(69, 117, 180, 0.15);
  background: white;
}

.explore-country-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 240px;
  max-height: 220px;
  overflow-y: auto;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 1001;
}

.explore-country-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  text-align: left;
  padding: 0.5rem 0.75rem;
  background: none;
  border: none;
  font-size: 0.825rem;
  color: #1a1a2e;
  cursor: pointer;
  transition: background 0.15s;
}

.explore-country-item:hover {
  background: #f0f4ff;
}

.explore-country-item svg {
  color: #a0aec0;
  flex-shrink: 0;
}

.explore-country-item:hover svg {
  color: #4575b4;
}

.explore-country-empty {
  padding: 1rem;
  text-align: center;
  color: #a0aec0;
  font-size: 0.825rem;
}

.explore-country-dropdown .explore-country-item + .explore-country-item {
  border-top: 1px solid #f1f5f9;
}

.map-section {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-box {
  background: white;
  border-radius: 0.75rem;
  padding: 1.75rem;
  width: 320px;
  max-width: 90%;
  position: relative;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  line-height: 1;
}

.modal-close:hover {
  color: #1a1a2e;
}

.modal-box h2 {
  font-size: 1.375rem;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 1rem;
  padding-right: 1.5rem;
}

.modal-stat {
  background: #f8fafc;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.25rem;
}

.stat-label {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a2e;
}

.stat-unit {
  font-size: 0.875rem;
  font-weight: 400;
  color: #64748b;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.875rem;
  border-radius: 0.3rem;
  font-size: 0.8125rem;
  font-weight: 500;
  text-align: center;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.15s;
  border: none;
}

.btn.primary {
  background: #1a1a2e;
  color: white;
}

.btn.primary:hover {
  background: #2d2d44;
}

.btn.secondary {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn.secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #1a1a2e;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-active .modal-box,
.fade-leave-active .modal-box {
  transition: transform 0.25s ease;
}

.fade-enter-from .modal-box,
.fade-leave-to .modal-box {
  transform: scale(0.95);
}

@media (max-width: 768px) {
  .home {
    padding: 1rem;
  }

  .welcome-banner h1 {
    font-size: 1.5rem;
  }

  .filters-section {
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }

  .explore-country-wrapper {
    margin-left: 0;
  }

  .explore-country-input {
    width: 100%;
  }

  .explore-country-dropdown {
    width: 100%;
  }

  .modal-box {
    width: calc(100% - 2rem);
  }
}
</style>
