<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFiltersStore } from '@/stores/filters'
import EuropeMap from '@/components/maps/EuropeMap.vue'
import CrimeFilters from '@/components/filters/CrimeFilters.vue'

const { t } = useI18n()
const filtersStore = useFiltersStore()

const selectedCountry = ref(null)
const showModal = ref(false)

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
      <CrimeFilters />
    </section>

    <section class="map-section">
      <EuropeMap
        height="550px"
        @country-click="handleCountryClick"
      />
    </section>

    <!-- Modal -->
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

.map-section {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Modal */
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

/* Animation */
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
</style>
