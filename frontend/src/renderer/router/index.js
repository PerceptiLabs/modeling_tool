import Vue    from 'vue'
import Router from 'vue-router'
import store  from '@/store'

import PageApp  from '@/pages/app/app.vue';
import PageLogin    from '@/pages/login/login.vue';
import PageRegister from '@/pages/register/register.vue';
import PageRestoreAccount from '@/pages/restore-account/restore-account.vue';
import PageProjects from '@/pages/projects/projects.vue';

import Analytics from '@/core/analytics';
import {isWeb} from "@/core/helpers";

Vue.use(Router);
let routerOptions = {};
let routesElectron = [];
if (!(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1)) {
  routerOptions.mode = 'history';
} else {
  routesElectron.push({path: '/', name: 'login',    component: PageLogin});
}

const authorizeRoutes = [
  {path: '/',                 name: 'home',             component: PageProjects},
  {path: '/app',              name: 'app',              component: PageApp},
  {path: '/restore-account',  name: 'restore-account',  component: PageRestoreAccount},
  {path: '/projects',         name: 'projects',         component: PageProjects },
];

const unauthorizedRoutes = [
  {path: '/login',            name: 'login',            component: PageLogin},
  {path: '/register',         name: 'register',         component: PageRegister},
];

const authorizeRoutesNames = authorizeRoutes.map(route => route.name);
const unauthorizedRoutesNames = unauthorizedRoutes.map(route => route.name);


const router = new Router({
  ...routerOptions,
  routes: [
    ...authorizeRoutes,
    ...unauthorizedRoutes,
    {path: '*', redirect: '/'}
  ],
});

router.beforeEach((to, from, next) => {
  const isAuthorized = !!store.state.mod_user.userToken.length;
  if(isAuthorized) {
    if(authorizeRoutesNames.includes(to.name)) {
      next(); 
    } else if (unauthorizedRoutesNames.includes(to.name)) {
      next({name: 'home'})
    }
  } else if(!isAuthorized) {
    if(unauthorizedRoutesNames.includes(to.name)) {
      next();
    } else if(authorizeRoutesNames.includes(to.name)) {
      next({name: 'register'});
    }
  }
  
  Analytics.hubSpot.trackRouteChange(to);
  Analytics.googleAnalytics.trackRouteChange(to);
});

export default router;