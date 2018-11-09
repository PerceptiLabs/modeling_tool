const namespaced = true;

const state = {
  statisticsIsOpen: false,
  selectedElArr: [],
};

const mutations = {
  SET_statisticsIsOpen (state, value) {
    state.statisticsIsOpen = value
  },
  SET_selectedElArr (state, value) {
    value.forEach(function(item, i, arr) {
      item.meta.isSelected = true;
    });
    state.selectedElArr = value
  },
};

const actions = {
  STAT_defaultSelect({dispatch, commit, rootGetters}) {
    let elArr = [];
    let count = {
      train: 0,
      notTrain: 0
    };
    let net = rootGetters['mod_workspace/currentNetworkNet'];
    net.forEach(function(item, i, arr) {
      if(count.train > 0 && count.notTrain > 0) {
        return
      }
      if(count.train === 0 && item.layerType === "Training") {
        elArr.push(item);
        count.train++
      }
      if(count.notTrain === 0 && item.layerType !== "Training") {
        elArr.push(item);
        count.notTrain++
      }
    });
    commit('SET_selectedElArr', elArr)
  },
  NET_trainingDone({state, commit, dispatch}) {
    commit('SET_appMode', 'training-done');
    commit('SET_showNetResult', true);
    dispatch('mod_workspace/a_SET_canTestStatistics', true, {root: true});
  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
