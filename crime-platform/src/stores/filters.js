import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useFiltersStore = defineStore('filters', () => {
  const selectedCrimeType = ref('ICCS0101')
  const selectedYear = ref(2023)
  const selectedCountries = ref([])
  const metric = ref('per100k')

  const years = computed(() => {
    const arr = []
    for (let y = 2008; y <= 2023; y++) {
      arr.push(y)
    }
    return arr
  })

  const crimeCategories = ref({
    violence: {
      label: 'Violence',
      crimes: [
        { code: 'ICCS0101', label: 'Intentional homicide' },
        { code: 'ICCS0102', label: 'Attempted intentional homicide' },
        { code: 'ICCS020111', label: 'Serious assault' },
        { code: 'ICCS020221', label: 'Kidnapping' },
        { code: 'ICCS0401', label: 'Robbery' }
      ]
    },
    sexual: {
      label: 'Sexual Crimes',
      crimes: [
        { code: 'ICCS0301', label: 'Sexual violence' },
        { code: 'ICCS03011', label: 'Rape' },
        { code: 'ICCS03012', label: 'Sexual assault' },
        { code: 'ICCS030221', label: 'Child pornography' },
        { code: 'ICCS0302', label: 'Sexual exploitation' }
      ]
    },
    property: {
      label: 'Property',
      crimes: [
        { code: 'ICCS0501', label: 'Burglary' },
        { code: 'ICCS05012', label: 'Burglary of private residential premises' },
        { code: 'ICCS0502', label: 'Theft' },
        { code: 'ICCS05021', label: 'Theft of motorized vehicles' }
      ]
    },
    drugs: {
      label: 'Drugs',
      crimes: [
        { code: 'ICCS0601', label: 'Unlawful acts involving controlled drugs' }
      ]
    },
    financial: {
      label: 'Financial',
      crimes: [
        { code: 'ICCS0701', label: 'Fraud' },
        { code: 'ICCS0703', label: 'Corruption' },
        { code: 'ICCS07031', label: 'Bribery' },
        { code: 'ICCS07041', label: 'Money laundering' }
      ]
    },
    cyber: {
      label: 'Cyber',
      crimes: [
        { code: 'ICCS0903', label: 'Acts against computer systems' },
        { code: 'ICCS09051', label: 'Organized criminal group participation' }
      ]
    },
    environmental: {
      label: 'Environmental',
      crimes: [
        { code: 'ICCS1001', label: 'Environmental crimes' }
      ]
    }
  })

  function setCrimeType(crimeType) {
    selectedCrimeType.value = crimeType
  }

  function setYear(year) {
    selectedYear.value = year
  }

  function setCountries(countries) {
    selectedCountries.value = countries
  }

  function setMetric(newMetric) {
    metric.value = newMetric
  }

  function resetFilters() {
    selectedCrimeType.value = 'ICCS0101'
    selectedYear.value = 2023
    selectedCountries.value = []
    metric.value = 'per100k'
  }

  return {
    selectedCrimeType,
    selectedYear,
    selectedCountries,
    metric,
    years,
    crimeCategories,
    setCrimeType,
    setYear,
    setCountries,
    setMetric,
    resetFilters
  }
})
