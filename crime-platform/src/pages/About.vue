<script setup>
// About page - Methodology, data sources, team info
</script>

<template>
  <div class="about">
    <h1>{{ $t('about.title') }}</h1>

    <section class="section">
      <h2>{{ $t('about.methodology.title') }}</h2>
      <p>{{ $t('about.methodology.content') }}</p>
    </section>

    <section class="section">
      <h2>{{ $t('about.dataSources.title') }}</h2>
      <p>{{ $t('about.dataSources.content') }}</p>
      <ul class="source-list">
        <li>
          <strong>Eurostat</strong> - European crime statistics database
        </li>
        <li>
          <strong>Time period:</strong> 2008-2023 (16 years)
        </li>
        <li>
          <strong>Coverage:</strong> 39 European countries
        </li>
        <li>
          <strong>Categories:</strong> 25 crime types
        </li>
      </ul>
    </section>

    <section class="section">
      <h2>{{ $t('about.scope.title') }}</h2>
      <p>{{ $t('about.scope.content') }}</p>
    </section>

    <section class="section">
      <h2>{{ $t('about.team.title') }}</h2>
      <p>{{ $t('about.team.content') }}</p>
    </section>
  </div>
</template>

<style scoped>
.about {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.about h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 2rem;
}

.section {
  margin-bottom: 2.5rem;
}

.section h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
}

.section p {
  color: #4a5568;
  line-height: 1.7;
}

.source-list {
  margin-top: 1rem;
  padding-left: 1.5rem;
}

.source-list li {
  color: #4a5568;
  margin-bottom: 0.5rem;
}
</style>
