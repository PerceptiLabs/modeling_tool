import Vue    from 'vue'
import Router from 'vue-router'
import PageApp  from '@/pages/app/app.vue';
import PageProjects from '@/pages/projects/projects.vue';
import SettingPage from '@/pages/settings/setting-page.vue';
import TestCreate from '@/pages/test-create/test-create.vue';
import TestDashboard from '@/pages/test-dashboard/test-dashboard.vue';

import Analytics from '@/core/analytics';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  routes: [
    {path: '/',               name: 'main-page',      component: PageProjects},
    {path: '/app',            name: 'app',            component: PageApp},
    {path: '/test-create',    name: 'test-create',    component: TestCreate},
    {path: '/test-dashboard', name: 'test-dashboard', component: TestDashboard},
    {path: '/projects',       name: 'projects',       component: PageProjects },
    {path: '/settings',       name: 'settings',       component: SettingPage },
    {path: '*', redirect: '/'}
  ],
});

router.beforeEach((to, from, next) => {
  Analytics.googleAnalytics.trackRouteChange(to); 
  next();
});

export default router;