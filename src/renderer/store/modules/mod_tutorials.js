const namespaced = true;

const state = {
  showTutorialStoryBoard: false,
  activeStepStoryboard: 0,
  activeStepMainTutorial: 0,
  firstTimeApp: localStorage.showFirstAppTutorial ? false : true,
  interective: {
    first_instructions: {
      title: 'Instructions:',
      points: [
        {
          done: true,
          isActive: false,
          content: '<div class="text-block">When working with AI, you can divide the process into 2 overarching steps:</div><p>1) Knowing your data</p> <p>2) Building your model</p>'
        }
      ]
    },
    import_data: {
      title: 'Step 1. Import your data',
      points: [
        {
          done: false,
          isActive: false,
          class_style: 'list_subtitle',
          tooltip: 'Data > Data...',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Data</div> > Select and drop <div class="marker">Data</div> to workspace > Load dataset',
        },
        {
          done: false,
          isActive: false,
          tooltip: 'Data > Data...',
          content: 'For this tutorial we will use the MNIST dataset',
        },
        {
          done: false,
          isActive: false,
          tooltip: 'Select MNIST dataset > Load...',
          content: 'Every input image has been flattened out to a 784x1 array.',
        },
        {
          done: false,
          isActive: false,
          tooltip: 'Data > Data...',
          content: 'Repeat this step for your label data – also known as ground truth (GT) required to train your supervised AI model.',
        }
      ]
    }
  }
};

const mutations = {
  SET_runButtonsActive(state, value) {
    state.runButtonsActive = value;
  },
  SET_activeStepStoryboard(state, value) {
    state.activeStepStoryboard = value;
  },
  SET_showTutorialStoryBoard(state, value) {
    state.showTutorialStoryBoard = value;
    state.firstTimeApp = value;
  },
  SET_activeStepMainTutorial(state, value) {
    state.activeStepMainTutorial = value;
  },
  SET_firstTimeApp(state, value) {
    localStorage.showFirstAppTutorial = value;
    state.showTutorial = value;
    state.firstTimeApp = value;
  }
};

const actions = {
 
};

export default {
  namespaced,
  state,
  mutations,
  actions
}
