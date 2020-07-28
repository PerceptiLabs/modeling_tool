import Vue    from 'vue'
import Router from 'vue-router'
import PageApp  from '@/pages/app/app.vue';
import PageRestoreAccount from '@/pages/restore-account/restore-account.vue';
import PageProjects from '@/pages/projects/projects.vue';
import SettingPage from '@/pages/settings/setting-page.vue';

import Analytics from '@/core/analytics';
import {isWeb} from "@/core/helpers";
import store from '@/store'
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
    {path: '/',             name: 'main-page',    component: PageProjects},
    {path: '/app',          name: 'app',      component: PageApp},
    // {path: '/restore-account',     name: 'restore-account', component: PageRestoreAccount},
    {path: '/projects',     name: 'projects', component: PageProjects },
    {path: '/settings',     name: 'settings', component: SettingPage },
    {path: '*', redirect: '/'}
  ],
});

router.beforeEach((to, from, next) => {
  // if(from.name === "app") {
  //   // store.commit('mod_workspace/set_workspacesInLocalStorage');

    // console.log('router.beforeEach - updateWorkspaces');
    // store.dispatch('mod_webstorage/updateWorkspaces', null, { root: true });
  // }
  if(isWeb()) {
    Analytics.googleAnalytics.trackRouteChange(to); 
  }
  next();
});

export default router;