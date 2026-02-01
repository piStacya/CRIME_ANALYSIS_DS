<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import EuropeMap from '@/components/maps/EuropeMap.vue'
import CrimeFilters from '@/components/filters/CrimeFilters.vue'

const { t } = useI18n()

const selectedCountry = ref(null)
const showCountryModal = ref(false)

const handleCountryClick = (country) => {
  selectedCountry.value = country
  showCountryModal.value = true
}

const closeModal = () => {
  showCountryModal.value = false
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

    <Teleport to="body">
      <div v-if="showCountryModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-content">
          <button class="modal-close" @click="closeModal">&times;</button>
          <h2>{{ selectedCountry?.name }}</h2>
          <div class="country-stats">
            <div class="stat-item">
              <span class="stat-label">Current Value</span>
              <span class="stat-value">
                {{ selectedCountry?.value?.toLocaleString() ?? t('common.noData') }}
              </span>
            </div>
          </div>
          <div class="modal-actions">
            <router-link
              :to="`/country/${selectedCountry?.code}`"
              class="btn-primary"
            >
              {{ t('common.viewDetails') }}
            </router-link>
            <router-link
              to="/explorer"
              class="btn-secondary"
            >
              View All Europe
            </router-link>
          </div>
        </div>
      </div>
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
  text-align: left;
  margin-bottom: 1.5rem;
}

.welcome-banner h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.welcome-banner p {
  color: #718096;
  font-size: 0.95rem;
  line-height: 1.5;
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

.modal-content {
  background: white;
  border-radius: 0.75rem;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  position: relative;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #718096;
  cursor: pointer;
  line-height: 1;
}

.modal-close:hover {
  color: #1a1a2e;
}

.modal-content h2 {
  font-size: 1.5rem;
  color: #1a1a2e;
  margin-bottom: 1.5rem;
}

.country-stats {
  margin-bottom: 1.5rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.stat-label {
  color: #718096;
  font-size: 0.875rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a2e;
}

.modal-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  display: inline-block;
  background: #1a1a2e;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  text-decoration: none;
  font-weight: 500;
  transition: background 0.2s ease;
}

.btn-primary:hover {
  background: #2d2d44;
  color: white;
}

.btn-secondary {
  display: inline-block;
  background: white;
  color: #1a1a2e;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  text-decoration: none;
  font-weight: 500;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #f7fafc;
  border-color: #cbd5e0;
}
</style>
