import Vue    from 'vue'
import Router from 'vue-router'

import PageApp  from '@/pages/app/app.vue';
import PageLogin    from '@/pages/login/login.vue';
import PageRegister from '@/pages/register/register.vue';
import PageRestoreAccount from '@/pages/restore-account/restore-account.vue';
import PageProjects from '@/pages/projects/projects.vue';

import Analytics from '@/core/analytics';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  routes: [
    {path: '/',     name: 'home', component: PageRegister},
    // {path: '/',             name: 'projects',    component: PageProjects},
    {path: '/login',             name: 'login',    component: PageLogin},
    {path: '/app',          name: 'app',      component: PageApp},
    {path: '/restore-account',     name: 'restore-account', component: PageRestoreAccount},
    {path: '/projects',     name: 'projects', component: PageProjects },
    {path: '/register',     name: 'register', component: PageRegister},
    {path: '*', redirect: '/'}
  ],
});

router.beforeEach((to, from, next) => {

  Analytics.hubSpot.trackRouteChange(to);
  Analytics.googleAnalytics.trackRouteChange(to);

  next();
});

export default router;