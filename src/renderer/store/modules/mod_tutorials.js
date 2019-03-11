import { isNumber } from "util";

const namespaced = true;

const state = {
  isTutorialMode: true,
  showTutorialStoryBoard: false,
  mainTutorialIsStarted: false,
  
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
              actionStatus: 'first'
            },
          ],
          pointStatus:'first',
          content: '<div class="text-block">When working with AI, you can divide the process into 2 overarching steps:</div><p>1) Knowing your data</p> <p>2) Building your model</p>'
        }
      ]
    },
    import_data: {
      title: 'Step 1. Import your data',
      points: [
        {
          type: 'interactive',
          pointStatus:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Data</div> > Select and drop <div class="marker">Data</div> to workspace > Load dataset',
          actions: [
            {
              tooltip: 'Data > Data...',
              id: 'tutorial_data',
              status: 'disabled'
            },
            {
              tooltip: 'Data > Data...',
              id: 'tutorial_data-data',
              status: 'disabled'
            },
            {
              tooltip: 'Select MNIST dataset > Load...',
              id: 'tutorial_data-data',
              status: 'disabled'
            },
            {
              tooltip: 'Select MNIST dataset > Load...',
              id: 'tutorial_button-load',
              status: 'disabled'
            },
            {
              tooltip: 'Apply loaded MNIST',
              id: 'tutorial_button-apply',
              status: 'disabled'
            },
            {
              status: 'disabled'
            }
          ],
        },
        {
          type: 'static',
          pointStatus:'disabled',
          content: 'For this tutorial we will use the MNIST dataset',
          actions: [
            {
              status: 'disabled',
              tooltip: ''
            }
          ],
        },
        {
          type: 'static',
          pointStatus:'disabled',
          content: 'Every input image has been flattened out to a 784x1 array.',
          actions: [
            {
              status: 'disabled',
              tooltip: ''
            },
          ],
        },
        {
          type: 'interactive',
          pointStatus:'disabled',
          tooltip: 'Data > Data...',
          content: 'Repeat this step for your label data – also known as ground truth (GT) required to train your supervised AI model.',
          actions: [
            {
              tooltip: 'Data > Data...',
              id: 'tutorial_data',
              status: 'disabled'
            },
            {
              tooltip: 'Data > Data...',
              id: 'tutorial_data-data',
              status: 'disabled'
            },
            {
              tooltip: 'Select MNIST dataset > Load...',
              id: 'tutorial_data-data',
              status: 'disabled'
            },
            {
              tooltip: 'Select MNIST dataset > Load...',
              id: 'tutorial_button-load',
              status: 'disabled'
            },
            {
              tooltip: 'Apply loaded MNIST',
              id: 'tutorial_button-apply',
              status: 'disabled'
            },
            {
              status: 'disabled'
            }
          ],
        }
      ]
    },
    precessing_reshape: {
      title: 'Step 2. Reshape the dataset',
      points: [
        {
          type: 'interactive',
          pointStatus:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Processing</div> > Connect input > Operation settings  ',
          actions: [
            {
              tooltip: 'Processing > Reshape...',
              id: 'tutorial_processing',
              status: 'disabled'
            },
            {
              tooltip: 'Processing > Reshape...',
              id: 'tutorial_process-reshape',
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              id: 'tutorial_process-reshape',
              status: 'disabled'
            },
            {
              tooltip: 'Open settings...',
              id: 'tutorial_process-reshape',
              status: 'disabled'
            },
            {
              tooltip: 'Reshape to 28x28x1 > Apply changes...',
              id: 'tutorial_input-reshape',
              status: 'disabled'
            },
            {
              tooltip: 'Reshape to 28x28x111111111 > Apply changes...',
              id: 'tutorial_processing',
              status: 'disabled'
            },
          ],
        },
        {
          type: 'static',
          pointStatus:'disabled',
          content: 'For this tutorial we will use the MNIST dataset',
          actions: [
            {
              status: 'disabled',
              tooltip: ''
            }
          ],
        },
        {
          type: 'static',
          pointStatus:'disabled',
          content: 'Every input image has been flattened out to a 784x1 array.',
          actions: [
            {
              status: 'disabled',
              tooltip: ''
            },
          ],
        },
        {
          type: 'interactive',
          pointStatus:'disabled',
          tooltip: 'Data > Data...',
          content: 'Repeat this step for your label data – also known as ground truth (GT) required to train your supervised AI model.',
          actions: [
            {
              tooltip: 'Data > Data...',
              id: 'tutorial_data',
              status: 'disabled'
            },
            {
              tooltip: 'Data > Data...',
              id: 'tutorial_data-data',
              status: 'disabled'
            },
            {
              tooltip: 'Select MNIST dataset > Load...',
              id: 'tutorial_data-data',
              status: 'disabled'
            },
            {
              tooltip: 'Select MNIST dataset > Load...',
              id: 'tutorial_button-load',
              status: 'disabled'
            },
            {
              tooltip: 'Apply loaded MNIST',
              id: 'tutorial_button-apply',
              status: 'disabled'
            },
            {
              status: 'disabled'
            }
          ],
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
  getMainTutorialIsStarted(state) {
    return state.mainTutorialIsStarted
  },
  getActiveStepMainTutorial(state) {
    return state.activeStepMainTutorial
  },
  getActivePointMainTutorial(state) {
    return state.activePointMainTutorial
  },
  getActiveActionMainTutorial(state) {
    return state.activeActionMainTutorial
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
  },
  getIsAllActionsDone(state, getters) {
    var count = 0;
    getters.getActivePoint.actions.forEach(action => {
      if(action.status === 'done') count++
    });
    return count === getters.getActivePoint.actions.length
  },
  getAllPointsIsDone(state, getters) {
    var count = 0;
    getters.getPoints.forEach(point => {
      if(point.pointStatus === 'done') count++
    });
    return count === getters.getPoints.length
  }
}

const mutations = {
  SET_isTutorialMode(state, value) {
    state.isTutorialMode = value
  },
  SET_mainTutorialIsStarted(state, value) {
    state.mainTutorialIsStarted = value
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
  SET_activePointMainTutorial(state, value) {
    if(isNumber(value)) {
      state.activePointMainTutorial = value
    } else if(value === 'next') {
      state.activePointMainTutorial++
    }
  },
  SET_activeActionMainTutorial(state, value) {
    if(isNumber(value)) {
      state.activeActionMainTutorial = value
    } else if(value === 'next') {
      state.activeActionMainTutorial++
    }
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
    actions[value.action].status = value.status
  }
};

const actions = {
  pointActivate({commit, dispatch, getters}, value) {
    if(getters.getIstutorialMode && getters.getMainTutorialIsStarted) {
      
      if(getters.getActiveAction && getters.getActiveAction.id === value.validation) {
        if(value.makeClass) dispatch('removeIdInWorkspace')
        if(value.way === 'next') commit('SET_activeActionMainTutorial', 'next')
        dispatch('checkAndSetActiveStep')
        dispatch('createTooltip', value.makeClass)
        commit('SET_activeAction', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, action: getters.getActiveActionMainTutorial, status: 'done'})
      }

      if(getters.getIsAllActionsDone) {
        commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, pointStatus: 'done'});
        if(getters.getActivePointMainTutorial < getters.getPoints.length - 1) commit('SET_activePointMainTutorial', 'next')
        commit('SET_activeActionMainTutorial', 0)

        if(getters.getAllPointsIsDone) {
          commit('SET_activePointMainTutorial', 0) 
        } else {
          dispatch('checkAndSetActiveStep')
          dispatch('createTooltip')
          dispatch('removeIdInWorkspace')
          commit('SET_activeAction', {
            step: getters.getActiveStep, 
            point: getters.getActivePointMainTutorial, 
            action: getters.getActiveActionMainTutorial, 
            status: 'done'
          })
        }
      }

    }
  },
  pointsDeactivate({commit, getters}) {

  },
  createTooltip({getters}, makeClass) {
    let activeTooltip = document.querySelector('.tooltip-tutorial')
    if(activeTooltip) activeTooltip.remove()
    if(getters.getActiveAction.tooltip) {
      let workspaceElements = document.querySelectorAll(`.${getters.getActiveAction.id}`)
      let element = makeClass ? workspaceElements[workspaceElements.length - 1] : document.getElementById(getters.getActiveAction.id)
      let tooltipBlock = document.createElement('div');
      tooltipBlock.classList.add('tooltip-tutorial');
      tooltipBlock.innerHTML = getters.getActiveAction.tooltip;
      console.log(getters.getActiveAction)
      element.appendChild(tooltipBlock)
    }
  },
  checkAndSetActiveStep({commit, getters}) {
    
    if(getters.getActivePoint && getters.getActivePoint.type === 'static') {
      commit('SET_activeActionMainTutorial', 0)
      for (let i = 0; i < getters.getPoints.length; i++) {
        if(getters.getPoints[i].type === 'static') {
          commit('SET_pointActivate', {step: getters.getActiveStep, point: i, pointStatus: 'done'});
          commit('SET_activePointMainTutorial', 'next')
        } 
        else if(getters.getPoints[i].pointStatus === 'done') {
          continue
        } 
        else {
          commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, pointStatus: 'active'});
        }
      }
    } else {
      commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, pointStatus: 'active'});
    }
  },
  removeIdInWorkspace({getters}) {
    let infoSectionTutorialElem = document.querySelector('.info-section_main').querySelector(`#${getters.getActiveAction.id}`)
    if(infoSectionTutorialElem) {
      infoSectionTutorialElem.setAttribute('id', '')
      infoSectionTutorialElem.classList.add(getters.getActiveAction.id)
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
