const wsForwardBackwardConnections = (store)=> {
  store.watch(
    (state) => state.mod_events.eventIOGenerate,
    () => {
      const fullNetworkElementList = store.getters['mod_workspace/GET_currentNetworkElementList'];
      let connections = {};
      let inputs = {};
      let outputs = {};
      let inputIds = [];
      let outputIds = [];

      Object.keys(fullNetworkElementList).map(networkId => {
        const el = fullNetworkElementList[networkId];
        inputs = {
          ...inputs,
          ...el.inputs,
        };
        outputs = {
          ...outputs,
          ...el.outputs,
        }
      });

      inputIds = Object.keys(inputs).map(key => key);
      outputIds = Object.keys(outputs).map(key => key);

      Object.keys(fullNetworkElementList).map(networkId => {
        connections[networkId] = {
          forward_connections: [],
          backward_connections: [],
        };
      })

      Object.keys(fullNetworkElementList).map(networkId => {
        const el = fullNetworkElementList[networkId];
        const elInputs = el.inputs;

        if (!el.inputs) { return;}

        Object.keys(elInputs).map(inputId => {
          let input = elInputs[inputId];
          if(input.reference_var_id !== null) {

            if(outputIds.indexOf(input.reference_var_id) !== -1) {
              // output of reference element
              let forward_connections_obj = {
                src_var: outputs[input.reference_var_id].name,
                dst_id: networkId,
                dst_var: input.name
              };
              // input
              let backward_connections_obj = {
                src_id: input.reference_layer_id,
                src_var: outputs[input.reference_var_id].name,
                dst_var: input.name,
              };
              connections[networkId].backward_connections.push(backward_connections_obj);
              connections[input.reference_layer_id].forward_connections.push(forward_connections_obj);
            }
          }
        })
      });

      updateForwardBackwardConnections(connections);
   
    }
  );
 
  function updateForwardBackwardConnections(connections) {
    store.dispatch('mod_workspace/updateForwardBackwardConnectionsAction', connections)
  }
};

export default wsForwardBackwardConnections
