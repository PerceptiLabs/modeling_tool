//import { throttleEv } from '@/core/helpers.js'
import throttle from 'lodash/throttle.js'
import {pathWebWorkers} from '@/core/constants.js'
// import debounce from 'lodash/debounce.js'

const diff = {
  "obj": {"obj1": {"string2": "New_Network"}},
  "array": {"0": "1569587805562"},
  "arrayObj": {"0": {"a": 1}}
};
const var1 = {
  "string": "New_Network",
  "number": 10,
  "udef": undefined,
  "bool": true,
  "null": null,
  "obj": {
    "string1": "New_Network",
    "obj1": {
      "string2": "New_Network1",
    },
  },
  "array": ["1", "1569587805563"],
  "arrayEm": [],
  "arrayObj": [{a: 11}, {b: 2}, {c: 3}],
  // "obj": {
  //   "1569587801334": {
  //     "string": "New_Network",
  //     "number": 10,
  //     "null": null,
  //     "udef": undefined,
  //     "bool": true,
  //     "array": ["1569587805562", "1569587805563"],
  //     "arrayEm": [],
  //     "arrayObj": [{a:1}, {b:2}, {c:3}],
  //   },
  //   "1569587805562": {
  //     "string": "New_Network",
  //     "number": 10,
  //     "null": null,
  //     "udef": undefined,
  //     "bool": true,
  //     "array": ["1569587805562", "1569587805563"],
  //     "arrayEm": [],
  //     "arrayObj": [{a:1}, {b:2}, {c:3}],
  //   }
  // },
}

const var2 = {
  "string": "New_Network",
  "number": 10,
  "udef": undefined,
  "bool": true,
  "null": null,
  "obj": {
    "string1": "New_Network",
    "obj1": {
      "string2": "New_Network",
    },
  },
  "array": ["1569587805562", "1569587805563"],
  "arrayEm": [],
  "arrayObj": [{a: 1}, {b: 2}, {c: 3}],
  // "obj": {
  //   "1569587801334": {
  //     "string": "New_Network",
  //     "number": 10,
  //     "null": null,
  //     "udef": undefined,
  //     "bool": true,
  //     "array": ["1569587805562", "1569587805563"],
  //     "arrayEm": [],
  //     "arrayObj": [{a:1}, {b:2}, {c:3}],
  //   },
  //   "1569587805562": {
  //     "string": "New_Network",
  //     "number": 10,
  //     "null": null,
  //     "udef": undefined,
  //     "bool": true,
  //     "array": ["1569587805562", "1569587805563"],
  //     "arrayEm": [],
  //     "arrayObj": [{a:1}, {b:2}, {c:3}],
  //   }
  // },
}
const var3 = {
  "networkName": "New_Network",
  "network": "Network1",
  "networkElementList": {
    "1569587801334": {
      "layerId": "1569587801334",
      "layerName": "Data_1",
      "layerType": "Data",
      "layerSettings": null,
      "layerCode": "",
      "layerCodeError": null,
      "layerNone": false,
      "layerMeta": {
        "isInvisible": false,
        "isLock": false,
        "isSelected": false,
        "position": {"top": 1254, "left": 516},
        "OutputDim": "",
        "InputDim": "",
        "layerContainerName": "",
        "layerBgColor": "",
        "containerDiff": {"top": 0, "left": 0}
      },
      "checkpoint": [],
      "endPoints": [],
      "componentName": "DataData",
      "connectionOut": ["1569587805562"],
      "connectionIn": [],
      "connectionArrow": ["1569587805562"]
    },
    "1569587805562": {
      "layerId": "1569587805562",
      "layerName": "Reshape_1",
      "layerType": "Other",
      "layerSettings": null,
      "layerCode": "",
      "layerCodeError": null,
      "layerNone": true,
      "layerMeta": {
        "isInvisible": false,
        "isLock": false,
        "isSelected": false,
        "position": {"top": 307, "left": 798},
        "OutputDim": "",
        "InputDim": "",
        "layerContainerName": "",
        "layerBgColor": "",
        "containerDiff": {"top": 0, "left": 0}
      },
      "checkpoint": [],
      "endPoints": [],
      "componentName": "ProcessReshape",
      "connectionOut": [],
      "connectionIn": ["1569587801334"],
      "connectionArrow": []
    }
  },
}

const wsHistory = (store) => {
  function pushSnapshot(answer) {
    console.log('pushSnapshot', answer.data);
    store.dispatch('mod_workspace-history/PUSH_newSnapshot', answer.data)
  }

  const wWorker = new Worker(`${pathWebWorkers}/findDiffObject.js`);
  wWorker.addEventListener('message', pushSnapshot, false);

  const thrNewSnapshot = throttle((twoObj) => {
    if (!twoObj.oldVal) {
      const fakeAnswer = {data: {was: null, became: twoObj.newVal}};
      pushSnapshot(fakeAnswer)
    } else wWorker.postMessage(twoObj);
  }, 1000);

  store.watch(
    (state, getters) => state.mod_workspace.workspaceContent.length,
    (newVal, oldVal) => {
      store.dispatch('mod_workspace-history/UPDATE_networkList')
    }
  );
  store.watch(
    (state, getters) => getters['mod_workspace/GET_currentNetwork'],
    (newVal, oldVal) => {
      thrNewSnapshot({'newVal': var1, 'oldVal': var2});
    },
    {deep: true}
  );
};

export default wsHistory
