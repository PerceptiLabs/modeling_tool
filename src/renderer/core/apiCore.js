const net = require('net');
import store from '@/store'
/*GENERAL CORE*/
const coreRequest = function (message, port, address) {
  return new Promise((resolve, reject) => {
    let socket = new net.Socket();
    let socketAddress = address || '127.0.0.1';
    let socketPort = port || 5000;

    socket.connect(socketPort, socketAddress, ()=> {

      const messageBuff = prepareCoreMessage(message);

      //store.dispatch('globalView/ADD_requestCounter');
      socket.write(messageBuff);

      let dataLength = '';
      let dataPart = '';

      socket.on('data', (data) => {
        const dataString = data.toString();
        //console.log(dataString);
        if (dataLength) dataPart = dataPart + dataString;
        if (!dataLength) {
          dataLength = +dataString.slice(dataString.indexOf('length') + 9, dataString.indexOf(','));
          dataPart = dataString.slice(dataString.indexOf('body') + 7 , dataString.length);
        }
        if(dataPart.length === dataLength + 1) {
          let obgData = JSON.parse(dataPart.slice(0, -1));
          //store.dispatch('globalView/REM_requestCounter');
          //console.log('then', obgData);
          resolve(obgData);
        }
        if (data.toString().endsWith('exit')) {
          //store.dispatch('globalView/REM_requestCounter');
          socket.destroy();
        }
      });
    });
    socket.on('error', (err) => {
      //store.dispatch('globalView/CLEAR_requestCounter');
      reject('error core api', err);
    });
    socket.on('close', () => {
      //console.log('Client closed');
    });
  });

  function prepareCoreMessage(dataSend) {
    const header = {
      "byteorder": 'little',
      "content-type": 'text/json',
      "content-encoding": 'utf-8',
      "content-length": 0,
    };
    let dataJSON = JSON.stringify(dataSend);
    //console.log(dataJSON);
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

    return Buffer.from(messageByte);
  }
};

export default coreRequest;
