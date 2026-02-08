<script setup>
import { useI18n } from 'vue-i18n'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const { locale, t } = useI18n()
const router = useRouter()

const languages = [
  { code: 'en', label: 'EN' },
  { code: 'et', label: 'ET' }
]

const mobileMenuOpen = ref(false)

function switchLanguage(langCode) {
  locale.value = langCode
}

function toggleMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

router.afterEach(() => {
  mobileMenuOpen.value = false
})
</script>

<template>
  <header class="app-header">
    <div class="header-container">
      <router-link to="/" class="logo">
        <span class="logo-text">Crime Analysis</span>
      </router-link>

      <nav class="main-nav" :class="{ open: mobileMenuOpen }">
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
        <div class="language-switcher mobile-lang">
          <button
            v-for="lang in languages"
            :key="lang.code"
            @click="switchLanguage(lang.code)"
            :class="['lang-btn', { active: locale === lang.code }]"
          >
            {{ lang.label }}
          </button>
        </div>
      </nav>

      <div class="header-right">
        <div class="language-switcher desktop-lang">
          <button
            v-for="lang in languages"
            :key="lang.code"
            @click="switchLanguage(lang.code)"
            :class="['lang-btn', { active: locale === lang.code }]"
          >
            {{ lang.label }}
          </button>
        </div>

        <button class="hamburger" @click="toggleMenu" :class="{ open: mobileMenuOpen }">
          <span></span>
          <span></span>
          <span></span>
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

.header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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

.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 28px;
  height: 28px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}

.hamburger span {
  display: block;
  width: 100%;
  height: 2px;
  background: white;
  border-radius: 1px;
  transition: all 0.3s ease;
}

.hamburger.open span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.hamburger.open span:nth-child(2) {
  opacity: 0;
}

.hamburger.open span:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

.mobile-lang {
  display: none;
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 1rem;
  }

  .header-container {
    height: 56px;
  }

  .hamburger {
    display: flex;
  }

  .desktop-lang {
    display: none;
  }

  .main-nav {
    display: none;
    position: absolute;
    top: 56px;
    left: 0;
    right: 0;
    background: #1a1a2e;
    flex-direction: column;
    gap: 0;
    padding: 0.5rem 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }

  .main-nav.open {
    display: flex;
  }

  .nav-link {
    padding: 0.75rem 1.5rem;
    border-bottom: none;
  }

  .nav-link.router-link-active {
    background: rgba(255, 255, 255, 0.1);
    border-bottom: none;
  }

  .mobile-lang {
    display: flex;
    margin: 0.5rem 1.5rem;
  }
}
</style>
