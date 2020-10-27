import { requestCloudApi } from "@/core/apiCloud";
import {generateID} from "@/core/helpers";
import { createFolder as fileserver_createFolder } from '@/core/apiFileserver';
import { rygg } from '@/core/apiRygg.js';
const namespaced = true;

const state = {
  currentProject: parseInt(localStorage.getItem('targetProject')) || null, // maybe we should copy all project object instead id and did modification in this one in case it wouldn't save changes.
  projectsList: [],
  isDefaultProjectMode: false
};

const getters = {
  GET_project(state, getters, rootState, rootGetters) {
    return state.projectsList.filter(project => (project.project_id === state.currentProject))[0];
  },
  GET_projectPath(state, getters) {
    return getters['GET_project'] && getters['GET_project'].default_directory || '';
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
  }
}

const mutations = {
  setProjectList(state, payload){
    state.projectsList = payload;
  },
  selectProject(state, projectId) {
    localStorage.setItem('targetProject', projectId);
    state.currentProject = projectId;
  },
  createProject(state, payload) {
    state.projectsList.push(payload);
  },
  removeProjectIdInLocalStorage(state, projectId) {
    if (localStorage.getItem('targetProject') == projectId) {
      localStorage.removeItem('targetProject');
    }
  },
  setIsDefaultProjectMode(state) {
    let envValue = process.env.FORCE_DEFAULT_PROJECT;
    if (typeof envValue === 'undefined' || envValue === null) { return; }

    state.isDefaultProjectMode = envValue === 'true';
  }
};

const actions = {
  getProjects(ctx) {
    return rygg.get(`/projects`)
      .then((res) => {
        ctx.commit('setProjectList', res.data.results);
        return res;
      })
      .catch((error)=> {
        console.error(error); 
      })
    },
  createProject(ctx, payload) {
    return rygg.post(`/projects/`, payload)
      .then(res => {
        ctx.commit('createProject', res.data); 
        return res.data;
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
        ctx.commit('removeProjectIdInLocalStorage', payload.projectId);
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
        return res.data
      })
  },
  getDefaultModeProject(ctx) {
    
    return new Promise((resolve, reject) => {
      return ctx.dispatch('getProjects')
        .then(({data: { results: projects }}) => {

          const defaultProject = projects.find(p => p.name === 'Default');
          if (!defaultProject) {
            // create project called "Default" if it doesn't exist
            return ctx.dispatch('prepareDefaultProjectDirectory');
          }
          
          return defaultProject;    
        })
        .then(defaultProjectMeta => {
          ctx.commit('selectProject', defaultProjectMeta.project_id);
          // console.log('defaultProjectMeta', defaultProjectMeta);
          resolve();
        })
        .catch(error => reject(error));
      });
  },
  prepareDefaultProjectDirectory(ctx) {
    return fileserver_createFolder('~/Documents/Perceptilabs/Default')
      .then(createFolderRes => {
        if (!createFolderRes) { throw new Error('Problem while creating project directory'); }

        let createProjectReq = {
          name: 'Default',
          default_directory: createFolderRes
        };
        return ctx.dispatch('createProject', createProjectReq);
      })
      .then(createProjectRes => createProjectRes)
      .catch(error => {
        console.error(error)
      });
  },
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions
}
