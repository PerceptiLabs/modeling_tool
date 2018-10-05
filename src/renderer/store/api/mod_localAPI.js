
const net = require('net');
// run server core

var exec = require('child_process').execFile;
var runServer = function () {
  exec('core_local/ServerForJS.exe', function (err, data) { });
};
runServer();

const namespacedLocal = true;

const stateLocal = {
  symPY: 'Local API'
};

const mutationsLocal = {
  SET_symPY(state, value) {
    state.symPY = value
  }
};

const actionsLocal = {
  PY_func({commit}, num) {
    let a = num.x;
    let b = num.y;
    let socketClient = net.connect({host:'127.0.0.1', port:5000}, () => {
      //console.log('connected to server!');
      socketClient.write(`<?xml version="1.0" encoding="utf-16"?><JsServerRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><CommandName>Add</CommandName><ParamA>${a}</ParamA><ParamB>${b}</ParamB></JsServerRequest>`);
    });

    socketClient.on('end', () => {
      //console.log('disconnected from server');
    });

    socketClient.on('data', (data) => {
      let response = data.toString();
      let startDel = response.indexOf('<Result>') + 8;
      let stopDel = response.indexOf('</Result>');
      let result = response.slice(startDel, stopDel);
      commit('SET_symPY', result)
    });
  }
};

export { namespacedLocal, stateLocal, mutationsLocal, actionsLocal }
