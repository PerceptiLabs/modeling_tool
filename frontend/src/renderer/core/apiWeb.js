// const wsPathDef = 'ws://perceptilabs-core-robertproject.apps.cluster-rdu-3950.rdu-3950.example.opentlc.com ';
const wsPathDef = ("ws://" + window.location.host).replace('perceptilabs-frontend', 'perceptilabs-core') + ":5000";
// const wsPathDef = 'ws://perceptilabs-core:5000';
// const wsPathDef = 'ws://localhost:5000';
// const wsPathDef = "ws://" + window.location.host + ":443";


var webSocket = null;
import store from '@/store'

function calcTime(stop, start, name, nameComp) {
  let time = stop - start;
  console.log(`${name}`, `${nameComp}` , `${time}ms`);
}

function coreRequest(data, path, no, name) {
    // var timeStartAnswer = 0;
    // var timeStartSend = 0;
    // var timeStopSend = 0;
    // var timeOpenWs = 0;
    //
    // timeStartSend = new Date();

  return new Promise((resolve, reject) => {
    let wsPath = path || wsPathDef;
    //console.log('path ', wsPath);

    let websocket = new WebSocket(wsPath);

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

      const header = {
        "byteorder": 'little',
        "content-type": 'text/json',
        "content-encoding": 'utf-8',
        "content-length": 0,
      };
      let dataJSON = JSON.stringify(message);
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
          //console.log(stringData);
          let obgData = JSON.parse(stringData);
          if(obgData.errorMessage && obgData.errorMessage.length) {
            store.dispatch('globalView/GP_errorPopup', obgData.errorMessage);
            store.dispatch('mod_tracker/EVENT_coreError', obgData.errorMessage);
            store.dispatch('mod_workspace/EVENT_startDoRequest', false);
            store.dispatch('mod_workspace/SET_openStatistics', null);
            store.dispatch('mod_workspace/SET_openTest', null);
            store.commit('mod_workspace/SET_showStartTrainingSpinner', false);
          }

          //console.log('answer core data ', obgData);
          // let stopRequest = new Date();
          // calcTime(stopRequest, timeStartAnswer, 'transmitting', name);
          resolve(obgData.content);
        }
        //websocket.close();
      }
    }
  });
}
const openWS = null;
const closeWS = null;


export {coreRequest, openWS, closeWS};
