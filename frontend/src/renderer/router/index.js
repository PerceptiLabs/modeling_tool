import Vue    from 'vue'
import Router from 'vue-router'

import PageApp  from '@/pages/app/app.vue';
import PageLogin    from '@/pages/login/login.vue';
import PageRegister from '@/pages/register/register.vue';
import PageRestoreAccount from '@/pages/restore-account/restore-account.vue';
import PageProjects from '@/pages/projects/projects.vue';

Vue.use(Router);

export default new Router({
  routes: [
    {path: '/',             name: 'login',    component: PageLogin},
    {path: '/app',          name: 'app',      component: PageApp},
    {path: '/register',     name: 'register', component: PageRegister},
    {path: '/restore-account',     name: 'restore-account', component: PageRestoreAccount},
    {path: '/projects',     name: 'projects', component: PageProjects },
    {path: '*', redirect: '/'}
  ]
})
