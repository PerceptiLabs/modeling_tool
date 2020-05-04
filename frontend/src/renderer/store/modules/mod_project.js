import { requestCloudApi } from "@/core/apiCloud";
import {generateID} from "@/core/helpers";
import axios from 'axios';
const namespaced = true;

const state = {
  currentProject: parseInt(localStorage.getItem('targetProject')) || null, // maybe we should copy all project object instead id and did modification in this one in case it wouldn't save changes.
  projectsList: [],
};

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
  /*
  // payload : { project: number, name: string };
  */
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
