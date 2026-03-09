<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="about-page">
    <h1>{{ t('about.title') }}</h1>

    <div class="about-card">
      <section class="section">
        <h2>{{ t('about.sourceCode.title') }}</h2>
        <p>{{ t('about.sourceCode.content') }}</p>
        <a
          href="https://github.com/piStacya/CRIME_ANALYSIS_DS"
          target="_blank"
          rel="noopener noreferrer"
          class="github-link"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
          </svg>
          <span>{{ t('about.sourceCode.link') }}</span>
        </a>
      </section>

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

.github-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: #1a1a2e;
  text-decoration: none;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.9rem;
  font-weight: 500;
  transition: border-color 0.2s, box-shadow 0.2s;
  margin-top: 0.75rem;
}

.github-link:hover {
  border-color: #4575b4;
  box-shadow: 0 1px 4px rgba(69, 117, 180, 0.15);
}

@media (max-width: 768px) {
  .about-page {
    padding: 1rem;
  }

  .about-page h1 {
    font-size: 1.5rem;
    padding-left: 0;
  }

  .about-card {
    padding: 1.25rem;
  }
}
</style>
