import Vue    from 'vue'
import Router from 'vue-router'

import PageApp  from '@/pages/app/app.vue';
import PageLogin    from '@/pages/login/login.vue';
import PageRegister from '@/pages/register/register.vue';
import PageRestoreAccount from '@/pages/restore-account/restore-account.vue';
import PageProjects from '@/pages/projects/projects.vue';

import Analytics from '@/core/analytics';
import {isWeb} from "@/core/helpers";

Vue.use(Router);
let routerOptions = {};

if (!(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1)) {
  routerOptions.mode = 'history';
}

const router = new Router({
  ...routerOptions,
  routes: [
    {path: '/',             name: 'login',    component: PageLogin},
    {path: '/',             name: 'projects',    component: PageProjects},
    {path: '/app',          name: 'app',      component: PageApp},
    {path: '/register',     name: 'register', component: PageRegister},
    {path: '/restore-account',     name: 'restore-account', component: PageRestoreAccount},
    {path: '/projects',     name: 'projects', component: PageProjects },
    {path: '*', redirect: '/'}
  ],
});

router.beforeEach((to, from, next) => {
  if(isWeb()) {
    Analytics.hubSpot.trackRouteChange(to);
    Analytics.googleAnalytics.trackRouteChange(to); 
  }
  next();
});

export default router;