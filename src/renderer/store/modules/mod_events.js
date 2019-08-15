import {ipcRenderer}  from 'electron'
import router         from "@/router";
import {fileLocalRead, openLoadDialog} from "@/core/helpers";

const namespaced = true;

const state = {
  calcArray: 0,
  openNetwork: 0,
  saveNetwork: 0,
  saveNetworkAs: 0,
  eventResize: 0,
  runNetwork: false,
  globalPressKey: {
    del: 0,
    esc: 0
  }
};

const mutations = {
  set_calcArray(state) {
    state.calcArray++
  },
  set_saveNetwork(state) {
    state.saveNetwork++
  },
  set_saveNetworkAs(state) {
    state.saveNetworkAs++
  },
  set_eventResize(state) {
    state.eventResize++
  },
  set_runNetwork(state, value) {
    state.runNetwork = value
  },
  set_globalPressKey(state, path) {
    state.globalPressKey[path]++
  },
};

const actions = {
  EVENT_calcArray({commit}) {
    commit('set_calcArray')
  },
  EVENT_loadNetwork({dispatch}, pathArr) {
    let localProjectsList = localStorage.getItem('projectsList');
    let projectsList, pathIndex;
    if(localProjectsList) {
      projectsList = JSON.parse(localProjectsList);
      pathIndex = projectsList.findIndex((proj)=> proj.path[0] === pathArr[0]);
    }
    return fileLocalRead(pathArr[0])
      .then((data) => {
        //validate JSON
        let net = {};
        net = JSON.parse(data.toString());
        //console.log('net', net);
        // try {
        //   net = JSON.parse(data.toString());
        //
        // }
        // catch(e) {
        //   this.$store.dispatch('globalView/GP_infoPopup', 'JSON file is not valid');
        //   return
        // }
        //validate model
        // try {
        //   if(!(net.network.networkName && net.network.networkID && net.network.networkMeta && net.network.networkElementList)) {
        //     throw ('err')
        //   }
        // }
        // catch(e) {
        //   this.$store.dispatch('globalView/GP_infoPopup', 'The model is not valid');
        //   return;
        // }
        if(pathIndex > -1 && projectsList) {
          net.network.networkID = projectsList[pathIndex].id;
        }
        dispatch('mod_workspace/ADD_network', net.network, {root: true});
      }
    );
  },
  EVENT_openNetwork({dispatch}) {
    const opt = {
      title:"Load Model",
      filters: [
        {name: 'Text', extensions: ['json']},
      ]
    };
    openLoadDialog(opt)
      .then((pathArr)=> {
        dispatch('EVENT_loadNetwork', pathArr)
      })
      .catch((err)=> {});
  },
  EVENT_saveNetwork({commit}) {
    commit('set_saveNetwork');
  },
  EVENT_saveNetworkAs({commit}) {
    commit('set_saveNetworkAs');
  },
  EVENT_logOut({dispatch}) {
    localStorage.removeItem('userToken');
    dispatch('mod_user/SET_userToken', '', {root: true});
    dispatch('mod_workspace/RESET_network', null, {root: true});
    router.replace({name: 'login'});
  },
  EVENT_appClose({dispatch, rootState}, event) {
    if(event) event.preventDefault();
    dispatch('mod_tracker/EVENT_appClose', null, {root: true});
    if(rootState.mod_api.statusLocalCore === 'online') {
      dispatch('mod_api/API_stopTraining', null, {root: true})
        .then(()=> dispatch('mod_api/API_CLOSE_core', null, {root: true}))
        .then(()=> ipcRenderer.send('app-close'));
    }
    else {
      ipcRenderer.send('app-close')
    }
  },
  EVENT_appMinimize() {
    ipcRenderer.send('app-minimize')
  },
  EVENT_appMaximize() {
    ipcRenderer.send('app-maximize')
  },
  EVENT_eventResize({commit}) {
    commit('set_eventResize');

  },
  EVENT_pressHotKey({commit}, hotKeyName) {
    commit('set_globalPressKey', hotKeyName)
  },
  EVENT_hotKeyEsc({commit, rootGetters, dispatch}) {
    commit('set_globalPressKey', 'esc');
  },
  EVENT_hotKeyCopy({rootGetters, dispatch}) {
    if(rootGetters['mod_workspace/GET_networkIsOpen']) {
      let arrSelect = rootGetters['mod_workspace/GET_currentSelectedEl'];
      let arrBuf = [];
      arrSelect.forEach((el) => {
        let newEl = {
          target: {
            dataset: {
              layer: el.layerName,
              type: el.layerType,
              component: el.componentName
            },
            clientHeight: el.layerMeta.position.top * 2,
            clientWidth: el.layerMeta.position.left * 2,
          },
          layerSettings: el.layerSettings,
          offsetY: el.layerMeta.position.top * 2,
          offsetX: el.layerMeta.position.left * 2
        };
        arrBuf.push(newEl)
      });

      dispatch('mod_buffer/SET_buffer', arrBuf, {root: true});
    }
  },
  EVENT_hotKeyPaste({rootState, rootGetters, dispatch}) {
    let buffer = rootState.mod_buffer.buffer;
    if(rootGetters['mod_workspace/GET_networkIsOpen'] && buffer) {
      buffer.forEach((el) => {
        dispatch('mod_workspace/ADD_element', el, {root: true});
      });
      dispatch('mod_buffer/CLEAR_buffer', null, {root: true});
    }
  },
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
