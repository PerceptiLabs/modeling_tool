

const namespaced = true;

const state = {
  closestElId: null,
  isShiftPressed: false,
  isFirstComponentDragged: false,
  draggedComponnentPosition: {
    x: null,
    y: null,
  }
};

const getters = {
  GET_mod_addComponentState(state) {
    return state;
  }
};

const mutations = {
  SET_shiftKey(state, value) {
    state.isShiftPressed = value;
  },
  SET_draggedComponnentPosition(state, value) {
    state.draggedComponnentPosition.x = value.x;
    state.draggedComponnentPosition.y = value.y;
  },
  SET_FirstComponentDragged(state, value) {
    state.isFirstComponentDragged = value;
  },
  SET_closestElementId(state, elId) {
    state.closestElId = elId
  }
};

const actions = {
  setShiftKey({commit}, value) {
    commit('SET_shiftKey', value);
  },
  setDraggedComponnentPosition({commit}, payload) {
    commit('SET_draggedComponnentPosition', payload);
  },
  setFirstComponentDragged({commit}, payload) {
    commit('SET_FirstComponentDragged', payload)
  },
  setClosestElementId({commit}, elId) {
    commit('SET_closestElementId', elId)
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
