import { HttpRequest } from "./http";
import { RYGG_BASE_URL, RYGG_URL_CONFIG_PATH } from "../../config/constants";
import { IProject, IModel } from "@/types";

export class RyggRequest extends HttpRequest {
  constructor() {
    super(RYGG_URL_CONFIG_PATH, RYGG_BASE_URL);
  }

  // Projects
  async getProjects(): Promise<Array<IProject>> {
    const res = await this.get<{
      count: number;
      next: IProject;
      previous: IProject;
      results: Array<IProject>;
    }>("/projects");
    return res.results;
  }

  async getProject(projectId: number): Promise<IProject> {
    const res = await this.get<IProject>(`/projects/${projectId}`);
    return res;
  }

  // Models
  async getModels(): Promise<Array<IModel>> {
    const res = await this.get<{
      count: number;
      next: IModel;
      previous: IModel;
      results: Array<IModel>;
    }>("/models");
    return res.results;
  }

  async getModel(modelId: number): Promise<IModel> {
    const res = await this.get<IModel>(`/models/${modelId}`);
    return res;
  }
}
