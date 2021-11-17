import { requestCloudApi } from "@/core/apiCloud";
import { generateID } from "@/core/helpers";
import { createFolder as rygg_createFolder } from '@/core/apiRygg';
import { isEnterpriseApp as rygg_isEnterpriseApp } from '@/core/apiRygg';
import { createProjectWithDefaultDir as rygg_createProjectWithDefaultDir } from '@/core/apiRygg';
import { rygg } from '@/core/apiRygg.js';
import { LOCAL_STORAGE_CURRENT_PROJECT } from "@/core/constants";
const namespaced = true;
const DEFAULT_PROJECT_NAME = 'Default';
const DEFAULT_LOCAL_PROJECT_DIR = '~/Documents/Perceptilabs/Default';

const state = {
  currentProject: parseInt(localStorage.getItem(LOCAL_STORAGE_CURRENT_PROJECT)) || null, // maybe we should copy all project object instead id and did modification in this one in case it wouldn't save changes.
  projectsList: [],
  isDefaultProjectMode: false
};

const getters = {
  GET_project(state, getters, rootState, rootGetters) {
    return state.projectsList.filter(project => (project.project_id === state.currentProject))[0];
  },
  GET_projectPath(state, getters) {
    const proj = getters['GET_project'];
    return proj && proj.default_directory || '';
  },
  GET_projectModelIds(state){
   return state.projectsList.filter(project => (project.project_id === state.currentProject))[0].models;
  },
  GET_isProjectWithThisDirectoryExist: (state) => (default_directory) => {
    const projectDirectoryesList = state.projectsList.map(pr => pr.default_directory);
    const projectExists = projectDirectoryesList.indexOf(default_directory) !== -1;

    return projectExists;
  },
  GET_isDefaultProjectMode(state) {
    return state.isDefaultProjectMode;
  },
  GET_isProjectSelected(state) {
    if (!localStorage.hasOwnProperty(LOCAL_STORAGE_CURRENT_PROJECT)){
      return false
    }
    const proj = localStorage.getItem(LOCAL_STORAGE_CURRENT_PROJECT)
    return proj === parseInt(proj) && proj > 0;
  },
}

const mutations = {
  setProjectList(state, payload){
    state.projectsList = payload;
  },
  selectProject(state, projectId) {
    if (projectId !== parseInt(projectId, 10)){
      throw new Error(`Invalid ${LOCAL_STORAGE_CURRENT_PROJECT}`);
    }
    localStorage.setItem(LOCAL_STORAGE_CURRENT_PROJECT, projectId);
    state.currentProject = projectId;
  },
  addProjectToList(state, payload) {
    state.projectsList.push(payload);
  },
  removeProjectIdInLocalStorage(state) {
    if (localStorage.getItem(LOCAL_STORAGE_CURRENT_PROJECT) == projectId) {
      localStorage.removeItem(LOCAL_STORAGE_CURRENT_PROJECT);
    }
  },
  setIsDefaultProjectMode(state) {
    let envValue = process.env.FORCE_DEFAULT_PROJECT;
    if (typeof envValue === 'undefined' || envValue === null) { return; }

    state.isDefaultProjectMode = envValue === 'true';
  }
};

const actions = {
  getProject(ctx, project_id) {
    return rygg.get(`/projects/${project_id}/`)
      .then((res) => res)
      .catch((error)=> {
        console.error(error);
      })
    },
  getProjects(ctx) {
    return rygg.get(`/projects/`)
      .then((res) => {
        ctx.commit('setProjectList', res.data.results);
        return res;
      })
      .catch((error)=> {
        console.error(error);
      })
    },
  updateProject(ctx, payload) {
    const {projectId, ...postData} = payload;
    return rygg.patch(`/projects/${projectId}/`, postData)
      .then(res => {
        ctx.dispatch('getProjects');
        return res.data;
      })
  },
  deleteProject(ctx, payload) {
    return rygg.delete(`/projects/${payload.projectId}/`)
      .then(res => {
        ctx.commit('removeProjectIdInLocalStorage');
        ctx.dispatch('getProjects');
      })
      .catch(e => console.log(e));
  },
  getModel(ctx, modelId) {
    return rygg.get(`/models/${modelId}/`)
      .then(res => res.data)
      .catch(console.error)
  },
  async getProjectModels({getters, dispatch}){
    const projectModesIds = getters['GET_projectModelIds'];
    let projectModesPromises = projectModesIds.map(modelId => dispatch('getModel', modelId))
    const models = await Promise.all(projectModesPromises);
    return models;
  },
  createProjectModel(ctx, payload) {
    return rygg.post(`/models/`, payload)
      .then(res => {
        return res.data
      })
  },
  updateModel(ctx, payload) {
    const { model_id, ...payloadData } = payload
    return rygg.put(`/models/${model_id}/`, payloadData)
  },
  patchModel(ctx, payload) {
    const { model_id, ...payloadData } = payload;
    return rygg.patch(`/models/${model_id}/`, payloadData);
  },
  deleteModel(ctx, payload) {
    const { model_id, project } = payload;

    return rygg.delete(`/models/${model_id}/`)
      .then(res => {
        ctx.dispatch('getProjects');
        ctx.dispatch('mod_webstorage/deleteTestStatisticByModelId', [model_id], {root: true});
        return res.data
      })
  },
  async getDefaultModeProject(ctx) {
    const {data: { results: projects }} = await ctx.dispatch('getProjects');

    // TODO: this won't scale in enterprise. Only do O(n) call to find() in local mode.
    let defaultProject = projects.find(p => p.name === DEFAULT_PROJECT_NAME);

    if (!defaultProject) {
      let req = await rygg_isEnterpriseApp() ?
        { name: DEFAULT_PROJECT_NAME } :
        { name: DEFAULT_PROJECT_NAME, default_directory: DEFAULT_LOCAL_PROJECT_DIR };
      defaultProject = await ctx.dispatch('createProject', req);
    }

    await ctx.commit('selectProject', defaultProject.project_id);
    return defaultProject;
  },
  async createProject(ctx, { name, default_directory }) {
    const createProjectRes = await rygg_createProjectWithDefaultDir(name, default_directory);
    if (!createProjectRes) {
      throw new Error('Problem while creating project.');
    }
    ctx.commit("addProjectToList", createProjectRes.data)

    return createProjectRes.data
  },
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions
}
