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
      networkName: 'Network_1',
      networkSettings: {
        isEmpty: true,
      },
      networkStatistics: null,
      network: [
        {
          layerId: 1,
          layerName: 'Layer Name 1',
          connectionOut: [{
            id: 2,
            type: 'dash1'
          }, {
            id: 4,
            type: 'dash2'
          }],
          componentName: 'DataData',
          meta: {
            isInvisible: false,
            isLock: false,
            isSelected: false,
            top: 300,
            left: 200
          },
        },
        {
          layerId: 2,
          layerName: 'Layer Name 2',
          connectionOut: [],
          componentName: 'LayerContainer',
          meta: {
            isInvisible: false,
            isLock: false,
            isSelected: false,
            top: 200,
            left: 650
          },
          child: [
            {
              layerId: 21,
              layerName: 'Layer Name 21',
              connectionOut: [],
              componentName: 'LayerContainer',
              meta: {
                isInvisible: false,
                isLock: false,
                isSelected: false,
                top: 50,
                left: 60
              },
              child: [
                {
                  layerId: 211,
                  layerName: 'Layer Name 211',
                  connectionOut: [],
                  componentName: 'IoInput',
                  meta: {
                    isInvisible: false,
                    isLock: false,
                    isSelected: false,
                    top: 50,
                    left: 60
                  }
                },
                {
                  layerId: 212,
                  layerName: 'Layer Name 212',
                  connectionOut: [],
                  componentName: 'LayerContainer',
                  meta: {
                    isInvisible: false,
                    isLock: false,
                    isSelected: false,
                    top: 50,
                    left: 160
                  },
                  child: [
                    {
                      layerId: 2121,
                      layerName: 'Layer Name 2121',
                      connectionOut: [],
                      componentName: 'IoInput',
                      meta: {
                        isInvisible: false,
                        isLock: false,
                        isSelected: false,
                        top: 50,
                        left: 60
                      },
                    },
                    {
                      layerId: 2122,
                      layerName: 'Layer Name 2122',
                      connectionOut: [],
                      componentName: 'IoInput',
                      meta: {
                        isInvisible: false,
                        isLock: false,
                        isSelected: false,
                        top: 250,
                        left: 60
                      },
                    },
                  ]
                },
              ]
            },
            {
              layerId: 22,
              layerName: 'Layer Name 22',
              connectionOut: [{
                id: 21,
                type: 'dash1'
              }],
              componentName: 'IoInput',
              meta: {
                isInvisible: false,
                isLock: false,
                isSelected: false,
                top: 150,
                left: 60
              },
            }
          ]
        },
        {
          layerId: 4,
          layerName: 'Layer Name 3',
          connectionOut: [],
          componentName: 'LearnClassVectorMachine',
          meta: {
            isInvisible: false,
            isLock: false,
            isSelected: false,
            top: 400,
            left: 650
          }
        },
        {
          layerId: 5,
          layerName: 'Layer Name 5',
          connectionOut: [{
            id: 1,
            type: 'solid'
          }],
          componentName: 'TrainGenetic',
          meta: {
            isInvisible: false,
            isLock: false,
            isSelected: false,
            top: 300,
            left: 650
          }
        }
      ]
    },
    {
      networkName: 'Network_2',
      networkSettings: {
        isEmpty: true,
      },
      networkStatistics: null,
      network: [
        {
          layerId: 1,
          layerName: 'Layer Name1',
          connectionOut: [],
          componentName: 'IoInput',
          meta: {
            isInvisible: false,
            isLock: false,
            isSelected: false,
            top: 80,
            left: 80
          },
        },
      ]
    }
  ],
  currentNetwork: 0,
  dragElement: {},
  arrowType: 'solid',
  startArrowID: null
};

const getters = {
  currentNetworkSettings: (state) => {
    return state.workspaceContent[state.currentNetwork].networkSettings;
  }
}


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
  SET_startArrowID (state, value) {
    state.startArrowID = value
  },
  SET_arrowType (state, value) {
    state.arrowType = value.type
  },
  ADD_workspace (state) {
    let newNetwork = {
      networkName: 'Network',
      networkSettings: {
        isEmpty: true,
      },
      network: []
    };
    state.workspaceContent.push(newNetwork);
  },
  ADD_dragElement(state, event) {
    var newLayer = {
      layerId: event.timeStamp,
      layerName: event.target.dataset.layer,
      connectionOut: [],
      componentName: event.target.dataset.component,
      meta: {
        //isInvisible: false,
        isLock: false,
        isSelected: false,
        top: event.target.clientHeight/2,
        left: event.target.clientWidth/2
      }
    };
    state.dragElement = newLayer;
  },
  ADD_elToWorkspace(state, event) {
    let top = state.dragElement.meta.top;
    let left = state.dragElement.meta.left;
    let net = state.currentNetwork;
    state.dragElement.meta.top = event.offsetY - top;
    state.dragElement.meta.left = event.offsetX - left;
    state.workspaceContent[net].network.push(state.dragElement);
  },
  ADD_arrow(state, stopID) {
    let startID = state.startArrowID;
    if(stopID == startID) {
      return
    }
    let pathNet = state.workspaceContent[state.currentNetwork];
    let indexStart = pathNet.network.findIndex((element, index, array)=> { return element.layerId == startID;});
    let findArrowType = pathNet.network[indexStart].connectionOut.findIndex((element, index, array)=> { return element.type == state.arrowType;});
    if(findArrowType !== -1) {
      alert('This type of connection already exists!');
      return
    }
    pathNet.network[indexStart].connectionOut.push({
      id: stopID,
      type: state.arrowType
    });
    state.startArrowID = null;
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
}

const actions = {


}

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions
}
