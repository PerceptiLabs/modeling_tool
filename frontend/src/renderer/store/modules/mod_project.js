import { requestCloudApi } from "@/core/apiCloud";
import {generateID} from "@/core/helpers";
import axios from 'axios';
const namespaced = true;

const state = {
  currentProject: null, // maybe we should copy all project object instead id and did modification in this one in case it wouldn't save changes.
  projectsList: [],
};

const mutations = {
  setProjectList(state, payload){
    state.projectsList = payload;
  },
  selectProject(state, projectId) {
    state.currentProject = projectId;
  },
  createProject(state, payload) {
    state.projectsList.push(payload);
  }
};

const actions = {
  getProjects(ctx) {
    return axios.get('http://localhost:8000/projects')
      .then((res) => {
        ctx.commit('setProjectList', res.data.results)
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
  deleteProject(ctx, payload) {
    // @todo 
    return axios.delete(`http://localhost:8000/projects/${payload.projectId}`)
      .then(res => {
        crx.commit('removeProject', res.data.project_id);
      })
  }
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
