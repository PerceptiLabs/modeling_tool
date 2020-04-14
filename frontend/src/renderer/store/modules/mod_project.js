import { requestCloudApi } from "@/core/apiCloud";
import {generateID} from "@/core/helpers";

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
    // @todo commit response not mock data
    return requestCloudApi('get', 'v1/projects')
      .then((response) => {
        ctx.commit('setProjectList', [{id: 1, name: 'project test', createdAt: new Date()},{id: 2, name: 'Second project', createdAt: new Date()}])
      })
      .catch((error)=> {
        ctx.commit('setProjectList', [{id: 1, name: 'project test', createdAt: new Date()},{id: 2, name: 'Second project', createdAt: new Date()}])
      })
  },
  createProject(ctx, payload) {
    ctx.commit('createProject', payload);
  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
