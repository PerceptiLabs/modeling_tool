import Vue    from 'vue'
import Router from 'vue-router'
import PageApp  from '@/pages/app/app.vue';
import PageProjects from '@/pages/projects/projects.vue';
import SettingPage from '@/pages/settings/setting-page.vue';
import Test from '@/pages/test/test.vue';
import ExportPage from '@/pages/export/export.vue';

import Analytics from '@/core/analytics';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  routes: [
    {path: '/',               name: 'main-page',      component: PageProjects},
    {path: '/app',            name: 'app',            component: PageApp},
    {path: '/test',           name: 'test',           component: Test},
    {path: '/projects',       name: 'projects',       component: PageProjects },
    {path: '/settings',       name: 'settings',       component: SettingPage },
    {path: '/export',         name: 'export',         component: ExportPage },
    {path: '*', redirect: '/'}
  ],
});

router.beforeEach((to, from, next) => {
  Analytics.googleAnalytics.trackRouteChange(to); 
  next();
});

export default router;