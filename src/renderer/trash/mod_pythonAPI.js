import {PythonShell} from 'python-shell';
import Vue from 'vue'


PythonShell.defaultOptions = {
  scriptPath: 'core_local'
};

const namespaced = true

const state = {
  symPY: 0
}

const mutations = {
  SET_symPY(state, value) {
    state.symPY = value
  }
}

const actions = {
  PY_console(context) {
    if(Vue.config.versionApp === 'core_local') {
      let opt = {args: ['hello', 'py']};
      PythonShell.run('test.py', opt, function (err, results) {
        if (err) throw err;
        alert('results:', results);
      });
    }

    else {
      alert('cloud version');
    }
  },
  PY_text({commit}, num) {
    let pyshell = new PythonShell('text.py');
    pyshell.send('hello type');

    pyshell.on('message', function (message) {
      console.log('message: ' + message);
    });

    pyshell.end(function (err, code, signal) {
      if (err) throw err;
    });

    //commit('SET_symPY', s)
  },
  PY_summ({commit}, num) {
    let pyshell = new PythonShell('summ.py', { mode: 'json' });

    pyshell.send({x: num.x, y: num.y});
    pyshell.on('message', function (data) {
      console.log(data)
      commit('SET_symPY', data)
    });

    pyshell.end(function (err, code, signal) {
      if (err) throw err;
      // console.log('The exit code was: ' + code);
      // console.log('The exit signal was: ' + signal);
      console.log('finished');
    });

  },
  PY_func({commit}, num) {
    let pyshell = new PythonShell('function.py', { mode: 'json' });

    let option = {
      funcName: 'add',
      value: {
        x: num.x,
        y: num.y,
      },
    }

    pyshell.send(option);

    pyshell.on('message', (data)=> {
      //console.log(data)
      commit('SET_symPY', data)
    });

    pyshell.end(function (err, code, signal) {
      if (err) throw err;
      //console.log('finished');
    });
  }
}

export default {
  namespaced,
  state,
  mutations,
  actions
}




function  createArrowList() {
  let size = 72;
  let listID = {};
  let connectList = [];
  let net = this.workspace.network;
  findAllID();

  net.forEach((itemEl, indexEl, arrNet)=> {
    if(itemEl.layerNext.length > 0) {
      itemEl.layerNext.forEach((itemCh, indexCh, arrCh)=> {
        //let indexNextCh = findIndexId(arrNet, itemCh);
        let newArrow = {
          l1: itemEl,
          l2: listID[itemCh],
          correctPosition: {
            x1: 0,
            y1: 0,
            x2: 0,
            y2: 0
          }
        };

        calcSideArrow(newArrow, itemEl, listID[itemCh]);
        //console.log(newArrow, "<NEW ARROW");
        Object.defineProperty(newArrow, 'positionArrow', {
          get() {
            return {
              x1: this.l1.meta.left + this.correctPosition.x1,
              y1: this.l1.meta.top + this.correctPosition.y1,
              x2: this.l2.meta.left + this.correctPosition.x2,
              y2: this.l2.meta.top + this.correctPosition.y2,
            }
          },
          enumerable: true,
          configurable: false
        });
        connectList.push(newArrow);
      });
    }
  });

  calcCorrectPosition(connectList);
  //console.log(connectList);

  function calcCorrectPosition(arrList) {
    arrList.forEach((itemArr, indexArr, listArr)=> {
      if(itemArr.l1.calcAnchor.bottom && itemArr.l2.calcAnchor.top) {
        itemArr.correctPosition.x1 = size - itemArr.l1.calcAnchor.bn * (size/(itemArr.l1.calcAnchor.bottom + 1));
        itemArr.correctPosition.x2 = size - itemArr.l2.calcAnchor.tn * (size/(itemArr.l2.calcAnchor.top + 1));
        itemArr.correctPosition.y1 = size;
        itemArr.correctPosition.y2 = 0;

        itemArr.l1.calcAnchor.bn = ++itemArr.l1.calcAnchor.bn;
        itemArr.l2.calcAnchor.tn = ++itemArr.l2.calcAnchor.tn;
      }
      if(itemArr.l1.calcAnchor.top && itemArr.l2.calcAnchor.bottom) {
        itemArr.correctPosition.x1 = size - itemArr.l1.calcAnchor.tn * (size/(itemArr.l1.calcAnchor.top + 1));
        itemArr.correctPosition.x2 = size - itemArr.l2.calcAnchor.bn * (size/(itemArr.l2.calcAnchor.bottom + 1));
        itemArr.correctPosition.y1 = 0;
        itemArr.correctPosition.y2 = size;

        itemArr.l1.calcAnchor.tn = ++itemArr.l1.calcAnchor.tn;
        itemArr.l2.calcAnchor.bn = ++itemArr.l2.calcAnchor.bn;
      }
      if(itemArr.l1.calcAnchor.right && itemArr.l2.calcAnchor.left) {
        itemArr.correctPosition.x1 = size;
        itemArr.correctPosition.x2 = 0;
        itemArr.correctPosition.y1 = size - itemArr.l1.calcAnchor.rn * (size/(itemArr.l1.calcAnchor.right + 1));
        itemArr.correctPosition.y2 = size - itemArr.l2.calcAnchor.ln * (size/(itemArr.l2.calcAnchor.left + 1));

        itemArr.l1.calcAnchor.rn = ++itemArr.l1.calcAnchor.rn;
        itemArr.l2.calcAnchor.ln = ++itemArr.l2.calcAnchor.ln;
      }
      if(itemArr.l1.calcAnchor.left && itemArr.l2.calcAnchor.right) {
        itemArr.correctPosition.x1 = 0;
        itemArr.correctPosition.x2 = size;
        itemArr.correctPosition.y1 = size - itemArr.l1.calcAnchor.ln * (size/(itemArr.l1.calcAnchor.left + 1));
        itemArr.correctPosition.y2 = size - itemArr.l2.calcAnchor.rn * (size/(itemArr.l2.calcAnchor.right + 1));

        itemArr.l1.calcAnchor.ln = ++itemArr.l1.calcAnchor.ln;
        itemArr.l2.calcAnchor.rn = ++itemArr.l2.calcAnchor.rn;
      }
    });
  }

  function calcSideArrow(arrow, startEl, stopEl) {

    const sideL1Right = arrow.l1.meta.left < arrow.l2.meta.left;
    const sideL1Bottom = arrow.l1.meta.top < arrow.l2.meta.top;

    const offsetX = Math.abs(arrow.l1.meta.left - arrow.l2.meta.left);
    const offsetY = Math.abs(arrow.l1.meta.top - arrow.l2.meta.top);

    if(sideL1Right && offsetX > offsetY) {
      startEl.calcAnchor.right = ++startEl.calcAnchor.right;
      stopEl.calcAnchor.left = ++stopEl.calcAnchor.left
    }
    if(!sideL1Right && offsetX > offsetY) {
      startEl.calcAnchor.left = ++startEl.calcAnchor.left;
      stopEl.calcAnchor.right = ++stopEl.calcAnchor.right;
    }
    if(sideL1Bottom && offsetX < offsetY) {
      startEl.calcAnchor.bottom = ++startEl.calcAnchor.bottom;
      stopEl.calcAnchor.top = ++stopEl.calcAnchor.top
    }
    if(!sideL1Bottom && offsetX < offsetY) {
      startEl.calcAnchor.top = ++startEl.calcAnchor.top;
      stopEl.calcAnchor.bottom = ++stopEl.calcAnchor.bottom
    }
  }

  function findAllID() {
    net.forEach((itemEl, indexEl, arrNet)=> {
      let itemID = itemEl.layerId;
      itemEl.calcAnchor = { top: 0, right: 0, bottom: 0, left: 0, tn: 1, rn: 1, bn: 1, ln: 1 };
      listID[itemID] = itemEl;
    });
  }
  function lengthLine(l1, l2) {
    return Math.round(Math.abs(Math.sqrt(Math.pow((l2.x-l1.x), 2) + Math.pow((l2.y - l1.y), 2))));
  }
  function findMinLength(l1, l2) {

    let position = '';

    (l1.meta.top < l2.meta.top) ? position = position + 't' : position = position + 'b';
    (l1.meta.left < l2.meta.left) ? position = position + 'r' : position = position + 'l';


    const offsetX = Math.abs(arrow.l1.meta.left - arrow.l2.meta.left);
    const offsetY = Math.abs(arrow.l1.meta.top - arrow.l2.meta.top);

    function topDot(dot) {
      return {
        x: dot.x + (size / 2),
        y: dot.y
      }
    }
    function rightDot(dot) {
      return {
        x: dot.x + size,
        y: dot.y + (size / 2)
      }
    }
    function bottomDot(dot) {
      return {
        x: dot.x + (size / 2),
        y: dot.y + size
      }
    }
    function leftDot(dot) {
      return {
        x: dot.x,
        y: dot.y + (size / 2)
      }
    }

    switch(position) {
      case 'tr':
        let top = topDot(l1);
        let right = rightDot(l1);
        let bottom = bottomDot(l2);
        let left = leftDot(l2);
        calcMinLength(top, right, bottom, left);


      //   break
      // case 'tl':
      //   break
      // case 'br':
      //   break
      // case 'bl':
      //   break
    }
  }

  function calcMinLength(d1, d2, d3, d4) {
    let d1d3 = lengthLine(d1, d3);
    let d1d4 = lengthLine(d1, d4);
    let d2d3 = lengthLine(d2, d3);
    let d2d4 = lengthLine(d2, d4);

    const arrows = [
      {
        length: lengthLine(d1, d3),
        start: d1,
        end: d3,
      },
      {
        length: lengthLine(d1, d4),
        start: d1,
        end: d4,
      },
      {
        length: lengthLine(d2, d3),
        start: d2,
        end: d3,
      },
      {
        length: lengthLine(d2, d4),
        start: d2,
        end: d4,
      }
    ]

    // let lineArr = [d1d3, d1d4, d2d3, d2d4].sort();
    // let minLine = lineArr[0];
    const minLen = arrows.sort( (a, b) => a.length - b.length )[0];
    return minLen;
  }
  //console.log(listID);
  this.arrowsList = connectList;
  //this.calcArrowsPosition()
},
