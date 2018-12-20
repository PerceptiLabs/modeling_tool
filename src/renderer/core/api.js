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
        if (dataLength) {
          dataPart = dataPart + dataString;
        }
        if (!dataLength) {
          dataLength = +dataString.slice(dataString.indexOf('content-length') + 16, dataString.indexOf('}{'));
          dataPart = dataString.slice(dataString.indexOf('}{') + 1 , dataString.length);
        }
        if(dataPart.length === dataLength) {
          let obgData = JSON.parse(dataPart);
          resolve(obgData);
        }

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
