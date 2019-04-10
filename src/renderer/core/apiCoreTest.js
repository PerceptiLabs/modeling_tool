const net = require('net');

/*GENERAL CORE*/
const coreRequest = function (message, port, address, name) {
  let coreConnectTime = new Date();
  return new Promise((resolve, reject) => {
    let socket = new net.Socket();
    let socketAddress = address || '127.0.0.1';
    let socketPort = port || 5000;

    socket.connect(socketPort, socketAddress, ()=> {
      let startRequestTime = new Date();
      const messageBuff = prepareCoreMessage(message);

      socket.write(messageBuff);

      let dataLength = '';
      let dataPart = '';

      socket.on('data', (data) => {
        let startAnswTime = new Date();

        const dataString = data.toString();
        //console.log(dataString);
        if (dataLength) dataPart = dataPart + dataString;
        if (!dataLength) {
          dataLength = +dataString.slice(dataString.indexOf('length') + 9, dataString.indexOf(','));
          dataPart = dataString.slice(dataString.indexOf('body') + 7 , dataString.length);
        }
        if(dataPart.length === dataLength + 1) {
          let obgData = JSON.parse(dataPart.slice(0, -1));


          let stopAnswTime = new Date();
          //let coreConnect = startRequestTime - coreConnectTime;
          let coreDelay = startAnswTime - startRequestTime;
          let answerDelay = stopAnswTime - startAnswTime;
          //console.log(`core connect ${name}`, `${coreConnect}ms`);
          console.log(`core delay ${name}`, `${coreDelay}ms`);
          console.log(`transmit delay ${name}`, `${answerDelay}ms`);
          resolve(obgData);
          console.log(obgData);
        }
        if (data.toString().endsWith('exit')) socket.destroy();
      });
    });
    socket.on('error', (err) => {
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
