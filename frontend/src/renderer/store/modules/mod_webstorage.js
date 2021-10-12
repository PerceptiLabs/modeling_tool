import idb from '@/core/helpers/idb-helper.js';

const namespaced = true;

const state = {};

const getters = {};

const mutations = {};

const actions = {
  async saveTestStatistic(ctx, payload) {
    return await idb.saveTestStatistic(payload);
  },
  async getTestStatistic(ctx) {
    return await idb.getTestStatistic();
  },
  async deleteTestStatisticByModelId(ctx, payload) {
    return await idb.deleteTestByModelIds(payload);
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}