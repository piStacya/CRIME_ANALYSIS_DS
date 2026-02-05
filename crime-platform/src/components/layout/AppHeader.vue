<script setup>
import { useI18n } from 'vue-i18n'
import { ref } from 'vue'

const { locale, t } = useI18n()

const languages = [
  { code: 'en', label: 'EN' },
  { code: 'et', label: 'ET' }
]

function switchLanguage(langCode) {
  locale.value = langCode
}
</script>

<template>
  <header class="app-header">
    <div class="header-container">
      <router-link to="/" class="logo">
        <span class="logo-text">Crime Analysis</span>
      </router-link>

      <nav class="main-nav">
        <router-link to="/home" class="nav-link">
          {{ t('nav.home') }}
        </router-link>
        <router-link to="/explorer" class="nav-link">
          {{ t('nav.explorer') }}
        </router-link>
        <router-link to="/compare" class="nav-link">
          {{ t('nav.compare') }}
        </router-link>
        <router-link to="/about" class="nav-link">
          {{ t('nav.about') }}
        </router-link>
      </nav>

      <div class="language-switcher">
        <button
          v-for="lang in languages"
          :key="lang.code"
          @click="switchLanguage(lang.code)"
          :class="['lang-btn', { active: locale === lang.code }]"
        >
          {{ lang.label }}
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: #1a1a2e;
  color: white;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: white;
  font-weight: 700;
  font-size: 1.125rem;
}

.main-nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: white;
}

.nav-link.router-link-active {
  color: white;
  border-bottom-color: #4fd1c5;
}

.language-switcher {
  display: flex;
  gap: 0.25rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.375rem;
  padding: 0.25rem;
}

.lang-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  padding: 0.375rem 0.75rem;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.lang-btn:hover {
  color: white;
}

.lang-btn.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}
</style>
