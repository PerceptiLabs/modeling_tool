// import throttle from 'lodash/throttle.js'

const wsHistory = (store)=> {
  // const thrNewSnapshot = throttle((newList)=> {
  //   pushSnapshot(newList);
  // }, 1000);
  store.watch(
    (state)=> state.mod_events.calcArray,
    ()=> {
      if(store.getters['mod_workspace-history/GET_isEnableHistory']) {
        pushSnapshot()
      }
      else store.dispatch('mod_workspace-history/SET_isEnableHistory', true);
    }
  );
  store.watch(
    (state)=> state.mod_workspace.workspaceContent.length,
    ()=> { store.dispatch('mod_workspace-history/UPDATE_networkList') }
  );
  store.watch(
    (state, getters)=> getters['mod_workspace/GET_currentNetwork'].networkName,
    (newName)=> {
      //console.log('update networkName');
      if(store.getters['mod_workspace-history/GET_isEnableHistory']) {
        pushSnapshot()
      }
    }
  );
  // store.watch(
  //   (state, getters)=> getters['mod_workspace/GET_currentNetwork'].networkElementList,
  //   (newList)=> {
  //     //console.log('update networkElementList');
  //     if(store.getters['mod_workspace-history/GET_isEnableHistory']) {
  //       thrNewSnapshot({networkElementList: newList})
  //     }
  //     //else store.dispatch('mod_workspace-history/SET_isEnableHistory', true);
  //   },
  //   {deep: true}
  // );

  function pushSnapshot(value) {
    store.dispatch('mod_workspace-history/PUSH_newSnapshot', value);
  }
};

export default wsHistory
