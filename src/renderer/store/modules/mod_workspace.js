function createPathNode(path, state) {
  const network = path.slice();
  const networkId = network.shift();
  const initValue = state.workspaceContent[state.currentNetwork].network[networkId];
  return network.reduce((acc, id) => acc.child[id], initValue);

}

const namespaced = true;

const state = {
  //TODO delete isInvisible
  workspaceContent: [
    {
      networkName: 'Network',
      networkSettings: null,
      networkMeta: {
        openStatistics: false,
        canTestStatistics: false,
        netMode: 'edit',
        coreStatus: {
          Status: 'Offline' //Created, Training, Validation, Paused, Finished
        }
      },
      network: [],
    }
  ],
  currentNetwork: 0,
  dragElement: {},
  arrowType: 'solid',
  startArrowID: null,
  preArrow: null
};

const getters = {
  GET_currentNetwork(state)  {
    return state.workspaceContent[state.currentNetwork];
  },
  GET_currentNetworkNet(state, getters) {
    return getters.GET_currentNetwork.network;
  },
  GET_currentNetworkSettings(state, getters) {
    return getters.GET_currentNetwork.networkSettings;
  },
  // currentSelectedElement: (state, getters) => {
  //   let selectedElements = getters.currentNetworkNet.filter(function(el) {
  //     return el.meta.isSelected;
  //   });
  //   console.log(selectedElements);
  //   return selectedElements;
  // },
  GET_currentSelectedEl: (state, getters) => {
    let selectedIndex = [];
    getters.GET_currentNetworkNet.forEach(function(el, index, arr) {
      if(el.meta.isSelected) {
        selectedIndex.push({
          index,
          el
        });

      }
    });
    return selectedIndex;
  },
  GET_API_dataCloseServer(state, getters) {
    return {
      reciever: getters.GET_currentNetwork.networkName,
      action: 'Close',
      value: ''
    };
  },
  GET_API_dataPauseTraining(state, getters) {
    return {
      reciever: getters.GET_currentNetwork.networkName,
      action: 'Pause',
      value: ''
    };
  },
  GET_API_dataStopTraining(state, getters) {
    return {
      reciever: getters.GET_currentNetwork.networkName,
      action: 'Stop',
      value: ''
    };
  },
  GET_API_dataSkipValidTraining(state, getters) {
    return {
      reciever: getters.GET_currentNetwork.networkName,
      action: 'SkipToValidation',
      value: ''
    }
  },
  GET_API_dataGetStatus(state, getters) {
    return {
      reciever: getters.GET_currentNetwork.networkName,
      action: 'getStatus', //getIter
      value: ''
    };
  },
};

const mutations = {
  SET_metaSelect(state, value) {
    //console.log(value);
    //let node = createPathNode(value.path, state);
    //node.meta.isSelected = value.setValue
    let pathNet = state.workspaceContent[state.currentNetwork];
    pathNet.network.forEach((el)=>{
      el.meta.isSelected = false;
    });
    pathNet.network[value.path].meta.isSelected = value.setValue;
  },
  SET_metaMultiSelect(state, value) {
    let pathNet = state.workspaceContent[state.currentNetwork];
    pathNet.network[value.path].meta.isSelected = value.setValue;
  },
  SET_metaLock(state, value) {
    let node = createPathNode(value, state);
    node.meta.isLock = !node.meta.isLock
  },
  SET_metaVisible(state, value) {
    let node = createPathNode(value, state);
    node.meta.isInvisible = !node.meta.isInvisible
  },
  SET_layerName(state, value) {
    let node = createPathNode(value.path, state);
    node.layerName = value.setValue
  },
  SET_networkNet(state, value) {
    state.workspaceContent[state.currentNetwork].network = value
  },
  SET_networkName(state, value) {
    state.workspaceContent[state.currentNetwork].networkName = value
  },
  SET_networkSettings(state, value) {
    state.workspaceContent[state.currentNetwork].networkSettings = value
  },
  SET_dragElement(state, value) {
    state.dragElement = value
  },
  SET_currentNetwork(state, value) {
    state.currentNetwork = value
  },
  SET_workspaceContent (state, value) {
    state.workspaceContent = value
  },
  SET_preArrow (state, value) {
    state.preArrow = value
  },
  SET_startArrowID (state, value) {
    state.startArrowID = value
  },
  SET_arrowType (state, value) {
    state.arrowType = value.type
  },
  SET_networkStatistics(state, {value, get}) {
    get.GET_currentNetwork.networkStatistics = value
  },
  SET_canTestStatistics(state, {value, get}) {
    get.GET_currentNetwork.canTestStatistics = value;
  },
  SET_elementSettings(state, {settings, getters}) {
    let indexEl = getters.GET_currentSelectedEl[0].index;
    getters.GET_currentNetworkNet[indexEl].layerSettings = settings; //TODO NEED CHECK
  },
  // ADD_workspace (state) {
  //   let newNetwork = {
  //     networkName: 'Network',
  //     networkSettings: {
  //       isEmpty: true,
  //     },
  //     emptyTrainingData: true,
  //     network: []
  //   };
  //   state.workspaceContent.push(newNetwork);
  // },
  ADD_loadNetwork (state, net) {
    let newNetwork = {};
    if(net === undefined) {
      newNetwork = {
        networkName: 'New_Network',
        networkSettings: {
          //isEmpty: true,
        },
        emptyTrainingData: true,
        networkMeta: {
          openStatistics: false,
          canTestStatistics: false,
          netMode: 'edit',
          coreStatus: {
            Status: 'Offline' //Created, Training, Validation, Paused, Finished
          }
        },
        network: []
      }
    }
    else {
      newNetwork = net;
    }
    state.workspaceContent.push(newNetwork);
    let lastIndex = state.workspaceContent.length - 1;
    state.currentNetwork = lastIndex;
  },
  ADD_dragElement(state, event) {
    let newLayer = {
      layerId: generateID(event.timeStamp).toString(),
      layerName: event.target.dataset.layer,
      layerType: event.target.dataset.type,
      layerSettings: null,
      componentName: event.target.dataset.component,
      connectionOut: [],
      connectionIn: [],
      meta: {
        //isInvisible: false,
        isLock: false,
        isSelected: false,
        top: event.target.clientHeight/2,
        left: event.target.clientWidth/2
      },
      trainingData: null
    };
    state.dragElement = newLayer;

    function generateID(input) {
      let out;
      let stringID = input.toString();
      let dotIndex = stringID.indexOf('.');
      dotIndex > 0 ? out = stringID.slice(0, dotIndex) + stringID.slice(dotIndex + 1) :  out = stringID;
      out = +out;
      return out
    }
  },
  ADD_elToWorkspace(state, event) {
    let top = state.dragElement.meta.top;
    let left = state.dragElement.meta.left;
    let net = state.currentNetwork;
    state.dragElement.meta.top = event.offsetY - top;
    state.dragElement.meta.left = event.offsetX - left;
    state.workspaceContent[net].network.push(state.dragElement);
    state.dragElement = {};
  },
  ADD_arrow(state, val) {

    let startID = state.startArrowID;
    let stopID = val.stopID;
    if(stopID == startID) {
      return
    }
    let pathNet = val.getters.GET_currentNetwork;
    let indexStart = pathNet.network.findIndex((element, index, array)=> { return element.layerId == startID;});
    let findArrowType = pathNet.network[indexStart].connectionOut.findIndex((element, index, array)=> { return element.type == state.arrowType;});
    if(findArrowType !== -1) {
      alert('This type of connection already exists!');
      return
    }
    // pathNet.network[indexStart].connectionOut.push({
    //   id: val.stopID,
    //   type: state.arrowType
    // });

    //TODO start only one type connection
    pathNet.network[indexStart].connectionOut.push(stopID.toString()); //ID.toString need for the core

    let indexStop = pathNet.network.findIndex((element, index, array)=> { return element.layerId == stopID;});
    pathNet.network[indexStop].connectionIn.push(startID.toString());
    //stop only one type connection
    state.startArrowID = null;
    val.dispatch('mod_events/EVENT_calcArray', null, {root: true})
  },
  SHOW_layerContainer(state, index) {
    let box = state.workspaceContent[state.currentNetwork].network[index];
    let newTab = {
      networkName: box.layerName,
      network: box.child
    };
    state.workspaceContent.push(newTab);
    state.currentNetwork = state.workspaceContent.length - 1;
  },
  DELETE_workspaceTab(state, index) {
    if(state.currentNetwork >= index) {
      state.currentNetwork = state.currentNetwork - 1
    }
    state.workspaceContent.splice(index, 1);
  },
  CHANGE_networkValue(state, path, value) {

  },
  CHANGE_elementPosition(state, value) {
    let el = value.index;
    let net = state.currentNetwork;
    state.workspaceContent[net].network[el].meta.top = value.top;
    state.workspaceContent[net].network[el].meta.left = value.left;
  },
  DELETE_elConnection(state, value) {
    value.newNet.forEach((el)=>{
      el.connectionOut = el.connectionOut.filter((connect)=>{
        //TODO return when return arrowType
        //return !value.arrSelectId.includes(connect.id)
        return !value.arrSelectId.includes(connect)
      });
      el.connectionIn  = el.connectionOut.filter((connect)=>{
        //TODO return when return arrowType
        //return !value.arrSelectId.includes(connect.id)
        return !value.arrSelectId.includes(connect)
      });
    });
    state.workspaceContent[state.currentNetwork].network = value.newNet;
    value.dispatch('mod_events/EVENT_calcArray', null, {root: true})
  }
};

const actions = {
  a_SET_elementSettings({commit, getters}, settings) {
    commit('SET_elementSettings', {settings, getters})
  },
  a_SET_networkStatistics({commit, getters}, value) {
    commit('SET_networkStatistics', {value, get: getters})
  },
  a_SET_canTestStatistics({commit, getters}, value) {
    commit('SET_canTestStatistics', {value, get: getters})
  },
  DELETE_netElement({commit, getters, dispatch}) {
    let net = getters.GET_currentNetworkNet;
    let arrSelect = getters.GET_currentSelectedEl;
    let arrSelectId = arrSelect.map((el)=>{
      return el.el.layerId
    });
    let newNet = net.filter((el)=>{
      return !arrSelectId.includes(el.layerId)
    });
    commit('DELETE_elConnection', {newNet, arrSelectId, net, dispatch})
  },
  a_ADD_arrow({commit, getters, dispatch}, stopID) {
    commit('ADD_arrow', {getters, dispatch, stopID})
  }
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions
}
