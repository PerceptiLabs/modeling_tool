const namespaced = true

const state = {
  workspaceContent: [
    {
      networkName: 'Network_1',
      network: [
        {
          layerId: 1,
          layerName: 'Layer Name',
          layerNext: [2, 4],
          componentName: 'IoInput',
          meta: {
            isVisible: true,
            isDraggable: true,
            top: 50,
            left: 60
          }
        },
        {
          layerId: 2,
          layerName: 'Layer Name',
          layerNext: [],
          componentName: 'IoInput',
          meta: {
            isVisible: true,
            isDraggable: true,
            top: 70,
            left: 650
          }
        },
        {
          layerId: 4,
          layerName: 'Layer Name',
          layerNext: [],
          componentName: 'IoInput',
          meta: {
            isVisible: true,
            isDraggable: true,
            top: 600,
            left: 300
          }
        }
      ]
    },
    {
      networkName: 'Network_2',
      network: [
        {
          layerId: 3,
          layerName: 'Layer Name',
          layerNext: [2],
          componentName: 'IoInput',
          meta: {
            isVisible: true,
            isDraggable: true,
            top: 80,
            left: 80
          }
        },

      ]
    }
  ],
  currentNetwork: 0,
  dragElement: {},

}

const mutations = {
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
      layerNext: null,
      componentName: event.target.dataset.component,
      meta: {
        isVisible: true,
        isDraggable: true,
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
