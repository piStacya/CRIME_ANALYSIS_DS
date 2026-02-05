import { useI18n } from 'vue-i18n'

export function useTranslations() {
  const { locale } = useI18n()

  const getCountryName = (country) => {
    if (!country) return ''
    if (locale.value === 'et' && country.nameEt) {
      return country.nameEt
    }
    return country.name || ''
  }

  const getCountryNameByCode = (code, countriesMetadata) => {
    if (!countriesMetadata || !code) return code
    const country = countriesMetadata.find(c => c.code === code)
    if (!country) return code
    return getCountryName(country)
  }

  const getCrimeName = (crime) => {
    if (!crime) return ''
    if (locale.value === 'et' && crime.nameEt) {
      return crime.nameEt
    }
    return crime.name || ''
  }

  const getCrimeNameByCode = (code, crimesMetadata) => {
    if (!crimesMetadata || !code) return code
    const crime = crimesMetadata.find(c => c.code === code)
    if (!crime) return code
    return getCrimeName(crime)
  }

  const getCategoryLabel = (category) => {
    if (!category) return ''
    if (locale.value === 'et' && category.labelEt) {
      return category.labelEt
    }
    return category.label || ''
  }

  return {
    locale,
    getCountryName,
    getCountryNameByCode,
    getCrimeName,
    getCrimeNameByCode,
    getCategoryLabel
  }
}
