<script setup>
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const router = useRouter()

const goToHome = () => {
  sessionStorage.setItem('hasVisited', 'true')
  router.push('/home')
}
</script>

<template>
  <div class="landing">
    <section class="hero">
      <div class="hero-container">
        <div class="hero-content">
          <h1 class="title">{{ t('landing.title') }}</h1>
          <p class="subtitle">{{ t('landing.subtitle') }}</p>

          <div class="stats-row">
            <div class="stat">
              <span class="stat-number">39</span>
              <span class="stat-text">{{ t('landing.stats.countries') }}</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat">
              <span class="stat-number">25</span>
              <span class="stat-text">{{ t('landing.stats.crimeTypes') }}</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat">
              <span class="stat-number">16</span>
              <span class="stat-text">{{ t('landing.stats.years') }}</span>
            </div>
          </div>

          <button class="cta-button" @click="goToHome">
            {{ t('landing.cta') }}
            <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>
        </div>
      </div>
    </section>

    <section class="features">
      <div class="features-container">
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l5.447 2.724A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
            </svg>
          </div>
          <h3>{{ t('landing.features.maps.title') }}</h3>
          <p>{{ t('landing.features.maps.desc') }}</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M3 3v18h18M7 16l4-4 4 4 5-6"/>
            </svg>
          </div>
          <h3>{{ t('landing.features.trends.title') }}</h3>
          <p>{{ t('landing.features.trends.desc') }}</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </div>
          <h3>{{ t('landing.features.compare.title') }}</h3>
          <p>{{ t('landing.features.compare.desc') }}</p>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
.landing {
  min-height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  background: #f7fafc;
}

.hero {
  background: #1a1a2e;
  padding: 4rem 2rem;
  flex: 1;
  display: flex;
  align-items: center;
}

.hero-container {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.hero-content {
  text-align: center;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 1rem;
  line-height: 1.2;
}

.subtitle {
  font-size: 1.1rem;
  color: #a0aec0;
  line-height: 1.7;
  margin: 0 0 2.5rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.stats-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2.5rem;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  line-height: 1;
}

.stat-text {
  font-size: 0.85rem;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.5rem;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: #2d3748;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: #2d3748;
  border: 1px solid #4a5568;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cta-button:hover {
  background: #4a5568;
  border-color: #718096;
}

.arrow-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.2s ease;
}

.cta-button:hover .arrow-icon {
  transform: translateX(4px);
}

.features {
  padding: 3rem 2rem;
  background: white;
}

.features-container {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 1.5rem;
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 1rem;
  color: #1a1a2e;
}

.feature-icon svg {
  width: 100%;
  height: 100%;
}

.feature-card h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 0.5rem;
}

.feature-card p {
  font-size: 0.9rem;
  color: #718096;
  line-height: 1.6;
  margin: 0;
}

@media (max-width: 768px) {
  .hero {
    padding: 3rem 1.5rem;
  }

  .title {
    font-size: 1.75rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .stats-row {
    gap: 1rem;
  }

  .stat-number {
    font-size: 1.75rem;
  }

  .stat-divider {
    height: 30px;
  }

  .features-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .feature-card {
    padding: 1rem;
  }
}
</style>
