const namespaced = true;

const state = {
  startupFolder: null,
};

const getters = {
  getCurrentDatasetSettings: state => () => {
    const currentDatasetPath = localStorage.getItem("currentDataset");
    return JSON.parse(localStorage.getItem(currentDatasetPath));
  }
};

const mutations = {
  SET_startupFolder(state, value) {
    state.startupFolder = value;
  }
};

const actions = {
  async setDatasetSettings(ctx, { datasetPath, settings }) {
    localStorage.setItem(datasetPath, JSON.stringify(settings));
  },
  async setCurrentDataset(ctx, datasetPath) {
    localStorage.setItem("currentDataset", datasetPath);
  },
  setStartupFolder({commit}, path) {
    commit('SET_startupFolder', path);
  }
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions
};
