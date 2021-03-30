import { Action, Module, Mutation, VuexModule } from "vuex-module-decorators";

import { rygg as ryggRequest } from "@/core/request/index";
import { IModel } from "@/types";

@Module({
  name: "mod_models",
  namespaced: true,
})
export default class ModelssModule extends VuexModule {
  models: { [modelId: number]: IModel } = {};

  @Mutation
  setModels(models: Array<IModel>) {
    this.models = models.reduce(
      (arr, project) => ({ ...arr, [project.modelId]: project }),
      {},
    );
  }

  @Action({
    commit: "setModels",
    rawError: true,
  })
  async getModels() {
    return await ryggRequest.getModels();
  }

  @Mutation
  setModel(project: IModel) {
    this.models[project.modelId] = project;
  }

  @Action({ commit: "setModel", rawError: true })
  async getModel(modelId: number) {
    return await ryggRequest.getModel(modelId);
  }
}
