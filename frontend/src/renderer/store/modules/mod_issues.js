import axios from 'axios';

const namespaced = true;

const state = {};

const getters = {};

const mutations = {};

const actions = {
    createIssue(ctx, payload) {
      return axios.post('http://localhost:8000/issues/', payload)
        .then(res => {
          return res.data;
        });
    },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
