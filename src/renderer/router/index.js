import Vue    from 'vue'
import Router from 'vue-router'

import PageQuantum  from '@/pages/app/quantum.vue'
import PageLogin    from '@/pages/login/login.vue'
import PageRegister from '@/pages/register/register.vue'
import PagePolicy   from '@/pages/policy/policy.vue'
import PageProjects from '@/pages/projects/projects.vue'

Vue.use(Router);

export default new Router({
  routes: [
    {path: '/',             name: 'login',    component: PageLogin},
    {path: '/app',          name: 'app',      component: PageQuantum},
    {path: '/register',     name: 'register', component: PageRegister},
    {path: '/policy-page',  name: 'policy',   component: PagePolicy},
    {path: '/projects',     name: 'projects', component: PageProjects },
    {path: '*', redirect: '/'}
  ]
})
