const namespaced = true;

const state = {
  isTutorialMode: true,
  showTutorialStoryBoard: false,
  activeStepStoryboard: 0,

  activeStepMainTutorial: 0,
  
  activePointMainTutorial: 0,
  activeActionMainTutorial: 0,
  firstTimeApp: localStorage.showFirstAppTutorial ? false : true,
  interective: {
    first_instructions: {
      title: 'Instructions:',
      points: [
        {
          actions: [
            {
              tooltip: '',
              actionStatus: 'done'
            },
          ],
          pointStatus:'done',
          content: '<div class="text-block">When working with AI, you can divide the process into 2 overarching steps:</div><p>1) Knowing your data</p> <p>2) Building your model</p>'
        }
      ]
    },
    import_data: {
      title: 'Step 1. Import your data',
      points: [
        {
          pointStatus:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Data</div> > Select and drop <div class="marker">Data</div> to workspace > Load dataset',
          actions: [
            {
              tooltip: 'Data > Data...',
              actionStatus: 'disabled'
            },
            {
              tooltip: 'Data > Data...',
              actionStatus: 'disabled'
            },
            {
              tooltip: 'Select MNIST dataset > Load...',
              actionStatus: 'disabled'
            },
            {
              tooltip: 'Select MNIST dataset > Load...',
              actionStatus: 'disabled'
            }
          ],
        },
        {
          pointStatus:'disabled',
          tooltip: 'Data > Data...',
          content: 'For this tutorial we will use the MNIST dataset',
        },
        {
          pointStatus:'disabled',
          tooltip: 'Select MNIST dataset > Load...',
          content: 'Every input image has been flattened out to a 784x1 array.',
        },
        {
          pointStatus:'disabled',
          tooltip: 'Data > Data...',
          content: 'Repeat this step for your label data – also known as ground truth (GT) required to train your supervised AI model.'
        }
      ]
    }
  }
};

const getters = {
  getIterective(state) {
    return state.interective
  },
  getIstutorialMode(state) {
    return state.isTutorialMode
  },
  getActiveStepMainTutorial(state) {
    return state.activeStepMainTutorial
  },
  getActiveStep(state) {
    return Object.keys(state.interective)[state.activeStepMainTutorial]
  },
  getPoints(state, getters) {
    return state.interective[getters.getActiveStep].points
  },
  getActivePoint(state, getters) {
    return getters.getPoints[state.activePointMainTutorial]
  },
  getActiveAction(state, getters) {
    return getters.getActivePoint.actions[state.activeActionMainTutorial]
  }
}

const mutations = {
  SET_isTutorialMode(state, value) {
    state.isTutorialMode = value
  },
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
    value === 'next' ? state.activeStepMainTutorial++ : state.activeStepMainTutorial--
  },
  SET_firstTimeApp(state, value) {
    localStorage.showFirstAppTutorial = value;
    state.showTutorial = value;
    state.firstTimeApp = value;
  },
  SET_pointActivate(state, value,) {
    let points = state.interective[value.step].points;
    points[value.point].pointStatus = value.pointStatus;
  },
  SET_activeAction(state, value) {
    let actions = state.interective[value.step].points[value.point].actions;
    actions[value.action].actionStatus = value.actionStatus
  }
};

const actions = {
  pointActivate({commit, dispatch, getters}) {
    dispatch('pointsDeactivate')
    //let actionsDoneCount = 0;
    for(let indexPoint = 0; indexPoint < getters.getPoints.length; indexPoint++ ) {
      let point = getters.getPoints[indexPoint]
      if(point.pointStatus === 'disabled') {
        commit('SET_pointActivate', {step: getters.getActiveStep, point: indexPoint, pointStatus: 'active'});
        for(let indexAction = 0; indexAction < point.actions.length; indexAction++) {
          let action = point.actions[indexAction]
          // if(action.actionStatus === 'done') {
          //   actionsDoneCount++
          //   if(actionsDoneCount === point.actions.length) {
          //     break
          //   }
          // }
          if(action.actionStatus === 'active') {
            commit('SET_activeAction',{
              step: getters.getActiveStep, 
              point: indexPoint, 
              action: indexAction, 
              actionStatus: 'done'
            })
          }
          if(action.actionStatus === 'disabled') {
            commit('SET_activeAction',{
              step: getters.getActiveStep, 
              point: indexPoint, 
              action: indexAction, 
              actionStatus: 'active'
            })
            break
          }
        }
        break
      }
    }
  },
  pointsDeactivate({commit, getters}) {
    for(let index = 0; index < getters.getPoints.length; index++ ) {
      if(getters.getActiveStep !== 'first_instructions') {
        commit('SET_pointActivate',{
          step: getters.getActiveStep, 
          point: index, 
          pointStatus: 'disabled'
        })
      }
    } 
  }
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
