//import { generateID }  from "@/core/helpers.js";
const generateID = function(input) {
  let out;
  let stringID = input.toString();
  let dotIndex = stringID.indexOf('.');
  dotIndex > 0 ? out = stringID.slice(0, dotIndex) + stringID.slice(dotIndex + 1) :  out = stringID;
  out = +out;
  return out
};
function createPathNode(path, state) {
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
  preArrow: null
};

const getters = {
  GET_currentNetwork(state)  {
    return state.workspaceContent[state.currentNetwork];
  },
  GET_currentNetworkSettings(state, getters) {
    return state.workspaceContent[state.currentNetwork].networkSettings;
  },
  GET_currentNetworkElementList(state, getters) {
    return state.workspaceContent[state.currentNetwork].networkElementList;
  },
  GET_networkCoreStatus(state, getters) {
    return getters.GET_currentNetwork.networkMeta.coreStatus.Status
  },
  GET_currentSelectedEl: (state, getters) => {
    let selectedIndex = [];
    getters.GET_currentNetworkElementList.forEach(function(el, index, arr) {
      if(el.layerMeta.isSelected) {
        selectedIndex.push({
          index,
          el
        });

      }
    });
    return selectedIndex;
  },
  //---------------
  //  Local CORE DATA
  //---------------

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
  ADD_network (state, net) {
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
      canTestStatistics: false,
      netMode: 'edit',//'addArrow', showStatistic
      coreStatus: {
        Status: 'Waiting' //Created, Training, Validation, Paused, Finished
      }
    };

    net === undefined ? newNetwork = defaultNetwork : newNetwork = net;
    newNetwork.networkMeta = defaultMeta;

    state.workspaceContent.push(newNetwork);
    state.currentNetwork = state.workspaceContent.length - 1;
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
  set_networkCanTesting(state, {get, value}) {
    get.GET_currentNetwork.networkMeta.canTestStatistics = value;
  },
  set_netMode(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.netMode = value;
  },
  set_openStatistics(state, {getters, value}) {
    getters.GET_currentNetwork.networkMeta.openStatistics = value;
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
    state.dragElement.layerMeta.top = event.offsetY - top;
    state.dragElement.layerMeta.left = event.offsetX - left;
    getters.GET_currentNetworkElementList.push(state.dragElement);
    state.dragElement = {};
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
  delete_arrow(state, {newNet, arrSelectId, dispatch}) {
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


  /*-- NETWORK ELEMENTS SETTINGS --*/
  set_elementSettings(state, {getters, settings}) {
    let indexEl = getters.GET_currentSelectedEl[0].index;
    getters.GET_currentNetworkElementList[indexEl].layerSettings = settings; //TODO NEED CHECK
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
      layerSettings: null,
      layerMeta: {
        isInvisible: false,
        isLock: false,
        isSelected: false,
        top: event.target.clientHeight/2,
        left: event.target.clientWidth/2
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
  // SET_preArrow (state, value) {
  //   state.preArrow = value
  // },
};

const actions = {
  //---------------
  //  NETWORK
  //---------------
  SET_networkName({commit, getters}, value) {
    commit('set_networkName', {getters, value})
  },
  SET_networkSettings({commit, getters}, value) {
    commit('set_networkSettings', {getters, value})
  },
  SET_networkElementList({commit, getters}, value) {
    commit('set_networkElementList', {getters, value})
  },
  SET_canTestStatistics({commit, getters}, value) {
    commit('set_networkCanTesting', {getters, value})
  },
  SET_netMode({commit, getters}, value) {
    commit('set_netMode', {getters, value})
  },
  SET_openStatistics({commit, getters}, value) {
    commit('set_openStatistics', {getters, value})
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
    commit('delete_arrow', {newNet, arrSelectId, dispatch})
  },
  ADD_arrow({commit, getters, dispatch}, stopID) {
    commit('add_arrow', {getters, dispatch, stopID})
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
