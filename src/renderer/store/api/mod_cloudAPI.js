export const namespacedCloud = true;

export const stateCloud = {
  symPY: 'Cloud API'
};

export const mutationsCloud = {
  SET_symPY(state, value) {
    state.symPY = value
  }
};

export const actionsCloud = {
  PY_func({commit}, num) {
    let a = num.x;
    let b = num.y;
    let result = a + b;
    commit('SET_symPY', result)
  }
};
