function createPathNode(path, state) {
  const network = path.slice();
  const networkId = network.shift();
  const initValue = state.workspaceContent[state.currentNetwork].network[networkId];
  return network.reduce((acc, id) => acc.child[id], initValue);

}

const namespaced = true;

const state = {
  workspaceContent: [
    {
      networkName: 'Network_1',
      network: [
        {
          layerId: 1,
          layerName: 'Layer Name1',
          connectionIn: [],
          connectionOut: [{
            id: 2,
            side: '',
            type: 'dash1'
          }, {
            id: 4,
            side: '',
            type: 'dash2'
          }],
          componentName: 'IoInput',
          meta: {
            isInvisible: false,
            isLock: false,
            isSelected: false,
            isDragged: false,
            top: 300,
            left: 200
          },
        },
        {
          layerId: 2,
          layerName: 'Layer Name2',
          connectionOut: [],
          connectionIn: [{
            id: 1,
            side: '',
          }],
          componentName: 'IoInput',
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
              layerName: 'Layer Name21',
              layerNext: [],
              componentName: 'IoInput',
              meta: {
                isInvisible: true,
                isLock: false,
                isSelected: false,
                top: 50,
                left: 60
              },
              child: [
                {
                  layerId: 211,
                  layerName: 'Layer Name211',
                  layerNext: [],
                  componentName: 'IoInput',
                  meta: {
                    isInvisible: true,
                    isLock: false,
                    isSelected: false,
                    top: 50,
                    left: 60
                  }
                },
                {
                  layerId: 212,
                  layerName: 'Layer Name212',
                  layerNext: [],
                  componentName: 'IoInput',
                  meta: {
                    isInvisible: true,
                    isLock: false,
                    isSelected: false,
                    top: 50,
                    left: 60
                  },
                  child: [
                    {
                      layerId: 2121,
                      layerName: 'Layer Name 2121',
                      layerNext: [],
                      componentName: 'IoInput',
                      meta: {
                        isInvisible: true,
                        isLock: false,
                        isSelected: false,
                        top: 50,
                        left: 60
                      },
                    },
                    {
                      layerId: 2122,
                      layerName: 'Layer Name 2122',
                      layerNext: [],
                      componentName: 'IoInput',
                      meta: {
                        isInvisible: true,
                        isLock: false,
                        isSelected: false,
                        top: 50,
                        left: 60
                      },
                    },
                  ]
                },
              ]
            },
            {
              layerId: 12,
              layerName: 'Layer Name12',
              layerNext: [2, 4],
              componentName: 'IoInput',
              meta: {
                isInvisible: true,
                isLock: false,
                isSelected: false,
                top: 50,
                left: 60
              },
            }
          ]
        },
        {
          layerId: 4,
          layerName: 'Layer Name3',
          connectionOut: [],
          connectionIn: [{
            id: 1,
            side: '',
          }],
          componentName: 'IoInput',
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
          layerName: 'Layer Name5',
          connectionOut: [{
            id: 1,
            side: '',
            type: 'solid'
          }],
          connectionIn: [],
          componentName: 'IoInput',
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
      network: [
        {
          layerId: 1,
          layerName: 'Layer Name1',
          layerNext: [],
          componentName: 'IoInput',
          meta: {
            isInvisible: false,
            isLock: false,
            isSelected: false,
            isDragged: false,
            top: 80,
            left: 80
          },
        },
      ]
    }
  ],
  currentNetwork: 0,
  dragElement: {},
};

const mutations = {
  SET_metaSelect(state, value) {
    // let node = createPathNode(value.path, state);
    // node.meta.isSelected = value.setValue

  },
  SET_metaDragged(state, value) {
    let node = createPathNode(value.path, state);
    node.meta.isDragged = value.setValue
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

  SET_dragElement(state, value) {
    state.dragElement = value
  },
  SET_currentNetwork(state, value) {
    state.currentNetwork = value
  },
  SET_workspaceContent (state, value) {
    state.workspaceContent = value
  },
  ADD_workspace (state) {
    let newNetwork = {
      networkName: 'Network',
      network: []
    }
    state.workspaceContent.push(newNetwork);
  },
  ADD_dragElement(state, event) {
    var newLayer = {
      layerId: event.timeStamp,
      layerName: event.target.dataset.layer,
      layerNext: [],
      componentName: event.target.dataset.component,
      meta: {
        isInvisible: false,
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
  state,
  mutations,
  actions
}
