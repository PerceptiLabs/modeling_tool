const namespaced = true;

const state = {
  calcArray: 0,
  openFile: 0,
};

const mutations = {
  set_calcArray(state) {
    state.calcArray++
  },
  set_openFile(state) {
    state.openFile++
  },
};

const actions = {
  EVENT_calcArray({commit}) {
    commit('set_calcArray')
  },
  EVENT_openFile({commit}) {
    commit('set_openFile');

    // fs.writeFile('D:\\textfile.txt', "Превед", function(err) {
    //   if(err) {
    //     return console.log(err);
    //   }
    //
    //   console.log("Файл сохранён.");
    // });
  }
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
