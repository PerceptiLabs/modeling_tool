import Vue    from 'vue'
import Router from 'vue-router'

import PageQuantum  from '@/pages/app/quantum.vue'
import PageLogin    from '@/pages/login/login.vue'
import PageRegister from '@/pages/register/register.vue'
import PagePolicy   from '@/pages/policy/policy.vue'

Vue.use(Router)

export default new Router({
  //mode: 'history',
  routes: [
    { path: '/',          name: 'login',    component: PageLogin },
    { path: '/register',  name: 'register', component: PageRegister },
    { path: '/policy-page',    name: 'policy',   component: PagePolicy },
    { path: '/app',       name: 'app',  component: PageQuantum },
    { path: '*', redirect: '/'
    }
  ]
})
