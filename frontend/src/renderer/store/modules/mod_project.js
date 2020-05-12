import { requestCloudApi } from "@/core/apiCloud";
import {generateID} from "@/core/helpers";
import axios from 'axios';
import Vue    from 'vue'
const namespaced = true;

const state = {
  currentProject: parseInt(localStorage.getItem('targetProject')) || null, // maybe we should copy all project object instead id and did modification in this one in case it wouldn't save changes.
  projectsList: {},
  // newProjectsList: {},
};

const mutations = {
  updateProject(state, payload) {
    Vue.set(state.projectsList, [payload.id], payload.value)
  },
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
};

const actions = {
  async getProjects(ctx) {
    const { data: { results : projectList }} = await axios.get('http://localhost:8000/projects');
    await projectList.forEach(async (project, index) => {
        projectList[index].path = '/Users/antonbourosu/proj/';
       let projectModels = {};
       let modelPromises = project.models.map(modelId => ctx.dispatch('getModel', modelId));
       let projectModelsArray = await Promise.all(modelPromises);
      await projectModelsArray.map(model => {
       projectModels[model.model_id] = model;
       projectModels[model.model_id]['path'] = `${project.path}model_${model.model_id}/`;
      })
       projectList[index].models = projectModels;
       ctx.commit('updateProject', { id: projectList[index].project_id, value: projectList[index]})
    })


    // ctx.commit('setProjectList', projectList);
  
  },
  createProject(ctx, payload) {
    return axios.post('http://localhost:8000/projects/', payload)
      .then(res => {
        ctx.commit('createProject', res.data); 
        return res.data;
      })
  },
  updateProject(ctx, payload) {
    return axios.put(`http://localhost:8000/projects/${payload.projectId}/`, {name: payload.name})
      .then(res => {
        ctx.dispatch('getProjects');
        return res.data;
      })
  },
  deleteProject(ctx, payload) {
    return axios.delete(`http://localhost:8000/projects/${payload.projectId}/`)
      .then(res => {
        crx.commit('removeProject', res.data.project_id);
      })
  },
  getModel(ctx, modelId) {
    return axios.get(`http://localhost:8000/models/${modelId}/`)
      .then(res => res.data)
      .catch(console.error)
  },
  createProjectModel(ctx, payload) {
    return axios.post('http://localhost:8000/models/', payload)
      .then(res => {
        return res.data
      })
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
  state,
  mutations,
  actions
}
