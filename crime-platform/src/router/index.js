import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Explorer from '../pages/Explorer.vue'
import Country from '../pages/Country.vue'
import About from '../pages/About.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/explorer',
    name: 'Explorer',
    component: Explorer
  },
  {
    path: '/country/:code',
    name: 'Country',
    component: Country
  },
  {
    path: '/about',
    name: 'About',
    component: About
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
