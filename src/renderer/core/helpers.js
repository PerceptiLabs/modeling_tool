import {remote} from "electron";
import fs from 'fs';
//import util from 'util';

//const readFilePromise = util.promisify(fs.readFile);



const findIndexId = function (arr, ID) {
  return arr.findIndex(function(item) {return item.layerId == ID});
};


const openLoadDialog = function (callback, options) {
  let dialog = remote.dialog;
  dialog.showOpenDialog(options, (files)=>{
    if(files !== undefined) {
      callback(files)
    }
  })
};


// const readFilePromiseNative = function (path) {
//   return new Promise((success, reject) => {
//     fs.readFile(path, (err, data) => {
//       if (err) {
//         return reject();
//       }
//       return success(data);
//     })
//   });
// };
const loadNetwork = function (pathArr) {
  console.log(pathArr);
  return readFilePromiseNative(pathArr[0]).then(
    (data) => {
      let net = JSON.parse(data.toString());
      this.$store.dispatch('mod_workspace/ADD_network', net.network);
      if(this.$router.history.current.name !== 'app') {
        this.$router.replace({name: 'app'});
      }
    }
  );
  function readFilePromiseNative(path) {
    return new Promise((success, reject) => {
      fs.readFile(path, (err, data) => {
        if (err) {
          console.log(err);
          return reject();
        }
        return success(data);
      })
    });
  };
};

const generateID = function(input) {
  let out;
  let stringID = input.toString();
  let dotIndex = stringID.indexOf('.');
  dotIndex > 0 ? out = stringID.slice(0, dotIndex) + stringID.slice(dotIndex + 1) :  out = stringID;
  out = +out;
  return out
};

export {findIndexId, openLoadDialog, loadNetwork, generateID}