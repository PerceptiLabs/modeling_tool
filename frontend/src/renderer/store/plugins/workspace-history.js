import throttle from 'lodash/throttle.js'

const wsHistory = (store)=> {
  const thrNewSnapshot = throttle((newList)=> {
    pushSnapshot(newList);
  }, 1000);

  store.watch(
    (state)=> state.mod_workspace.workspaceContent.length,
    ()=> { store.dispatch('mod_workspace-history/UPDATE_networkList') }
  );
  store.watch(
    (state, getters)=> getters['mod_workspace/GET_currentNetwork'].networkName,
    (newName)=> {
      if(store.getters['mod_workspace-history/GET_isEnableHistory']) {
        pushSnapshot({networkName: newName})
      }
    }
  );
  store.watch(
    (state, getters)=> getters['mod_workspace/GET_currentNetwork'].networkElementList,
    (newList)=> {
      if(store.getters['mod_workspace-history/GET_isEnableHistory']) {
        thrNewSnapshot({networkElementList: newList})
      }
    },
    {deep: true}
  );

  function pushSnapshot(value) {
    store.dispatch('mod_workspace-history/PUSH_newSnapshot', value);
  }
};

export default wsHistory
