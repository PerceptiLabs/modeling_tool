import { HttpRequest } from "./http";
import { RYGG_BASE_URL, RYGG_URL_CONFIG_PATH } from "../../config/constants";
import { IProject } from "@/types";

export class RyggRequest extends HttpRequest {
  constructor() {
    super(RYGG_URL_CONFIG_PATH, RYGG_BASE_URL);
  }

  // Projects CRUD
  async getProjects(): Promise<Array<IProject>> {
    const res = await this.get<{
      count: number;
      next: IProject;
      previous: IProject;
      results: Array<IProject>;
    }>("/projects");
    return res.results;
  }

  // async createProjects() {}
}
