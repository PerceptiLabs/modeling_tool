import { findIndexId, generateID }  from "@/core/helpers.js";
// const generateID = function(input) {
//   let out;
//   let stringID = input.toString();
//   let dotIndex = stringID.indexOf('.');
//   dotIndex > 0 ? out = stringID.slice(0, dotIndex) + stringID.slice(dotIndex + 1) :  out = stringID;
//   out = +out;
//   return out
// };
function createPathNode(path, state) {
  //console.log('createPathNode');
  const network = path.slice();
  const networkId = network.shift();
  const initValue = state.workspaceContent[state.currentNetwork].networkElementList[networkId];
  return network.reduce((acc, id) => acc.child[id], initValue);

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
  GET_currentNetwork(state)  {
    if(state.workspaceContent.length) {
      return state.workspaceContent[state.currentNetwork];
    }
    return ['empty app']
  },
  GET_currentNetworkSettings(state, getters) {
    if(state.workspaceContent.length) {
      return state.workspaceContent[state.currentNetwork].networkSettings;
    }
    return {}
  },
  GET_currentNetworkElementList(state, getters) {
    if(state.workspaceContent.length) {
      return state.workspaceContent[state.currentNetwork].networkElementList;
    }
    return ['empty app']
  },
  GET_networkCoreStatus(state, getters) {
    if(state.workspaceContent.length) {
      return getters.GET_currentNetwork.networkMeta.coreStatus.Status
    }
    return 'empty app'
  },
  GET_currentSelectedEl(state, getters) {
    let selectedIndex = [];
    if(state.workspaceContent.length) {
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
      networkID: 'net' + generateID(Date.now()),
      networkSettings: null,
      networkMeta: {},
      networkElementList: []
    };
    let defaultMeta = {
      openStatistics: null, //null - hide Statistics; false - close Statistics, true - open Statistics
      openTest: null,
      //canTestStatistics: false,
      zoom: 1,
      netMode: 'edit',//'addArrow', showStatistic
      coreStatus: {
        Status: 'Waiting' //Created, Training, Validation, Paused, Finished
      }
    };

    net.network === undefined ? newNetwork = defaultNetwork : newNetwork = net.network;
    newNetwork.networkMeta = defaultMeta;

    state.workspaceContent.push(newNetwork);
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
  set_statusNetworkZoom(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.zoom = value;
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
    let top = state.dragElement.layerMeta.top;
    let left = state.dragElement.layerMeta.left;
    let zoom = getters.GET_currentNetwork.networkMeta.zoom;

    state.dragElement.layerMeta.top = (event.offsetY - top)/zoom;
    state.dragElement.layerMeta.left = (event.offsetX - left)/zoom;
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
    //let stopID = val.stopID;
    if(stopID == startID) {
      return
    }
    let pathNet = getters.GET_currentNetworkElementList;
    let indexStart = pathNet.findIndex((element, index, array)=> { return element.layerId == startID;});
    let findArrowType = pathNet[indexStart].connectionOut.findIndex((element, index, array)=> { return element.type == state.arrowType;});
    if(findArrowType !== -1) {
      alert('This type of connection already exists!');
      return
    }
    // pathNet.network[indexStart].connectionOut.push({
    //   id: val.stopID,
    //   type: state.arrowType
    // });

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
    net[el].layerMeta.top = value.top;
    net[el].layerMeta.left = value.left;
  },
  set_elementBeForEnd(state, {getters, value}) {
    //console.log('set_elementBeForEnd', value);
    getters.GET_currentNetworkElementList.forEach((el)=>{
      el.layerMeta.OutputDim = value[el.layerId].OutputDim;
      el.layerMeta.InputDim = value[el.layerId].InputDim
      // if(el.layerMeta.OutputDim) {
      //
      // }
      // if(el.layerMeta.InputDim) {
      //
      // }
    });
  },

  //---------------
  //  OTHER
  //---------------
  SET_currentNetwork(state, value) {
    state.currentNetwork = value
  },
  ADD_dragElement(state, event) {
    let newLayer = {
      layerId: generateID(event.timeStamp).toString(),
      layerName: event.target.dataset.layer,
      layerType: event.target.dataset.type,
      layerSettings: '',
      layerCode: '',
      layerMeta: {
        isInvisible: false,
        isLock: false,
        isSelected: false,
        top: event.target.clientHeight/2,
        left: event.target.clientWidth/2,
        OutputDim: '',
        InputDim: ''
      },
      componentName: event.target.dataset.component,
      connectionOut: [],
      connectionIn: [],
      trainingData: null
    };
    state.dragElement = newLayer;
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
  SET_statusNetworkZoom({commit, getters}, value) {
    commit('set_statusNetworkZoom', {getters, value})
  },
  RESET_network({commit}) {
    commit('RESET_network')
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
  SET_elementBeForEnd({commit, getters}, value) {
    commit('set_elementBeForEnd', {getters, value})
  },
  CHANGE_elementPosition({commit, getters}, value) {
    commit('change_elementPosition', {getters, value})
  },

};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions
}
