import Vue    from 'vue'
import Router from 'vue-router'
import PageApp  from '@/pages/app/app.vue';
import PageRestoreAccount from '@/pages/restore-account/restore-account.vue';
import PageProjects from '@/pages/projects/projects.vue';

import Analytics from '@/core/analytics';
import {isWeb} from "@/core/helpers";

Vue.use(Router);
let routerOptions = {};
let routesElectron = [];
if (!(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1)) {
  routerOptions.mode = 'history';
}

const router = new Router({
  ...routerOptions,
  routes: [
    ...routesElectron,
    {path: '/',             name: 'projects',    component: PageProjects},
    {path: '/app',          name: 'app',      component: PageApp},
    // {path: '/restore-account',     name: 'restore-account', component: PageRestoreAccount},
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