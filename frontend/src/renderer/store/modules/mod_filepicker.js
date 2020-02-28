const namespaced = true;

const state = {
  selectedFilePathes: []
};

const getters = {
  get_selectedFilePaths(state) {
    return state.selectedFilePathes;
  },
}

const mutations = {
  set_selectedFilePaths (state, value) {
    state.selectedFilePathes = value;
  },
};


const actions = {
  SET_selectedFilePaths({commit, rootGetters}, value) {
    return new Promise((resolve, reject) => {
      commit('set_selectedFilePaths', value);
      resolve(value);
    });
  }
}

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
