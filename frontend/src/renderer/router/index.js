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
    // {path: '/',             name: 'login',    component: PageLogin},
    {path: '/',             name: 'projects',    component: PageProjects},
    {path: '/app',          name: 'app',      component: PageApp},
    {path: '/register',     name: 'register', component: PageRegister},
    {path: '/restore-account',     name: 'restore-account', component: PageRestoreAccount},
    {path: '/projects',     name: 'projects', component: PageProjects },
    {path: '*', redirect: '/'}
  ],
});

router.beforeEach((to, from, next) => {
  setRouteTracking_HubSpot(to);
  Analytics.googleAnalytics.trackRouteChange(to);

  next();
});

const setRouteTracking_HubSpot = function(to) {
  const _hsq = window._hsq = window._hsq || [];

  if (_hsq.length === 0) {
    return;
  }

  if (to.path === '/') {
    _hsq.push(['setPath', '/']);
  } else {
    _hsq.push(['setPath', to.path]);
    _hsq.push(['trackPageView']);
  }
}


export default router;