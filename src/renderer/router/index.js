import Vue    from 'vue'
import Router from 'vue-router'

// export const PageQuantum  = () => import(/* webpackChunkName: 'page-app' */ '@/pages/app/quantum.vue');
// export const PageLogin    = () => import(/* webpackChunkName: 'page-login' */ '@/pages/login/login.vue');
// export const PageRegister = () => import(/* webpackChunkName: 'page-register' */ '@/pages/register/register.vue');
// export const PagePolicy   = () => import(/* webpackChunkName: 'page-policy' */ '@/pages/policy/policy.vue');
// export const PageProjects = () => import(/* webpackChunkName: 'page-projects' */ '@/pages/projects/projects.vue');
import PageApp  from '@/pages/app/app.vue';
import PageLogin    from '@/pages/login/login.vue';
import PageRegister from '@/pages/register/register.vue';
import PagePolicy   from '@/pages/policy/policy.vue';
import PageProjects from '@/pages/projects/projects.vue';

Vue.use(Router);

export default new Router({
  routes: [
    {path: '/',             name: 'login',    component: PageLogin},
    {path: '/app',          name: 'app',      component: PageApp},
    {path: '/register',     name: 'register', component: PageRegister},
    {path: '/policy-page',  name: 'policy',   component: PagePolicy},
    {path: '/projects',     name: 'projects', component: PageProjects },
    {path: '*', redirect: '/'}
  ]
})
