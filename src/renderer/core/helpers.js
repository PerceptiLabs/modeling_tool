import {remote} from "electron";

const findIndexId = function (arr, ID) {
  return arr.findIndex(function(item) {return item.layerId == ID});
};

const clickOutside = function (event) {
  //console.log('clickOutside');
  if (event.target.closest('.clickout') !== this.currentNode) {
    document.removeEventListener('click', this.clickOutside);
    this.clickOutsideAction();
  }
};

const trainingElements =  ['TrainNormal', 'TrainNormalData', 'TrainReinforce', 'TrainGenetic', 'TrainDynamic'];
//const trainingElements =  ['TrainNormal'];
const deepLearnElements = ['DeepLearningFC', 'DeepLearningConv', 'DeepLearningDeconv', 'DeepLearningRecurrent'];

const openLoadDialog = function (callback, options) {
  let dialog = remote.dialog;
  dialog.showOpenDialog(options, (files)=>{
    if(files !== undefined) {
      callback(files)
    }
  })
};


export {findIndexId, clickOutside, trainingElements, deepLearnElements, openLoadDialog}






//------------триугольники
//polygon(class="svg-arrow_triangle" :points="arrow.t1.x+','+arrow.t1.y+' '+arrow.t2.x+','+arrow.t2.y+' '+arrow.t3.x+','+arrow.t3.y")
// arrowsList() {
//   let connectList = [];
//   this.workspace.network.forEach((itemEl, indexEl, arrNet)=> {
//
//     if(itemEl.layerNext.length > 0) {
//       itemEl.layerNext.forEach((itemCh, indexCh, arrCh)=> {
//         let indexNextCh = findIndexId(arrNet, itemCh);
//         let newArrow = {
//           l1: {
//             y: itemEl.meta.top + 35,
//             x: itemEl.meta.left + 35
//           },
//           l2: {
//             y: arrNet[indexNextCh].meta.top + 35,
//             x: arrNet[indexNextCh].meta.left + 35
//           }
//         };
//         connectList.push(newArrow);
//       });
//     }
//   });
//
//   function findIndexId (arr, ID) {
//     return arr.findIndex(function(item) {return item.layerId == ID});
//   }
//   //console.log(connectList)
//   return connectList
// }
// calcArrow(dot1, dot2) {
//   let triangleSize = 8;
//   let radians = Math.atan2((dot2.y - dot1.y), (dot2.x - dot1.x))
//   let l1 = {x: dot1.x + 35, y: dot1.y + 35};
//   let l2 = {x: dot2.x + 35, y: dot2.y + 35};
//   //let lengthArrow = Math.round(Math.abs(Math.sqrt(Math.pow((l2.x-l1.x), 2) + Math.pow((l2.y - l1.y), 2))));
//   //console.log(lengthArrow)
//
//   let t1start = {x: l2.x - triangleSize, y: l2.y - triangleSize/2};
//   let t2start = {x: l2.x - triangleSize, y: l2.y + triangleSize/2};
//   let t3start = {x: l2.x, y: l2.y};
//
//   let t1 = turnСoordinate(t1start, l2, radians);
//   let t2 = turnСoordinate(t2start, l2, radians);
//   let t3 = turnСoordinate(t3start, l2, radians);
//
//   // let t1 = correctTriangle(t1x, radians);
//   // let t2 = correctTriangle(t2x, radians);
//   // let t3 = correctTriangle(t3x, radians);
//
//   //l1 = correctLine(l1, radians);
//   //l2 = correctLine(l2, radians);
//
//   function turnСoordinate(dot, dotZero, rad) {
//     let relX = dot.x - dotZero.x;
//     let relY = dot.y - dotZero.y;
//     let newX = (relX*Math.cos(rad) - relY*Math.sin(rad)) + dotZero.x;
//     let newY = (relX*Math.sin(rad) + relY*Math.cos(rad)) + dotZero.y;
//     let newDot = {
//       x: roundNum(newX),
//       y: roundNum(newY),
//     };
//     return newDot
//   }
//   function correctLine(finishDot, rad) {
//     return {
//       x: roundNum(finishDot.x - Math.cos(rad) * triangleSize/2),
//       y: roundNum(finishDot.y - Math.sin(rad) * triangleSize/2),
//     }
//   }
//   function correctTriangle(rt, rad) {
//     return {
//       x: roundNum(rt.x - Math.cos(rad) * triangleSize/3),
//       y: roundNum(rt.y - Math.sin(rad) * triangleSize/3),
//     }
//   }
//   function roundNum (num) {
//     let accur = 100;
//     return Math.round(num * accur) / accur;
//   }
//
//   return {l1, l2, t1, t2, t3};
//
// },
