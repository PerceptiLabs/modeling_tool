const net = require('net');


/*GENERAL CORE*/
const coreRequest = function (message, port, address) {
  let socket = new net.Socket();
  let socketAddress = address || '127.0.0.1';
  let socketPort = port || 5000;

  init();

  function init() {
    socket.connect(socketPort, socketAddress, ()=> {
      const header = {
        "byteorder": 'little',
        "content-type": 'text/json',
        "content-encoding": 'utf-8',
        "content-length": 0,
      };
      return new Promise((resolve, reject) => {
        let dataJSON = JSON.stringify(message);
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

        const messageBuff = Buffer.from(messageByte);

        socket.write(messageBuff);
        let dataLength = '';
        let dataPart = '';
        socket.on('data', (data) => {
          const dataString = data.toString();
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
          if(dataPart.length === dataLength + 1) {
            let obgData = JSON.parse(dataPart.slice(0, -1));
            //console.log('then', obgData);
            resolve(obgData);
          }

          if (data.toString().endsWith('exit')) {
            socket.destroy();
          }
        });

        socket.on('error', (err) => {
          reject('error core api', err);
        });

      });
    });

    socket.on('close', () => {
      console.log('Client closed');
    });
  }
};

export default coreRequest;
