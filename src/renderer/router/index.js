import Vue from 'vue'
import Router from 'vue-router'
import PageQuantum from '@/pages/app/quantum.vue'
//  import PageLogin from '@/pages/login/login.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    { path: '/quantum', name: 'landing-page', component: require('@/components/LandingPage').default },
    { path: '/', name: 'quantum', component: PageQuantum },
    //  { path: '/login', name: 'login', component: PageLogin },
    { path: '*', redirect: '/'
    }
  ]
})
