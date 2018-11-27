// const requestApi = function (request) {
//   const net = require('net');
//   let answerSerwer;
//   const header = {
//     "byteorder": 'little',
//     "content-type": 'text/json',
//     "content-encoding": 'utf-8',
//     "content-length": 0,
//   };
//
//   let socketClient = net.connect({host:'127.0.0.1', port:5000}, () => {
//
//     let dataJSON = JSON.stringify(request);
//     let dataByte = (new TextEncoder('utf-8').encode(dataJSON));
//     let dataByteLength = dataByte.length;
//
//     header["content-length"] = dataByteLength;
//
//     let headerJSON = JSON.stringify(header);
//     let headerByte = (new TextEncoder('utf-8').encode(headerJSON));
//     let headerByteLength = headerByte.length;
//
//     let firstByte = 0;
//     let secondByte = headerByteLength;
//
//     if(headerByteLength > 256) {
//       firstByte = Math.floor(headerByteLength / 256);
//       secondByte = headerByteLength % 256;
//     }
//     //console.log(dataJSON);
//     const message = [
//       firstByte, secondByte,
//       ...headerByte,
//       ...dataByte
//     ];
//
//     const buf6 = Buffer.from(message);
//     socketClient.write(buf6);
//   });
//
//   socketClient.on('end', ()=>{});
//
//   socketClient.on('data', (data) => {
//     let dataString = data.toString();
//     let clearData = dataString.slice(dataString.indexOf('}{"result": ') + 12, dataString.length-1);
//     socketClient.end();
//     //answerSerwer = clearData;
//     //console.log(clearData);
//   });
//   socketClient.on('error', (err) => {
//     console.log('answer error server', err.toString());
//     socketClient.end();
//   });
//   return answerSerwer
// };
//
// export default requestApi
//


'use strict';

const net = require('net');

class Client {
  constructor(port, address) {
    this.socket = new net.Socket();
    this.address = address || '127.0.0.1';
    this.port = port || 5000;
    this.init();
  }

  init() {
    var client = this;
    client.socket.connect(client.port, client.address, () => {
      //console.log(`Client connected to: ${client.address} :  ${client.port}`);
    });

    client.socket.on('close', () => {
      //console.log('Client closed');
    });
  }

  sendMessage(message) {
    var client = this;
    const header = {
      "byteorder": 'little',
      "content-type": 'text/json',
      "content-encoding": 'utf-8',
      "content-length": 0,
    };
    return new Promise((resolve, reject) => {

      let dataJSON = JSON.stringify(message);
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
      //console.log(dataJSON);
      const messageByte = [
        firstByte, secondByte,
        ...headerByte,
        ...dataByte
      ];

      const messageBuff = Buffer.from(messageByte);

      client.socket.write(messageBuff);

      client.socket.on('data', (data) => {
        let dataString = data.toString();
        let clearData = dataString.slice(dataString.indexOf('}{"result": ') + 12, dataString.length-1);
        resolve(clearData);
        if (data.toString().endsWith('exit')) {
          client.socket.destroy();
        }
      });

      client.socket.on('error', (err) => {
        reject(err);
      });

    });
  }
}
export default Client;
// module.exports = Client;
