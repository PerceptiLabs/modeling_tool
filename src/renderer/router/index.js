import Vue    from 'vue'
import Router from 'vue-router'

import PageQuantum  from '@/pages/app/quantum.vue'
import PageLogin    from '@/pages/login/login.vue'
import PageRegister from '@/pages/register/register.vue'
import PagePolicy   from '@/pages/policy/policy.vue'
import PageProjects from '@/pages/projects/projects.vue'

Vue.use(Router);

var home = {};
var app = {};
if(process.env.NODE_ENV === 'production') {
  home = {path: '/',  name: 'login', component: PageLogin};
  app = {path: '/app',name: 'app',   component: PageQuantum};
}
else {
  home = {path: '/',  name: 'app', component: PageQuantum};
  app = {path: '/login',name: 'login',   component: PageLogin};
}


export default new Router({
  //mode: 'history',
  routes: [
    {...home},
    {...app},
    {path: '/register',     name: 'register', component: PageRegister},
    {path: '/policy-page',  name: 'policy',   component: PagePolicy},
    {path: '/projects',     name: 'projects', component: PageProjects },
    {path: '*', redirect: '/'}
  ]
})
