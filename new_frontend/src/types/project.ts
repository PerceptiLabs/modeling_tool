export interface IProject {
  projectId: number;
  name: string;
  defaultDirectory: string;
  created: string;
  updated: string;
  models: Array<number>; // array of model IDs
  notebooks: Array<any>;
}
