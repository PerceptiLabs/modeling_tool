import Vue from 'vue'
import Router from 'vue-router'
import PageApp from '@/pages/app/app.vue'
//  import PageLogin from '@/pages/login/login.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    { path: '/', name: 'landing-page', component: require('@/components/LandingPage').default },
    { path: '/app', name: 'app', component: PageApp },
    //  { path: '/login', name: 'login', component: PageLogin },
    { path: '*', redirect: '/'
    }
  ]
})
