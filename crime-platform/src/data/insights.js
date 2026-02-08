export const insights = [
  {
    id: 'property-crime-decline',
    category: 'declining',
    countries: [],
    explorer: true
  },
  {
    id: 'modern-crime-rise',
    category: 'rising',
    countries: [],
    explorer: true
  },
  {
    id: 'sexual-violence-reporting',
    category: 'context',
    countries: ['SE', 'NO', 'LU', 'IE', 'IS', 'DE', 'FR', 'DK', 'BE', 'AT'],
    explorer: true
  },
  {
    id: 'baltic-homicide-decline',
    category: 'declining',
    countries: ['LT', 'EE', 'LV'],
    explorer: true
  },
  {
    id: 'post-covid-surge',
    category: 'rising',
    countries: [],
    explorer: true
  },
  {
    id: 'fraud-replacing-theft',
    category: 'shift',
    countries: ['ES', 'PL'],
    explorer: false
  },
  {
    id: 'small-country-effect',
    category: 'context',
    countries: ['LI'],
    explorer: true
  },
  {
    id: 'finland-cybercrime',
    category: 'rising',
    countries: ['FI'],
    explorer: false
  },
  {
    id: 'drugs-top-crime',
    category: 'shift',
    countries: ['AL', 'CY', 'MK'],
    explorer: false
  }
]

export function getCountryInsights(countryCode) {
  return insights.filter(i => i.countries.includes(countryCode))
}

export function getExplorerInsights() {
  return insights.filter(i => i.explorer)
}
