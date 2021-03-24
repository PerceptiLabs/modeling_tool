import { Action, Module, Mutation, VuexModule } from "vuex-module-decorators";

import { rygg as ryggRequest } from "@/core/request/index";
import { IProject } from "@/types";

@Module({
  name: "mod_projects",
  namespaced: true,
})
export default class ProjectsModule extends VuexModule {
  projects: Array<IProject> = [];

  @Mutation
  setProjects(projects: Array<IProject>) {
    this.projects = projects;
  }

  @Action({ commit: "setProjects" })
  async getProjects() {
    return await ryggRequest.getProjects();
  }
}
