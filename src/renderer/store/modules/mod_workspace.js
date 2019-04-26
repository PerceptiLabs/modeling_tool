import { findIndexId, generateID }  from "@/core/helpers.js";

function createPathNode(path, state) {
  //console.log('createPathNode');
  const network = path.slice();
  const networkId = network.shift();
  const initValue = state.workspaceContent[state.currentNetwork].networkElementList[networkId];
  return network.reduce((acc, id) => acc.child[id], initValue);
}
function createNetElement(event) {
  return {
    layerId: generateID(event.timeStamp).toString(),
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
  };
}

const namespaced = true;

const state = {
  workspaceContent: [],
  currentNetwork: 0,
  dragElement: {},
  startArrowID: null,
  arrowType: 'solid',
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
    if(getters.GET_networkIsNotEmpty) return state.workspaceContent[state.currentNetwork];

    return ['empty app']
  },
  GET_currentNetworkSettings(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return state.workspaceContent[state.currentNetwork].networkSettings;
    }
    return {}
  },
  GET_currentNetworkElementList(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return state.workspaceContent[state.currentNetwork].networkElementList;
    }
    return ['empty app']
  },
  GET_networkCoreStatus(state, getters) {
    if(getters.GET_networkIsNotEmpty) {
      return getters.GET_currentNetwork.networkMeta.coreStatus.Status
    }
    return 'empty app'
  },
  GET_currentSelectedEl(state, getters) {
    let selectedIndex = [];
    if(getters.GET_networkIsNotEmpty) {
      getters.GET_currentNetworkElementList.forEach(function (el, index, arr) {
        if (el.layerMeta.isSelected) {
          selectedIndex.push({
            index,
            el
          });
        }
      });
    }
    return selectedIndex;
  },
  GET_networkIsTraining(state, getters) {
    let coreStatus = getters.GET_networkCoreStatus;
    if(coreStatus === 'Training'
      || coreStatus === 'Validation'
      || coreStatus === 'Paused'
    ){
      return true
    }
    else return false
  },
  GET_tutorialActiveId(state, getters, rootState, rootGetters) {
    if( rootGetters['mod_tutorials/getIstutorialMode'] && rootGetters['mod_tutorials/getActiveAction']) {
      return rootGetters['mod_tutorials/getActiveAction'].dynamic_id
    }
  },  
  GET_networkCanEditLayers(state, getters) {
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

  set_networkElementList(state, {getters, value}) {
    getters.GET_currentNetworkElementList = value
  },
  add_network (state, {dispatch, net}) {
    let newNetwork = {};
    let defaultNetwork = {
      networkName: 'New_Network',
      networkID: '',
      networkSettings: null,
      networkMeta: {},
      networkElementList: [],
      //networkContainerList: [],
    };
    let defaultMeta = {
      openStatistics: null, //null - hide Statistics; false - close Statistics, true - open Statistics
      openTest: null,
      //canTestStatistics: false,
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

    net.network === undefined ? newNetwork = defaultNetwork : newNetwork = net.network;
    newNetwork.networkMeta = defaultMeta;
    newNetwork.networkID = 'net' + generateID(Date.now());

    state.workspaceContent.push(JSON.parse(JSON.stringify(newNetwork)));
    state.currentNetwork = state.workspaceContent.length - 1;
    if(net.ctx.$router.history.current.name !== 'app') {
      net.ctx.$router.replace({name: 'app'});
    }
  },
  DELETE_network(state, index) {
    if(state.currentNetwork >= index) {
      state.currentNetwork = state.currentNetwork - 1
    }
    state.workspaceContent.splice(index, 1);
  },
  RESET_network (state) {
    state.workspaceContent = [];
    state.currentNetwork = 0;
    state.dragElement = {};
    state.startArrowID = null;
    state.arrowType = 'solid';
    state.preArrow = null;
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
  // set_networkCanTesting(state, {getters, value}) {
  //   getters.GET_currentNetwork.networkMeta.canTestStatistics = value;
  // },
  set_netMode(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.netMode = value;
  },
  set_openStatistics(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.openStatistics = value;
  },
  set_openTest(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.openTest = value;
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
    if(networkIndex) {
      state.workspaceContent[networkIndex].networkMeta.chartsRequest.doRequest++
    }
    else {
      getters.GET_currentNetwork.networkMeta.chartsRequest.doRequest++
    }
  },
  set_charts_showCharts(state, {getters, networkIndex}) {
    if(networkIndex) {
      state.workspaceContent[networkIndex].networkMeta.chartsRequest.showCharts++
    }
    else {
      getters.GET_currentNetwork.networkMeta.chartsRequest.showCharts++
    }
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
  //TODO check SET_elementName can easy
  SET_elementName(state, value) {
    let node = createPathNode(value.path, state);
    node.layerName = value.setValue
  },
  add_element(state, {getters, event}) {
    let top = state.dragElement.layerMeta.position.top;
    let left = state.dragElement.layerMeta.position.left;
    let zoom = getters.GET_currentNetwork.networkMeta.zoom;
    state.dragElement.layerMeta.tutorialId = getters.GET_tutorialActiveId
    
    state.dragElement.layerMeta.position.top = (event.offsetY - top)/zoom;
    state.dragElement.layerMeta.position.left = (event.offsetX - left)/zoom;
    getters.GET_currentNetworkElementList.push(state.dragElement);
    state.dragElement = {};
  },
  delete_elementConnection(state, {newNet, arrSelectId, dispatch}) {
    newNet.forEach((el)=>{
      el.connectionOut = el.connectionOut.filter((connect)=>{
        //TODO return when return arrowType
        //return !value.arrSelectId.includes(connect.id)
        return !arrSelectId.includes(connect)
      });
      el.connectionIn  = el.connectionIn.filter((connect)=>{
        //TODO return when return arrowType
        //return !value.arrSelectId.includes(connect.id)
        return !arrSelectId.includes(connect)
      });
    });
    state.workspaceContent[state.currentNetwork].networkElementList = newNet;
    dispatch('mod_events/EVENT_calcArray', null, {root: true})
  },

  add_arrow(state, {getters, dispatch, stopID}) {
    let startID = state.startArrowID;
    if(stopID == startID) return;

    let pathNet = getters.GET_currentNetworkElementList;
    let indexStart = pathNet.findIndex((element, index, array)=> { return element.layerId == startID;});
    let findArrow = pathNet[indexStart].connectionOut.findIndex((element, index, array)=> element == stopID );
    if(findArrow !== -1) {
      alert('This type of connection already exists!');
      return
    }

    //TODO start only one type connection
    pathNet[indexStart].connectionOut.push(stopID.toString()); //ID.toString need for the core

    let indexStop = pathNet.findIndex((element, index, array)=> { return element.layerId == stopID;});
    pathNet[indexStop].connectionIn.push(startID.toString());
    //stop only one type connection
    state.startArrowID = null;
    dispatch('mod_events/EVENT_calcArray', null, {root: true})
  },
  delete_arrow(state,{getters, dispatch, arrow}) {
    let arrowList = getters.GET_currentNetworkElementList;
    let startID = arrow.startID;
    let stopID = arrow.stopID;
    let indexStartEl = findIndexId(arrowList, startID);
    let indexStopEl = findIndexId(arrowList, stopID);
    let newConnectionOut = arrowList[indexStartEl].connectionOut.filter((item)=> item !== stopID);
    let newConnectionIn = arrowList[indexStopEl].connectionIn.filter((item)=> item !== startID);
    state.workspaceContent[state.currentNetwork].networkElementList[indexStartEl].connectionOut = newConnectionOut;
    state.workspaceContent[state.currentNetwork].networkElementList[indexStopEl].connectionIn = newConnectionIn;
    dispatch('mod_events/EVENT_calcArray', null, {root: true})
  },
  /*-- NETWORK ELEMENTS SETTINGS --*/
  set_elementSettings(state, {getters, settings}) {
    let indexEl = getters.GET_currentSelectedEl[0].index;
    getters.GET_currentNetworkElementList[indexEl].layerSettings = settings.set;  //TODO NEED CHECK
    getters.GET_currentNetworkElementList[indexEl].layerCode = settings.code;     //TODO NEED CHECK
  },


  /*-- NETWORK ELEMENTS META --*/
  set_elementUnselect(state, {getters}) {
    getters.GET_currentNetworkElementList.forEach((el)=>{
      el.layerMeta.isSelected = false;
    });
  },
  set_elementSelect(state, {getters, value}) {
    getters.GET_currentNetworkElementList[value.path].layerMeta.isSelected = value.setValue;
  },
  set_elementMultiSelect(state, {getters, value}) {
    getters.GET_currentNetworkElementList[value.path].layerMeta.isSelected = value.setValue;
  },
  SET_elementLock(state, value) {
    let node = createPathNode(value, state);
    node.layerMeta.isLock = !node.layerMeta.isLock
  },
  SET_elementVisible(state, value) {
    let node = createPathNode(value, state);
    node.layerMeta.isInvisible = !node.layerMeta.isInvisible
  },
  change_elementPosition(state, {getters, value}) {
    let el = value.index;
    let net = getters.GET_currentNetworkElementList;
    net[el].layerMeta.position.top = value.top;
    net[el].layerMeta.position.left = value.left;
  },
  set_elementInputDim(state, {getters, value}) {
    getters.GET_currentNetworkElementList.forEach((el)=>{
      el.layerMeta.InputDim = value[el.layerId]
    });
  },
  set_elementOutputDim(state, {getters, value}) {
    getters.GET_currentNetworkElementList.forEach((el)=>{
      el.layerMeta.OutputDim = value[el.layerId];
    });
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
    console.log(newNetElList);
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
      item.el.layerMeta.containerDiff.top = container.layerMeta.position.top - item.el.layerMeta.position.top;
      item.el.layerMeta.containerDiff.left = container.layerMeta.position.left - item.el.layerMeta.position.left;
      item.el.layerMeta.displayNone = true;
      item.el.layerMeta.position = container.layerMeta.position;
    });
    container.layerMeta.displayNone = false
  },
  open_container(state, container) {
    container.containerLayersList.forEach((item)=> {
      let diffTop = item.el.layerMeta.containerDiff.top;
      let diffLeft = item.el.layerMeta.containerDiff.left;
      let top = item.el.layerMeta.position.top;
      let left = item.el.layerMeta.position.left;

      item.el.layerMeta.containerDiff = {
        top: 0,
        left: 0
      };
      item.el.layerMeta.position = {
        top: top - diffTop,
        left: left - diffLeft
      };
      item.el.layerMeta.displayNone = false;
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
  SET_arrowType (state, value) {
    state.arrowType = value.type
  },
  // SET_dragElement(state, value) {
  //   state.dragElement = value
  // },
  SET_startArrowID (state, value) {
    state.startArrowID = value
  },
  SET_preArrowStart (state, value) {
    state.preArrow.start = value;
    state.preArrow.stop = value;
    state.preArrow.show = true
    state.preArrow.type = value.type
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
  ADD_network({commit, dispatch}, net) {
    commit('add_network', {dispatch, net})
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
  // SET_canTestStatistics({commit, getters}, value) {
  //   commit('set_networkCanTesting', {getters, value})
  // },
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
    // setTimeout(()=>{
    //   commit('set_charts_doRequest', {getters});
    //   dispatch('mod_api/API_getStatus', null, {root: true});
    // }, 0);
  },
  //---------------
  //  NETWORK ELEMENTS
  //---------------
  SET_elementSettings({commit, getters}, settings) {
    commit('set_elementSettings', {getters, settings})
  },
  ADD_element({commit, getters}, event) {
    commit('add_element', {getters, event})
  },
  DELETE_element({commit, getters, dispatch}) {
    let net = getters.GET_currentNetworkElementList;
    let arrSelect = getters.GET_currentSelectedEl;
    let arrSelectId = arrSelect.map((el)=>{
      return el.el.layerId
    });
    let newNet = net.filter((el)=>{
      return !arrSelectId.includes(el.layerId)
    });
    commit('delete_elementConnection', {newNet, arrSelectId, dispatch})
  },
  ADD_arrow({commit, getters, dispatch}, stopID) {
    commit('add_arrow', {getters, dispatch, stopID})
  },
  DELETE_arrow({commit, getters, dispatch}, arrow) {
    commit('delete_arrow', {getters, dispatch, arrow})
  },
  SET_elementUnselect({commit, getters}) {
    commit('set_elementUnselect', {getters})
  },
  SET_elementSelect({commit, getters}, value) {
    commit('set_elementSelect', {getters, value})
  },
  SET_elementMultiSelect({commit, getters}, value) {
    commit('set_elementMultiSelect', {getters, value})
  },
  SET_elementInputDim({commit, getters}, value) {
    commit('set_elementInputDim', {getters, value})
  },
  SET_elementOutputDim({commit, getters}, value) {
    commit('set_elementOutputDim', {getters, value})
  },
  CHANGE_elementPosition({commit, getters}, value) {
    commit('change_elementPosition', {getters, value})
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
      timeStamp: new Date().getTime(),
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
