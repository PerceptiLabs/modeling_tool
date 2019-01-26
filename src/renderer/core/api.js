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
    //console.log(message);
    var client = this;
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

      client.socket.write(messageBuff);
      let dataLength = '';
      let dataPart = '';
      client.socket.on('data', (data) => {
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
          client.socket.destroy();
        }
      });

      client.socket.on('error', (err) => {
        reject('error core api', err);
      });

    });
  }
}
export default Client;
