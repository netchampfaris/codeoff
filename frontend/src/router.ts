import { createRouter, createWebHistory } from 'vue-router'
import { session } from './data/session'

const router = createRouter({
  history: createWebHistory(__FRONTEND_ROUTE__ + '/'),
  routes: [
    {
      path: '/',
      redirect: () => (session.isLoggedIn ? '/home' : '/spectate'),
    },
    {
      path: '/home',
      name: 'Home',
      component: () => import('@/pages/Home.vue'),
    },
    {
      path: '/spectate',
      name: 'SpectateHome',
      component: () => import('@/pages/SpectateHome.vue'),
      meta: { public: true },
    },
    {
      path: '/match/:matchId',
      name: 'MatchWorkspace',
      component: () => import('@/pages/MatchWorkspace.vue'),
      props: true,
    },
    {
      path: '/spectate/:matchId',
      name: 'Spectate',
      component: () => import('@/pages/Spectate.vue'),
      props: true,
      meta: { public: true },
    },
  ],
})

router.beforeEach((to, from) => {
  if (to.meta?.public) return true
  if (to.name !== 'Login' && !session.isLoggedIn) {
    window.location.href = '/login'
    return false
  }
})

export default router
