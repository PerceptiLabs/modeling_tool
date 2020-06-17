import { requestCloudApi } from "@/core/apiCloud";
import {generateID} from "@/core/helpers";
import axios from 'axios';
const namespaced = true;

const state = {
  currentProject: parseInt(localStorage.getItem('targetProject')) || null, // maybe we should copy all project object instead id and did modification in this one in case it wouldn't save changes.
  projectsList: [],
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
  removeProjectIdInLocalStorage(start, projectId) {
    if (localStorage.getItem('targetProject') == projectId) {
      localStorage.removeItem('targetProject');
    }
  }
};

const actions = {
  getProjects(ctx) {
    return axios.get('http://localhost:8000/projects')
      .then((res) => {
        ctx.commit('setProjectList', res.data.results);
        return res;
      })
      .catch((error)=> {
        console.error(error); 
      })
    },
  createProject(ctx, payload) {
    return axios.post('http://localhost:8000/projects/', payload)
      .then(res => {
        ctx.commit('createProject', res.data); 
        return res.data;
      })
  },
  updateProject(ctx, payload) {
    const {projectId, ...postData} = payload;
    return axios.patch(`http://localhost:8000/projects/${projectId}/`, postData)
      .then(res => {
        ctx.dispatch('getProjects');
        return res.data;
      })
  },
  deleteProject(ctx, payload) {
    return axios.delete(`http://localhost:8000/projects/${payload.projectId}/`)
      .then(res => {
        ctx.commit('removeProjectIdInLocalStorage', payload.projectId);
        ctx.dispatch('getProjects');
      })  
      .catch(e => console.log(e));
  },
  getModel(ctx, modelId) {
    return axios.get(`http://localhost:8000/models/${modelId}/`)
      .then(res => res.data)
      .catch(console.error)
  },
  async getProjectModels({getters, dispatch}){
    const projectModesIds = getters['GET_projectModelIds'];
    let projectModesPromises = projectModesIds.map(modelId => dispatch('getModel', modelId))
    const models = await Promise.all(projectModesPromises);
    return models;
  },
  updateModel(ctx, payload) {
    const { modelId, ...body } = payload;
    return axios.put(`http://localhost:8000/models/${modelId}/`, body)
  },
  createProjectModel(ctx, payload) {
    return axios.post('http://localhost:8000/models/', payload)
      .then(res => {
        return res.data
      })
  },
  updateModel(ctx, payload) {
    const { model_id, ...payloadData } = payload
    return axios.put(`http://localhost:8000/models/${model_id}/`, payloadData)
  },
  deleteModel(ctx, payload) {
    const { model_id, project } = payload;
    return axios.delete(`http://localhost:8000/models/${model_id}/`)
      .then(res => {
        ctx.dispatch('getProjects');
        return res.data
      })
  }
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions
}
