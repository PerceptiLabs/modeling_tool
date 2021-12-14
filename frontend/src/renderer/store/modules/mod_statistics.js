import Vue    from 'vue'
import {deepCloneNetwork} from "@/core/helpers";

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
    isTabPlaceValid(layerType);
    return state[layerType].selectedMetric;
  },
  getLayerMetrics: (state) => (sectionTitle) => {
    isTabPlaceValid(sectionTitle);
    return state[sectionTitle].layerMetrics;
  },
}

const mutations = {
  SET_selectedElArr (state, value) {
    const {selectedMetric, ...data} = value;
    if (data.viewBox) {
      data.viewBox.layerMeta.isSelected = true; 
      state.statisticsTabs.selectedMetric = selectedMetric || data.statistics.layerName
      state.selectedElArr = data;
    }
  },
  SET_piePercents (state, value) {
    state.piePercents = value
  },

  CHANGE_StatisticSelectedArr(state, dataEl) {
    state.selectedElArr.statistics = dataEl;
    state.statisticsTabs.selectedMetric = dataEl.layerName;
  },
  CHANGE_viewBoxSelectElArr(state, dataEl) {
    state.selectedElArr.viewBox.layerMeta.isSelected = false;
    state.selectedElArr.viewBox = dataEl;
    state.selectedElArr.viewBox.layerMeta.isSelected = true;
  },
  setDefaultMetric(state, placeToBeChanged) {
    isTabPlaceValid(placeToBeChanged);
    let tabs = state[placeToBeChanged];
    const layerMetricsKeys = Object.keys(tabs.layerMetrics);
    const value = layerMetricsKeys && Object.keys(tabs.layerMetrics)[0] || '';
     
    Vue.set(tabs, 'selectedMetric', value);
  },
  setSelectedMetric(state, { placeToBeChanged, selectedMetric }) {
    isTabPlaceValid(placeToBeChanged);
    let tabs = state[placeToBeChanged];

    const layerMetricsKeys = Object.keys(tabs.layerMetrics);
    if (layerMetricsKeys.includes(selectedMetric) || selectedMetric === "Global") {
      Vue.set(tabs, 'selectedMetric', selectedMetric);
    } else if (layerMetricsKeys) {
      Vue.set(tabs, 'selectedMetric', Object.keys(tabs.layerMetrics)[0]);
    } else {
      Vue.set(tabs, 'selectedMetric', '');
    }
  },
  setLayerMetrics(state, { placeToBeChanged, layerMetrics }) {
    isTabPlaceValid(placeToBeChanged);
    Vue.set(state[placeToBeChanged], 'layerMetrics', layerMetrics || {});
  },
};

const actions = {
  STAT_defaultSelect({commit, rootGetters}) {
    let elArr = {
      statistics: null,
      viewBox: null
    };
    let selectedMetric = null;

    let net = rootGetters['mod_workspace/GET_currentNetworkSnapshotElementList'];
    for(let el in net) {
      let item = net[el];
      
      const areStatisticsAlreadySet = !(elArr.statistics === null || (elArr.statistics !== null && item.layerType === 'IoOutput')) && elArr.viewBox !== null || elArr.layerType === "Container";
      
      if(areStatisticsAlreadySet) {
        continue
      }
      const isTrainingOrIOComponent = (elArr.statistics === null && (item.layerType === "Training" || item.layerType === 'IoOutput' || item.layerType === 'IoInput')) || (item.layerType === 'IoOutput' && elArr.statistics);
      if(isTrainingOrIOComponent) {
        if (elArr.statistics === null || item.layerType === 'IoOutput') {
          elArr.statistics = item;
          if (item.layerType === 'IoOutput') {
            selectedMetric = 'Overview';
          }
        }
      } else  {
        elArr.viewBox = item;
      }
    }
    commit('SET_selectedElArr', {...elArr, selectedMetric});
  },
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}

const isTabPlaceValid = (tabName) => {
  const tabOptions = ['viewBoxTabs', 'statisticsTabs'];
  if(!tabOptions.includes(tabName)) {
    throw new Error(`${tabName} is not valid key`); 
  }
};