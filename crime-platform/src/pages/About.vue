<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="about-page">
    <h1>{{ t('about.title') }}</h1>

    <div class="about-card">
      <section class="section">
        <h2>{{ t('about.overview.title') }}</h2>
        <p>{{ t('about.overview.content') }}</p>
      </section>

      <section class="section">
        <h2>{{ t('about.methodology.title') }}</h2>
        <p>{{ t('about.methodology.content') }}</p>
      </section>

      <section class="section">
        <h2>{{ t('about.scope.title') }}</h2>
        <p>{{ t('about.scope.content') }}</p>
      </section>

      <section class="section">
        <h2>{{ t('about.credits.title') }}</h2>
        <p>{{ t('about.credits.content') }}</p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.about-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

.about-page h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 1.5rem;
  padding-left: 15px;
}

.about-card {
  background: white;
  border-radius: 0.75rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section {
  margin-bottom: 2rem;
}

.section:last-child {
  margin-bottom: 0;
}

.section h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  padding-left: 0;
  border-bottom: 1px solid #e2e8f0;
}

.section p {
  color: #4a5568;
  line-height: 1.7;
  margin: 0;
}
</style>
