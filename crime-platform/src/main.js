import { createApp } from 'vue'
import { pinia } from './stores'
import { i18n } from './i18n'
import router from './router'
import App from './App.vue'
import './style.css'

const app = createApp(App)

app.use(pinia)
app.use(i18n)
app.use(router)

app.mount('#app')
