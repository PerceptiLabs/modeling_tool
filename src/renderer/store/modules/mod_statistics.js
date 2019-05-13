const namespaced = true;
//TODO разобраться что это
const state = {
  selectedElArr: {
    statistics: null,
    viewBox: null
  },
};

const mutations = {
  SET_selectedElArr (state, value) {
    // value.statistics.meta.isSelected = true;
    // value.viewBox.meta.isSelected = true;
    // console.log(value.viewBox);
    for (var el in value) {
      //console.log(value[el]);
      value[el].layerMeta.isSelected = true;
    }
    // console.log(value);
    state.selectedElArr = value
  },
  CHANGE_selectElArr(state, dataEl) {
    let elArr = state.selectedElArr;
    if (dataEl.el.layerType === "Training") {
      elArr.statistics.layerMeta.isSelected = false;
      elArr.statistics = dataEl.el;
      elArr.statistics.layerMeta.isSelected = true;
    }
    else {
      elArr.viewBox.layerMeta.isSelected = false;
      elArr.viewBox = dataEl.el;
      elArr.viewBox.layerMeta.isSelected = true;
    }
  },
};

const actions = {
  STAT_defaultSelect({dispatch, commit, rootGetters}) {
    let elArr = {
      statistics: null,
      viewBox: null
    };
    let net = rootGetters['mod_workspace/GET_currentNetworkElementList'];
    net.forEach(function(item, i, arr) {
      if(elArr.statistics !== null && elArr.viewBox !== null) {
        return
      }
      if(elArr.statistics === null && item.layerType === "Training") {
        elArr.statistics = item;
      }
      if(elArr.viewBox === null && item.layerType !== "Training") {
        elArr.viewBox = item;
      }
    });
    /*выполнить после statisticsIsOpen net-base-element.vue*/
    setTimeout(()=> {
      ///console.log('costul');
      commit('SET_selectedElArr', elArr)
    }, 500);

  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
