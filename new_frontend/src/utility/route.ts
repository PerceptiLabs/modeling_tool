import { RouteParams } from "vue-router";

export function getNavbarComponentName(routeParams: RouteParams) {
  if (routeParams.projectId === null || routeParams.projectId === undefined) {
    return "NavSidebarProjectOverView";
  } else {
    return "NavSidebarProjectDetail";
  }
}
