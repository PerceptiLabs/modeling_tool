import Vue    from 'vue'

const namespaced = true;

const state = {
  selectedElArr: {
    statistics: null,
    viewBox: null,
    piePercents: null
  },
  statisticsTabs: {
    layerMetrics: {},
    selectedMetric: ''
  },
  viewBoxTabs: {
    layerMetrics: {},
    selectedMetric: ''
  },
};

const getters = {
  getSelectedMetric: (state) => (layerType) => {
    if (layerType === 'Training' || layerType === 'IoOutput') {
      return state.statisticsTabs.selectedMetric;  
    } else {
      return state.viewBoxTabs.selectedMetric;
    }
  },
  getLayerMetrics: (state) => (layerType) => {
    if (layerType === 'Training' || layerType === 'IoOutput') {
      return state.statisticsTabs.layerMetrics;  
    } else {
      return state.viewBoxTabs.layerMetrics;
    }
  },
}

const mutations = {
  SET_selectedElArr (state, value) {
    for (var keyId in value) {
      if (value[keyId] && value[keyId].layerMeta) {
        value[keyId].layerMeta.isSelected = true;
      }
    }
    state.selectedElArr = value;
  },
  SET_piePercents (state, value) {
    state.piePercents = value
  },
  CHANGE_selectElArr(state, dataEl) {
    let elArr = state.selectedElArr;
    if (dataEl.layerType === 'Training' || dataEl.layerType === 'IoOutput') {
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
  setDefaultMetric(state, layerType) {
    let tabs = '';

    if (layerType === 'Training' || layerType === 'IoOutput') {
      tabs = state.statisticsTabs;
    } else {
      tabs = state.viewBoxTabs;
    }

    const layerMetricsKeys = Object.keys(tabs.layerMetrics);
    
    if (layerMetricsKeys) {
      Vue.set(tabs, 'selectedMetric', Object.keys(tabs.layerMetrics)[0]);
    } else {
      Vue.set(tabs, 'selectedMetric', '');
    }
  },
  setSelectedMetric(state, { layerType, selectedMetric }) {
    let tabs = '';

    if (layerType === 'Training' || layerType === 'IoOutput') {
      tabs = state.statisticsTabs;
    } else {
      tabs = state.viewBoxTabs;
    }

    const layerMetricsKeys = Object.keys(tabs.layerMetrics);
    if (layerMetricsKeys.includes(selectedMetric)) {
      Vue.set(tabs, 'selectedMetric', selectedMetric);
    } else if (layerMetricsKeys) {
      Vue.set(tabs, 'selectedMetric', Object.keys(tabs.layerMetrics)[0]);
    } else {
      Vue.set(tabs, 'selectedMetric', '');
    }
  },
  setLayerMetrics(state, { layerType, layerMetrics }) {
    if (layerType === 'Training' || layerType === 'IoOutput') {
      Vue.set(state.statisticsTabs, 'layerMetrics', layerMetrics || {});
    } else {
      Vue.set(state.viewBoxTabs, 'layerMetrics', layerMetrics || {});
    }   
  }
};

const actions = {
  STAT_defaultSelect({commit, rootGetters}) {
    let elArr = {
      statistics: null,
      viewBox: null
    };

    let net = rootGetters['mod_workspace/GET_currentNetworkSnapshotElementList'];
    for(let el in net) {
      let item = net[el];
      if(elArr.statistics !== null && elArr.viewBox !== null || elArr.layerType === "Container") {
        continue
      }
      if(elArr.statistics === null && (item.layerType === "Training" || item.layerType === 'IoOutput')) {
        elArr.statistics = item;
      }
      if(elArr.viewBox === null && item.layerType !== "Training" && item.layerType !== 'IoOutput') {
        elArr.viewBox = item;
      }
    }
    commit('SET_selectedElArr', elArr)
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
