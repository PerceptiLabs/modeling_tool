import { generateID }  from "@/core/helpers.js";
import Vue from 'vue'

const namespaced = true;

const state = {
  workspaceContent: [],
  currentNetwork: 0,
  dragElement: {},
  startArrowID: null,
  preArrow: {
    show: false,
    start: {x: 0, y: 0},
    stop: {x: 0, y: 0},
  }
};

const getters = {
  GET_networkIsNotEmpty(state) {
    return state.workspaceContent.length ? true : false
  },
  GET_currentNetwork(state, getters)  {
    return getters.GET_networkIsNotEmpty
      ? state.workspaceContent[state.currentNetwork]
      : {networkID: '1'} //for the close ap when the empty workspace
  },
  GET_currentNetworkSettings(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? state.workspaceContent[state.currentNetwork].networkSettings
      : {}
  },
  GET_currentNetworkElementList(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? state.workspaceContent[state.currentNetwork].networkElementList
      : null
  },
  GET_networkCoreStatus(state, getters) {
    return getters.GET_networkIsNotEmpty
      ? getters.GET_currentNetwork.networkMeta.coreStatus.Status
      : null
  },
  GET_currentSelectedEl(state, getters) {
    let selectedIndex = [];
    if(getters.GET_networkIsNotEmpty) {
      let elList = getters.GET_currentNetworkElementList;
      for(var el in elList) {
        if (elList[el].layerMeta.isSelected) selectedIndex.push(elList[el]);
      }
    }
    return selectedIndex;
  },
  GET_networkIsTraining(state, getters) {
    const coreStatus = getters.GET_networkCoreStatus;
    const statusList = ['Training', 'Validation', 'Paused'];
    return statusList.includes(coreStatus) ? true : false
  },
  GET_tutorialActiveId(state, getters, rootState, rootGetters) {
    if( rootGetters['mod_tutorials/getIstutorialMode'] && rootGetters['mod_tutorials/getActiveAction']) {
      return rootGetters['mod_tutorials/getActiveAction'].dynamic_id
    }
  },
  // GET_networkCanEditLayers(state, getters) {
  //   if(getters.GET_networkIsNotEmpty) {
  //     let openStatistics = getters.GET_currentNetwork.networkMeta.openStatistics;
  //     let openTest = getters.GET_currentNetwork.networkMeta.openTest;
  //     return !(openStatistics || openTest) ? true : false;
  //   }
  // },
  GET_statisticsIsOpen(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.openStatistics ? true : false;
    }
  },
  GET_testIsOpen(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.openTest ? true : false;
    }
  },
  GET_networkIsOpen(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      let openStatistics = getters.GET_currentNetwork.networkMeta.openStatistics;
      let openTest = getters.GET_currentNetwork.networkMeta.openTest;
      return !(openStatistics || openTest) ? true : false;
    }
  },
  GET_networkWaitGlobalEvent(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.chartsRequest.waitGlobalEvent;
    }
  }
};

const mutations = {
  //---------------
  //  NETWORK
  //---------------
  set_networkName(state, {getters, value}) {
    getters.GET_currentNetwork.networkName = value
  },
  add_network (state, {net, ctx}) {
    let newNetwork = {};
    const defaultNetwork = {
      networkName: 'New_Network',
      networkID: '',
      networkSettings: null,
      networkMeta: {},
      networkElementList: null,
      //networkContainerList: [],
    };
    const defaultMeta = {
      openStatistics: null, //null - hide Statistics; false - close Statistics, true - open Statistics
      openTest: null,
      zoom: 1,
      netMode: 'edit',//'addArrow', showStatistic
      coreStatus: {
        Status: 'Waiting' //Created, Training, Validation, Paused, Finished
      },
      chartsRequest: {
        timerID: null,
        waitGlobalEvent: false,
        doRequest: 0,
        showCharts: 0
      }
    };

    net === undefined
      ? newNetwork = defaultNetwork
      : newNetwork = net;
    newNetwork.networkMeta = defaultMeta;
    newNetwork.networkID = 'net' + generateID();

    state.workspaceContent.push(JSON.parse(JSON.stringify(newNetwork)));
    state.currentNetwork = state.workspaceContent.length - 1;
    if(ctx.$router.history.current.name !== 'app') {
      ctx.$router.replace({name: 'app'});
    }
  },
  DELETE_network(state, index) {
    if(state.currentNetwork >= index) {
      state.currentNetwork = state.currentNetwork - 1
    }
    state.workspaceContent.splice(index, 1);
  },
  //---------------
  //  NETWORK SETTINGS
  //---------------
  set_networkSettings(state, {getters, value}) {
    getters.GET_currentNetwork.networkSettings = value
  },

  //---------------
  //  NETWORK META
  //---------------
  set_netMode(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.netMode = value;
  },
  set_openStatistics(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.openStatistics = value;
    if(value && getters.GET_testIsOpen !== null) {
      getters.GET_currentNetwork.networkMeta.openTest = false;
    }
  },
  set_openTest(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.openTest = value;
    if(value && getters.GET_statisticsIsOpen !== null) {
      getters.GET_currentNetwork.networkMeta.openStatistics = false;
    }
  },
  set_statusNetworkCore(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.coreStatus = value;
  },
  set_statusNetworkCoreStatus(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.coreStatus.Status = value;
  },
  set_statusNetworkCoreStatusProgressClear(state, {getters}) {
    if(getters.GET_currentNetwork.networkMeta.coreStatus.Status.Progress) {
      getters.GET_currentNetwork.networkMeta.coreStatus.Status.Progress = 0;
    }
  },
  set_statusNetworkZoom(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.zoom = value;
  },
set_charts_doRequest(state, {getters, networkIndex}) {
  networkIndex
    ? state.workspaceContent[networkIndex].networkMeta.chartsRequest.doRequest++ // TODO add getters
    : getters.GET_currentNetwork.networkMeta.chartsRequest.doRequest++
},
set_charts_showCharts(state, {getters, networkIndex}) {
  networkIndex
    ? state.workspaceContent[networkIndex].networkMeta.chartsRequest.showCharts++ // TODO add getters
    : getters.GET_currentNetwork.networkMeta.chartsRequest.showCharts++
},
  set_charts_timerID(state, {getters, timerId}) {
    getters.GET_currentNetwork.networkMeta.chartsRequest.timerID = timerId;
  },
  set_statusNetworkWaitGlobalEvent(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.chartsRequest.waitGlobalEvent = value;
  },
  //---------------
  //  NETWORK ELEMENTS
  //---------------
  SET_elementName(state, value) {
    currentElement(value.id).layerName = value.setValue
  },
  add_element(state, {getters, event}) {
    let newEl = state.dragElement;
    let top = newEl.layerMeta.position.top;
    let left = newEl.layerMeta.position.left;
    let zoom = getters.GET_currentNetwork.networkMeta.zoom;
    let elementList = getters.GET_currentNetworkElementList;
    newEl.layerMeta.tutorialId = getters.GET_tutorialActiveId;
    newEl.layerMeta.position.top = (event.offsetY - top)/zoom;
    newEl.layerMeta.position.left = (event.offsetX - left)/zoom;

    if(!elementList) state.workspaceContent[state.currentNetwork].networkElementList = {};
    Vue.set(state.workspaceContent[state.currentNetwork].networkElementList, newEl.layerId, newEl);
    state.dragElement = {};
  },
delete_element(state, {getters, dispatch}) {
  let net = getters.GET_currentNetworkElementList;
  let arrSelect = getters.GET_currentSelectedEl;
  arrSelect.forEach((el)=>{
    delete net[el.layerId]
  });
  for(let el in net) {
    net[el].connectionOut = net[el].connectionOut.filter((connect)=>{
      return !arrSelect.includes(connect)
    });
    net[el].connectionIn  = net[el].connectionIn.filter((connect)=>{
      return !arrSelect.includes(connect)
    });
  }
  //state.workspaceContent[state.currentNetwork].networkElementList = newNet;
  dispatch('mod_events/EVENT_calcArray', null, {root: true})
},

  add_arrow(state, {dispatch, stopID}) {
    let startID = state.startArrowID;
    if(stopID === startID) return;

    let findArrow = currentElement(startID).connectionOut.findIndex((element)=> element === stopID );
    if(findArrow !== -1) {
      alert('This type of connection already exists!');
      return
    }

    currentElement(startID).connectionOut.push(stopID.toString()); //ID.toString need for the core
    currentElement(stopID).connectionIn.push(startID.toString());
    state.startArrowID = null;
    dispatch('mod_events/EVENT_calcArray', null, {root: true})
  },
delete_arrow(state,{dispatch, arrow}) {
  let startID = arrow.startID;
  let stopID = arrow.stopID;

  let newConnectionOut = currentElement(startID).connectionOut.filter((item)=> item !== stopID);
  let newConnectionIn = currentElement(stopID).connectionIn.filter((item)=> item !== startID);

  currentElement(startID).connectionOut = newConnectionOut;
  currentElement(stopID).connectionIn = newConnectionIn;
  dispatch('mod_events/EVENT_calcArray', null, {root: true})
},

  /*-- NETWORK ELEMENTS SETTINGS --*/
  set_elementSettings(state, settings) {
    currentElement(settings.elId).layerSettings = settings.set;  //TODO NEED CHECK
    currentElement(settings.elId).layerCode = settings.code;     //TODO NEED CHECK
  },

  /*-- NETWORK ELEMENTS META --*/
  set_elementUnselect(state, {getters}) {
    for(let layer in getters.GET_currentNetworkElementList) {
      currentElement(layer).layerMeta.isSelected = false;
    }
  },
  set_elementSelect(state, value) {
    currentElement(value.id).layerMeta.isSelected = value.setValue;
  },
  set_elementMultiSelect(state, value) {
    currentElement(value.id).layerMeta.isSelected = value.setValue;
  },
  SET_elementLock(state, id) {
    let elMeta = currentElement(id).layerMeta;
    elMeta.isLock = !elMeta.isLock
  },
  SET_elementVisible(state, id) {
    let elMeta = currentElement(id).isInvisible;
    elMeta.isLock = !elMeta.isInvisible
  },
  change_elementPosition(state, value) {
    let elPosition = currentElement(value.id).layerMeta.position;
    elPosition.top = value.top;
    elPosition.left = value.left;
  },
  set_elementInputDim(state, {getters, value}) {
    for(let element in getters.GET_currentNetworkElementList) {
      currentElement(element).layerMeta.InputDim = value[element]
    }
  },
  set_elementOutputDim(state, {getters, value}) {
    for(let element in getters.GET_currentNetworkElementList) {
      currentElement(element).layerMeta.OutputDim = value[element]
    }
  },

  //---------------
  //  NETWORK CONTAINER
  //---------------
add_container(state, {getters, dispatch, newContainer, arrSelect}) {
  let allTop = [];
  let allLeft = [];

  let arrElID = arrSelect.map((item)=> {
    // allOutId = [...allOutId, ...new Set(item.el.connectionOut)];
    // allInId  = [...allInId,  ...new Set(item.el.connectionIn)];
    allTop.push(item.el.layerMeta.position.top);
    allLeft.push(item.el.layerMeta.position.left);
    return item.el.layerId
  });

  newContainer.containerLayersList = arrSelect;
  newContainer.layerMeta.position.top = calcPosition(allTop);
  newContainer.layerMeta.position.left = calcPosition(allLeft);

  let newNetElList = getters.GET_currentNetworkElementList.filter((el)=> {
    return !arrElID.includes(el.layerId);
  });

  newNetElList.push(newContainer);

  state.workspaceContent[state.currentNetwork].networkElementList = newNetElList;
  dispatch('CLOSE_container', newContainer);
  dispatch('mod_events/EVENT_calcArray', null, {root: true});

  function calcPosition(arrIn) {
    return (Math.max(...arrIn) + Math.min(...arrIn))/2
  }
},
close_container(state, container) {
  container.containerLayersList.forEach((item)=> {
    item.layerMeta.containerDiff.top = container.layerMeta.position.top - item.layerMeta.position.top;
    item.layerMeta.containerDiff.left = container.layerMeta.position.left - item.layerMeta.position.left;
    item.layerMeta.displayNone = true;
    item.layerMeta.position = container.layerMeta.position;
  });
  container.layerMeta.displayNone = false
},
open_container(state, container) {
  container.containerLayersList.forEach((item)=> {
    let diffTop = item.layerMeta.containerDiff.top;
    let diffLeft = item.layerMeta.containerDiff.left;
    let top = item.layerMeta.position.top;
    let left = item.layerMeta.position.left;

    item.layerMeta.containerDiff = {
      top: 0,
      left: 0
    };
    item.layerMeta.position = {
      top: top - diffTop,
      left: left - diffLeft
    };
    item.layerMeta.displayNone = false;
  });
  container.layerMeta.displayNone = true
},
  //---------------
  //  OTHER
  //---------------
  SET_currentNetwork(state, value) {
    state.currentNetwork = value
  },
  ADD_dragElement(state, event) {
    state.dragElement = createNetElement(event);
  },
  SET_startArrowID (state, value) {
    state.startArrowID = value
  },
  SET_preArrowStart (state, value) {
    state.preArrow.start = value;
    state.preArrow.stop = value;
    state.preArrow.show = true;
  },
  SET_preArrowStop (state, value) {
    state.preArrow.stop = value
  },
  CLEAR_preArrow (state) {
    state.preArrow = {
      show: false,
      start: {x: 0, y: 0},
      stop: {x: 0, y: 0},
    }
  },
};

const actions = {
  //---------------
  //  NETWORK
  //---------------
  ADD_network({commit, dispatch}, {network, ctx}) {
    commit('add_network', {network, ctx})
  },
  SET_networkName({commit, getters}, value) {
    commit('set_networkName', {getters, value})
  },
  SET_networkSettings({commit, getters}, value) {
    commit('set_networkSettings', {getters, value})
  },
  SET_networkElementList({commit, getters}, value) {
    commit('set_networkElementList', {getters, value})
  },
  SET_netMode({commit, getters}, value) {
    commit('set_netMode', {getters, value})
  },
  SET_openStatistics({commit, getters}, value) {
    commit('set_openStatistics', {getters, value})
  },
  SET_openTest({commit, getters}, value) {
    commit('set_openTest', {getters, value})
  },
  SET_statusNetworkCore({commit, getters}, value) {
    commit('set_statusNetworkCore', {getters, value})
  },
  SET_statusNetworkCoreStatus({commit, getters}, value) {
    commit('set_statusNetworkCoreStatus', {getters, value})
  },
  SET_statusNetworkCoreStatusProgressClear({commit, getters}) {
    commit('set_statusNetworkCoreStatusProgressClear', {getters})
  },
  SET_statusNetworkZoom({commit, getters}, value) {
    commit('set_statusNetworkZoom', {getters, value})
  },
  SET_statusNetworkWaitGlobalEvent({commit, getters}, value) {
    commit('set_statusNetworkWaitGlobalEvent', {getters, value})
  },
  RESET_network({commit}) {
    commit('RESET_network')
  },
  CHECK_requestInterval({dispatch, commit, rootState, getters, state}, time) {
    //console.log(`request -> can show`, `${time}ms`);
    const timeRequest = time + 500;
    const isLongRequest = timeRequest > rootState.globalView.timeIntervalDoRequest;
    if(isLongRequest) {
      const currentMeta = getters.GET_currentNetwork.networkMeta.chartsRequest;
      clearInterval(currentMeta.timerID);
      console.log('new time', timeRequest);
      dispatch('globalView/SET_timeIntervalDoRequest', timeRequest, {root: true});
      dispatch('EVENT_startDoRequest', true);
    }
  },
  EVENT_startDoRequest({dispatch, commit, rootState, getters, state}, isStart) {
    //console.log('EVENT_startDoRequest', isStart);
    const currentMeta = getters.GET_currentNetwork.networkMeta.chartsRequest;
    if(currentMeta === undefined) return;
    const timeInterval = rootState.globalView.timeIntervalDoRequest;

    dispatch('SET_statusNetworkWaitGlobalEvent', isStart);
    if(isStart) {
      let timerId = setInterval(()=> {
        dispatch('EVENT_chartsRequest')
      }, timeInterval);
      commit('set_charts_timerID', {getters, timerId});
    }
    else {
      clearInterval(currentMeta.timerID);
    }
  },
  EVENT_chartsRequest({dispatch, commit, rootState, getters, state}) {
    var networkIndex = state.currentNetwork;
    commit('set_charts_showCharts', {getters, networkIndex});
    dispatch('mod_api/API_updateResults', null, {root: true})
      .then(()=> {
        commit('set_charts_doRequest', {getters, networkIndex});
        dispatch('mod_api/API_getStatus', null, {root: true});
      });
  },
  EVENT_onceDoRequest({dispatch, commit, rootState, getters}, isStart) {
    dispatch('mod_api/API_updateResults', null, {root: true})
      .then(()=> {
        commit('set_charts_doRequest', {getters});
        dispatch('mod_api/API_getStatus', null, {root: true});
      });
  },
  //---------------
  //  NETWORK ELEMENTS
  //---------------
  SET_elementSettings({commit}, settings) {
    commit('set_elementSettings', settings)
  },
  ADD_element({commit, getters}, event) {
    commit('add_element', {getters, event})
  },
  DELETE_element({commit, getters, dispatch}) {
    commit('delete_element', {getters, dispatch})
  },
  ADD_arrow({commit, getters, dispatch}, stopID) {
    commit('add_arrow', {dispatch, stopID})
  },
  DELETE_arrow({commit, getters, dispatch}, arrow) {
    commit('delete_arrow', {dispatch, arrow})
  },
  SET_elementUnselect({commit, getters}) {
    commit('set_elementUnselect', {getters})
  },
  SET_elementSelect({commit}, value) {
    commit('set_elementSelect', value)
  },
  SET_elementMultiSelect({commit}, value) {
    commit('set_elementMultiSelect', value)
  },
  SET_elementInputDim({commit, getters}, value) {
    commit('set_elementInputDim', {getters, value})
  },
  SET_elementOutputDim({commit, getters}, value) {
    commit('set_elementOutputDim', {getters, value})
  },
  CHANGE_elementPosition({commit, getters}, value) {
    commit('change_elementPosition', value)
  },
  //---------------
  //  NETWORK CONTAINER
  //---------------
  ADD_container({commit, getters, dispatch}, event) {
    let arrSelect = getters.GET_currentSelectedEl;
    if(arrSelect.length === 0) return;
    if(arrSelect.length === 1) {
      alert('At least 2 elements are needed to create a group');
      return;
    }
    let fakeEvent = {
      timeStamp: generateID(),
      target: {
        dataset: {
          layer: 'Data Group',
          type: 'container',
          component: 'LayerContainer',
        },
        clientHeight: 0,
        clientWidth: 0
      }
    };
    let newContainer = createNetElement(fakeEvent);

    commit('add_container', {getters, dispatch, newContainer, arrSelect});
  },
  OPEN_container({commit, getters, dispatch}, container) {
    commit('open_container', container)
  },
  CLOSE_container({commit, getters, dispatch}, container) {
    commit('close_container', container)
  },

};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions
}

function currentElement(id) {
  return state.workspaceContent[state.currentNetwork].networkElementList[id];
}
function createNetElement(event) {
  return {
    layerId: generateID(),
    layerName: event.target.dataset.layer,
    layerType: event.target.dataset.type,
    layerSettings: '',
    layerCode: '',
    layerMeta: {
      displayNone: false,
      isInvisible: false,
      isLock: false,
      isSelected: false,
      position: {
        top: event.target.clientHeight/2,
        left: event.target.clientWidth/2,
      },
      tutorialId: '',
      OutputDim: '',
      InputDim: '',
      containerDiff: {
        top: 0,
        left: 0,
      }
    },
    componentName: event.target.dataset.component,
    connectionOut: [],
    connectionIn: [],
    calcAnchor: { top: [], right: [], bottom: [], left: []}
  };
}