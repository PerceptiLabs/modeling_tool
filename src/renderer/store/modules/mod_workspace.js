const namespaced = true

const state = {
  workspaceContent: [
    {
      networkName: 'Network_1',
      network: [
        {
          layerId: 1,
          layerName: 'Layer Name',
          layerChild: [2,3,5],
          componentName: 'io-input',
          meta: {
            isVisible: true,
            isDraggable: true,
            top: 50,
            left: 50
          }
        }
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
      layerChild: null,
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
  CHANGE_networkValue(context, path, value) {

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
