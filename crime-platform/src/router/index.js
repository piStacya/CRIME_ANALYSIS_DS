import { createRouter, createWebHistory } from 'vue-router'
import Landing from '../pages/Landing.vue'
import Home from '../pages/Home.vue'
import Explorer from '../pages/Explorer.vue'
import Country from '../pages/Country.vue'
import Compare from '../pages/Compare.vue'
import About from '../pages/About.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: Landing
  },
  {
    path: '/home',
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
    path: '/compare',
    name: 'Compare',
    component: Compare
  },
  {
    path: '/about',
    name: 'About',
    component: About
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.path === '/' && sessionStorage.getItem('hasVisited') === 'true') {
    next('/home')
  } else {
    next()
  }
})

export default router
