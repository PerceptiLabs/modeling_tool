const namespaced = true;

const state = {
  selectedElArr: {
    statistics: null,
    viewBox: null
  },
};

const mutations = {
  SET_selectedElArr (state, value) {
    for (var keyId in value) {
      value[keyId].layerMeta.isSelected = true;
    }
    state.selectedElArr = value;
  },
  CHANGE_selectElArr(state, dataEl) {
    let elArr = state.selectedElArr;
    if (dataEl.layerType === "Training") {
      elArr.statistics.layerMeta.isSelected = false;
      elArr.statistics = dataEl;
      elArr.statistics.layerMeta.isSelected = true;
    }
    else {
      elArr.viewBox.layerMeta.isSelected = false;
      elArr.viewBox = dataEl;
      elArr.viewBox.layerMeta.isSelected = true;
    }
  },
};

const actions = {
  STAT_defaultSelect({commit, rootGetters}) {
    let elArr = {
      statistics: null,
      viewBox: null
    };
    let net = rootGetters['mod_workspace/GET_currentNetworkElementList'];
    for(let el in net) {
      let item = net[el];
      if(elArr.statistics !== null && elArr.viewBox !== null || elArr.layerType === "Container") {
        continue
      }
      if(elArr.statistics === null && item.layerType === "Training") {
        elArr.statistics = item;
      }
      if(elArr.viewBox === null && item.layerType !== "Training") {
        elArr.viewBox = item;
      }
    }
    commit('SET_selectedElArr', elArr)
  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
