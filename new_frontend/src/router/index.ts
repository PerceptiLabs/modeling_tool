import env from "@/config/env";
import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import RootLayout from "@/views/Layout.vue";
import Page404 from "@/views/common/404.vue";
import TestView from "@/views/Test.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    component: RootLayout,
    children: [
      {
        path: "",
        component: () => import("@/views/main/MainLayout.vue"),
        children: [
          {
            path: "",
            redirect: "projects",
          },
          {
            path: "projects",
            name: "ProjectsView",
            component: () => import("@/views/main/ProjectsView.vue"),
          },
          {
            path: "settings",
            name: "SettingsView",
            component: () => import("@/views/main/SettingsView.vue"),
          },
        ],
      },
      {
        path: "projects/:projectId",
        component: () => import("@/views/project/ProjectLayout.vue"),
        children: [
          {
            path: "",
            redirect: { name: "ModelsView" },
          },
          {
            path: "models",
            component: () => import("@/views/project/model/ModelLayout.vue"),
            children: [
              {
                path: "",
                name: "ModelsView",
                component: () => import("@/views/project/model/ModelsView.vue"),
              },
              {
                path: ":modelId",
                name: "ModelView",
                component: () => import("@/views/project/model/ModelView.vue"),
              },
            ],
          },
          {
            path: "data",
            name: "DataView",
            component: () => import("@/views/project/data/DataView.vue"),
          },
          {
            path: "test",
            name: "TestView",
            component: () => import("@/views/project/test/TestView.vue"),
          },
          {
            path: "system",
            name: "SystemView",
            component: () => import("@/views/project/system/SystemView.vue"),
          },
        ],
      },
    ],
  },
  {
    path: "/404",
    name: "404 Page",
    component: Page404,
  },
  env.NODE_ENV === "development"
    ? {
        path: "/test",
        component: TestView,
      }
    : {
        path: "/test",
        redirect: { name: "404 Page" },
      },
  {
    path: "/:pathMatch(.*)",
    redirect: { name: "404 Page" },
  },
];

const router = createRouter({
  history: createWebHistory(env.BASE_URL),
  routes,
});

export default router;
