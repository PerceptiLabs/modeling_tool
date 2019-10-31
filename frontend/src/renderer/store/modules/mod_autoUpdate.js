const namespaced = true;

const state = {
  showPopupUpdates: false,
  showNotAvailable: false,
  updateStatus: 'before update', // ('before update', 'downloading', 'no update', 'done')
  updateInfo: null,
  updateProgress: 0
};
const getters = {
  GET_releaseNotes(state) {
    if(state.updateInfo && state.updateInfo.releaseNotes) {
      return JSON.parse(state.updateInfo.releaseNotes)
    }
    else return null
  }
};

const mutations = {
  SET_showPopupUpdates (state, value) {
    state.showPopupUpdates = value
  },
  SET_showNotAvailable (state, value) {
    state.showNotAvailable = value
  },
  SET_updateStatus (state, value) {
    state.updateStatus = value
  },
  SET_updateInfo (state, value) {
    state.updateInfo = value
  },
  SET_updateProgress (state, value) {
    state.updateProgress = value
  },
};

const actions = {

};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
