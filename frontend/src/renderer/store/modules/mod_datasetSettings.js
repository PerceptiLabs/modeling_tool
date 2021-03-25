const namespaced = true;

const state = {
};

const getters = {
  getCurrentDatasetSettings: state => () => {
    const currentDatasetPath = localStorage.getItem("currentDataset");
    return JSON.parse(localStorage.getItem(currentDatasetPath));
  }
};

const mutations = {};

const actions = {
  async setDatasetSettings(ctx, { datasetPath, settings }) {
    localStorage.setItem(datasetPath, JSON.stringify(settings));
  },
  async setCurrentDataset(ctx, datasetPath) {
    localStorage.setItem("currentDataset", datasetPath);
  }
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions
};
