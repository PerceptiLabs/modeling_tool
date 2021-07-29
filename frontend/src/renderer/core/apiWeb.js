import store from '@/store'
import { stringifyNetworkObjects } from '@/core/helpers';
import { whenUrlIsResolved } from '@/core/urlResolver';
import { KERNEL_BASE_URL } from '@/core/constants'
import { KERNEL_URL_CONFIG_PATH }   from "@/core/constants";
import { KERNEL_VERSION_CONFIG_PATH }   from "@/core/constants";
import { whenVersionIsResolved } from '@/core/versionResolver';
import { renderingKernel }  from "@/core/apiRenderingKernel.js";


function calcTime(stop, start, name, nameComp) {
  let time = stop - start;
  console.log(`${name}`, `${nameComp}` , `${time}ms`);
}

const kernelUrlPromise = Promise.all([whenUrlIsResolved(KERNEL_URL_CONFIG_PATH, KERNEL_BASE_URL), whenVersionIsResolved(KERNEL_VERSION_CONFIG_PATH)]).then(([kernel_url]) => {
  return kernel_url;
})

function coreRequest(data, path, no, name) {
    data.instanceId = store.state.mod_api.instanceId
    // var timeStartAnswer = 0;
    // var timeStartSend = 0;
    // var timeStopSend = 0;
    // var timeOpenWs = 0;
    //
    // timeStartSend = new Date();

  // console.log('process.env', process.env);
  const initialSentData = data;

  const action = data.action;  
  const receiver = data.receiver;
  const userEmail = store.getters['mod_user/GET_userEmail'];
    
  return renderingKernel.sessionProxy(action, receiver, userEmail, data)
    .then(obgData => {
      const modelId = initialSentData.receiver === null || initialSentData.receiver === undefined ? store.getters['mod_workspace/GET_currentNetworkId'] : parseInt(initialSentData.receiver);

      if(obgData.errorMessage && obgData.errorMessage.length) {

        if(initialSentData.action === "updateResults") {
          let errorMessage = obgData.errorMessage[0];
          // let startPosition =  errorMessage.indexOf(' This will be reported as a bug.');
          // if(startPosition !== -1) {
          //   errorMessage = errorMessage.substring(0, startPosition)
          // }
          store.dispatch('mod_workspace/set_NetworkCoreErrorAction', {errorMessage, modelId});
        }
	
        store.dispatch('globalView/GP_errorPopup', obgData.errorMessage);
        store.dispatch('mod_tracker/EVENT_coreError', obgData.errorMessage);
        store.dispatch('mod_workspace/setViewType', 'model');
        store.commit('mod_workspace/update_network_meta', 
                     {key: 'coreStatus', 
                      networkID: modelId,
                      value: {Status: 'Waiting'}
                     });
        store.dispatch('mod_workspace/EVENT_startDoRequest', false);
        store.dispatch('mod_workspace/SET_openStatistics', null);
        store.dispatch('mod_workspace/SET_openTest', null);
        store.commit('mod_workspace/SET_showStartTrainingSpinner', false);
      }
      
      if(obgData.warningMessage && obgData.warningMessage.length) {
        for(const wm of obgData.warningMessage) {
          store.dispatch('mod_workspace-notifications/addError', {
            networkId: modelId,
            errorObject: ({
              Message: wm,
            }),
            addToast: true
          });
        }
      }
      
      if(obgData.generalLogs && obgData.generalLogs.length) {
        for(const wm of obgData.generalLogs) {
          store.dispatch('mod_workspace-notifications/addWarning', {
            networkId: modelId,
            warningObject: ({
              Message: wm,
            }),
            addToast: true
          });
        }
      }
      
      if (obgData.consoleLogs) {
        store.dispatch('mod_logs/addLogsForNetwork', {
          networkId: modelId,
          logs: obgData.consoleLogs
        });
      }
      //console.log('answer core data ', obgData);
      // let stopRequest = new Date();
      // calcTime(stopRequest, timeStartAnswer, 'transmitting', name);

      /*
      if(process.env.NODE_ENV !== 'production') {
        console.log('REQ:' + initialSentData.action, 
                    JSON.parse(JSON.stringify(initialSentData)),
                    JSON.parse(JSON.stringify(obgData.content)),
                   );
      }
      */
      return obgData.content
    });

}
const openWS = null;
const closeWS = null;


export {coreRequest, openWS, closeWS};
