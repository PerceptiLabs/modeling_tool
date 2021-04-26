import store from '@/store'
import { stringifyNetworkObjects } from '@/core/helpers';
import { whenUrlIsResolved } from '@/core/urlResolver';
import { KERNEL_BASE_URL } from '@/core/constants'
import { KERNEL_URL_CONFIG_PATH }   from "@/core/constants";


function calcTime(stop, start, name, nameComp) {
  let time = stop - start;
  console.log(`${name}`, `${nameComp}` , `${time}ms`);
}

const kernelUrlPromise = whenUrlIsResolved(KERNEL_URL_CONFIG_PATH, KERNEL_BASE_URL)

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
  return kernelUrlPromise
    .then(kernel_url => {
      return new Promise((resolve, reject) => {
        // let wsPath = path || wsPathDef;
        let wsPath = path || kernel_url;
        //console.log('path ', wsPath);

        let websocket = new WebSocket(wsPath);
        // used a factory to return a singleton
        // let websocket = webSocketClientFactory.getInstance(wsPath);

        websocket.onopen =    (evt)=> {
          // timeOpenWs = new Date();
          // calcTime(timeOpenWs, timeStartSend, 'creating WS', name);
          sendData(data)
        };
        websocket.onclose =   (evt)=> {
          //console.log("DISCONNECTED");
        };
        websocket.onmessage = (message)=> {
          //console.log('RESPONSE ', message.data);
          //websocket.close();
          onMessage(message)
        };
        websocket.onerror =   (evt)=> {
          reject(evt);
          websocket.close();
        };

        function sendData(message) {
          //console.log('sent to core ', message);

          // temporarly send like dict specific action.
          const sendActionLikeObject = ['test']
          if(sendActionLikeObject.some(val => val === message.action)) {
            websocket.send(message);
            return;
          }

          const header = {
            "byteorder": 'little',
            "content-type": 'text/json',
            "content-encoding": 'utf-8',
            "content-length": 0,
          };
          let dataJSON = stringifyNetworkObjects(message);
          //console.log('input data ', dataJSON);
          let dataByte = (new TextEncoder('utf-8').encode(dataJSON));
          let dataByteLength = dataByte.length;

          header["content-length"] = dataByteLength;

          let headerJSON = JSON.stringify(header);
          let headerByte = (new TextEncoder('utf-8').encode(headerJSON));
          let headerByteLength = headerByte.length;

          let firstByte = 0;
          let secondByte = headerByteLength;

          if(headerByteLength > 256) {
            firstByte = Math.floor(headerByteLength / 256);
            secondByte = headerByteLength % 256;
          }
          const messageByte = [
            firstByte, secondByte,
            ...headerByte,
            ...dataByte
          ];
          const messageBuff = Buffer.from(messageByte);
          websocket.send(messageBuff);

          // timeStopSend = new Date();
          // calcTime(timeStopSend, timeOpenWs, 'creating send message', name);
          // calcTime(timeStopSend, timeStartSend, 'req->send', name);
        }

        function onMessage(data) {
          //console.log('answer WS data', data);
          // timeStartAnswer = new Date();
          // calcTime(timeStartAnswer, timeStopSend, 'core delay', name);

          let dataLength = '';
          let dataPart = '';
          //let dataString = data.toString();
          let dataString = data.data;
          //console.log(dataString);
          if (dataLength) {
            dataPart = dataPart + dataString;
          }
          if (!dataLength) {
            // console.log(dataString.indexOf('length'));
            // console.log(dataString.length);
            dataLength = +dataString.slice(dataString.indexOf('length') + 9, dataString.indexOf(','));
            dataPart = dataString.slice(dataString.indexOf('body') + 7 , dataString.length);
            // console.log('dataLength: ', dataLength);
            // console.log('dataPart: ', dataPart);
          }
          //console.log(dataPart.length, dataLength + 1);
          if(dataPart.length === dataLength + 1) {
            let stringData = dataPart.slice(0, -1);
            //console.log('stringData ', stringData);
            if(stringData == 'None') {
              //console.log('None');
              reject(dataPart);
            }
            else {
              // console.log(stringData);
              let obgData = JSON.parse(stringData);
              if(obgData.errorMessage && obgData.errorMessage.length) {

                if(initialSentData.action === "updateResults") {
                  const modelId = parseInt(initialSentData.receiver);
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
                           networkID: store.getters['mod_workspace/GET_currentNetwork'].networkID,
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
                    networkId: store.getters['mod_workspace/GET_currentNetworkId'],
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
                    networkId: store.getters['mod_workspace/GET_currentNetworkId'],
                    warningObject: ({
                      Message: wm,
                    }),
                    addToast: true
                  });
                }
              }

              if (obgData.consoleLogs) {
                store.dispatch('mod_logs/addLogsForNetwork', {
                  networkId: store.getters['mod_workspace/GET_currentNetworkId'],
                  logs: obgData.consoleLogs
                });
              }
              //console.log('answer core data ', obgData);
              // let stopRequest = new Date();
              // calcTime(stopRequest, timeStartAnswer, 'transmitting', name);
              if(initialSentData.action !== 'checkCore' && process.env.NODE_ENV !== 'production')
              console.log('REQ:' + initialSentData.action, 
                 JSON.parse(JSON.stringify(initialSentData)),
                JSON.parse(JSON.stringify(obgData.content)),
              );
              
              /* TOREMOVE
              delete obgData['consoleLogs']

              if (obgData.content) {
                delete obgData.content['consoleLogs']
              }
              */
              resolve(obgData.content);
            }
            //websocket.close();
          }
        }
      });
    });
}
const openWS = null;
const closeWS = null;


export {coreRequest, openWS, closeWS};
