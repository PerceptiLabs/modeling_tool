import {PythonShell} from 'python-shell';
import Vue from 'vue'
//let pyshell = new PythonShell('../../../test.py', {mode: 'json'});

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
