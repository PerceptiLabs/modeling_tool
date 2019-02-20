//import requestApi  from "@/core/api.js";
import {ipcRenderer} from 'electron'

const namespaced = true;

const state = {
  calcArray: 0,
  openNetwork: 0,
  saveNetwork: 0,
  chartsRequest: {
    timeInterval: 2000,
    timerID: null,
    waitGlobalEvent: false,
    doRequest: 0,
    requestCounter: 0,
    showCharts: 0
  }
};

const mutations = {
  set_calcArray(state) {
    state.calcArray++
  },
  set_openNetwork(state) {
    state.openNetwork++
  },
  set_saveNetwork(state) {
    state.saveNetwork++
  },
  set_charts_doRequest(state) {
    console.log('doRequest');
    state.chartsRequest.doRequest++
  },
  // set_charts_showCharts(state) {
  //   state.chartsRequest.showCharts++
  // },
  set_charts_timerID(state, id) {
    state.chartsRequest.timerID = id;
  },
  set_charts_waitGlobalEvent(state, isWait) {
    state.chartsRequest.waitGlobalEvent = isWait
  },
  set_charts_requestCounterAdd(state) {
    state.chartsRequest.requestCounter++
  },
  set_charts_waitGlobalEventReduce(state) {
    state.chartsRequest.requestCounter--;
    if(state.chartsRequest.requestCounter === 0) {
      console.log('showCharts');
      state.chartsRequest.showCharts++
    }
  },
};

const actions = {
  EVENT_calcArray({commit}) {
    commit('set_calcArray')
  },
  EVENT_openNetwork({commit}) {
    commit('set_openNetwork');
  },
  EVENT_saveNetwork({commit}) {
    commit('set_saveNetwork');
  },
  EVENT_logOut({dispatch}, ctx) {
    localStorage.removeItem('userToken');
    dispatch('globalView/SET_userToken', '', {root: true});
    dispatch('mod_workspace/RESET_network', null, {root: true});
    ctx.$router.replace({name: 'login'});
  },
  EVENT_closeApp({dispatch}) {
    dispatch('mod_api/API_CLOSE_core', null, {root: true});
    ipcRenderer.send('appClose');
  },
  EVENT_startDoRequest({dispatch, commit, state}, isStart) {
    if(isStart) {
      let timer = setInterval(()=> {
        commit('set_charts_doRequest');
      }, state.chartsRequest.timeInterval);
      commit('set_charts_waitGlobalEvent', isStart);
      commit('set_charts_timerID', timer);
      dispatch('mod_api/API_getStatus', null, {root: true});
    }
    else {
      commit('set_charts_waitGlobalEvent', isStart);
      clearInterval(state.chartsRequest.timerID);
    }
  }
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
