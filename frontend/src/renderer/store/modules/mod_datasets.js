import { getDatasets as rygg_getDatasets } from '@/core/apiRygg.js'
const namespaced = true;

const state = {
  datasets: [],
};

const getters = {
  GET_datasets(state) {
    return state.datasets;
  }
}
const mutations = {
  SET_datasets(state, value) {
    state.datasets = value;
  }
};

const actions = {
  async getDatasets({commit}) {
    const { data } = await rygg_getDatasets();
    commit('SET_datasets', data.results);
    return data;
  }
};

export default {
  getters,
  namespaced,
  state,
  mutations,
  actions
};
