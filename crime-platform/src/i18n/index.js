import { createI18n } from 'vue-i18n'
import en from '../locales/en.json'
import et from '../locales/et.json'

export const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en,
    et
  }
})
