import {PythonShell} from 'python-shell';
//let pyshell = new PythonShell('../../../test.py', {mode: 'json'});

// const pythonFolder = 'engine'
//
// PythonShell.options = {
//   scriptPath: pythonFolder
// };

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
    // PythonShell.runString('x=1+1;print(x)', null, function (err) {
    //   if (err) throw err;
    //   console.log('finished');
    // });
    // pyshell.send({x: 2, y: 3});
    //
    // pyshell.on('message', function (message) {
    //   // received a message sent from the Python script (a simple "print" statement)
    //   console.log(message);
    // });
    let opt = {args: ['hello', 'py']};
    PythonShell.run('test.py', opt, function (err, results) {
      if (err) throw err;
      // results is an array consisting of messages collected during execution
      alert('results:', results);
    });
  },
  PY_text({commit}, num) {
    let pyshell = new PythonShell('engine/text.py');
    pyshell.send('hello type');

    pyshell.on('message', function (message) {
      console.log('message: ' + message);
    });

    pyshell.end(function (err, code, signal) {
      if (err) throw err;
      console.log('The exit code was: ' + code);
      console.log('The exit signal was: ' + signal);
      console.log('finished');
    });

    //commit('SET_symPY', s)
  },
  PY_summ({commit}, num) {
    // console.log(num)
    //let s = num.x + num.y;

    let pyshell = new PythonShell('engine/summ.py', { mode: 'json' });

    pyshell.send({x: num.x, y: num.y});

    pyshell.on('message', function (data) {
      console.log(data);
    });

    pyshell.end(function (err, code, signal) {
      if (err) throw err;
      console.log('The exit code was: ' + code);
      console.log('The exit signal was: ' + signal);
      console.log('finished');
    });


    //commit('SET_symPY', s)
  }
}

export default {
  namespaced,
  state,
  mutations,
  actions
}
