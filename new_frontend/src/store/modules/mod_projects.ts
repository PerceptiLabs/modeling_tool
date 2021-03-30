import { Action, Module, Mutation, VuexModule } from "vuex-module-decorators";

import { rygg as ryggRequest } from "@/core/request/index";
import { IProject } from "@/types";

@Module({
  name: "mod_projects",
  namespaced: true,
})
export default class ProjectsModule extends VuexModule {
  projects: { [projectId: number]: IProject } = {};

  @Mutation
  setProjects(projects: Array<IProject>) {
    this.projects = projects.reduce(
      (arr, project) => ({ ...arr, [project.projectId]: project }),
      {},
    );
  }

  @Action({
    commit: "setProjects",
    rawError: true,
  })
  async getProjects() {
    return await ryggRequest.getProjects();
  }

  @Mutation
  setProject(project: IProject) {
    this.projects[project.projectId] = project;
  }

  @Action({ commit: "setProject", rawError: true })
  async getProject(projectId: number) {
    return await ryggRequest.getProject(projectId);
  }
}
