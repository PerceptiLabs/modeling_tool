import { isNumber } from "util";

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
              tooltip: 'Data > Data...1',
              id: 'tutorial_data',
              status: 'disabled'
            },
            {
              tooltip: 'Data > Data...2',
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
              tooltip: 'Data > Data...3',
              id: 'tutorial_data',
              status: 'disabled'
            },
            {
              tooltip: 'Data > Data...4',
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
    //return true
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
  SET_activePointMainTutorial(state, value) {
    value === 'next' ? state.activePointMainTutorial++ : state.activePointMainTutorial--
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
    if(getters.getIstutorialMode) {

      //1. check first action element 
      if(value === 'next') commit('SET_activeActionMainTutorial', 'next')

      //2. remove old tooltip
      let activeTooltip = document.querySelector('.tooltip-tutorial')
      if(activeTooltip) activeTooltip.remove()
      
      //3. create new tooltip
      console.log('1.',  getters.getActivePoint.content)
      if(getters.getActiveAction.tooltip) {
        let element = document.getElementById(getters.getActiveAction.id)
        element.classList.add('tutorial-relative')
        let tooltipBlock = document.createElement('div');
        tooltipBlock.classList.add('tooltip-tutorial');
        tooltipBlock.innerHTML = getters.getActiveAction.tooltip;
        element.appendChild(tooltipBlock)
      }
     
      //4. remove id atribute in .info-section_main element
      let infoSectionTutorialElem = document.querySelector('.info-section_main').querySelector(`#${getters.getActiveAction.id}`)
      if(infoSectionTutorialElem) infoSectionTutorialElem.setAttribute('id', '')
     
      //5. set action is done
      commit('SET_activeAction', {
        step: getters.getActiveStep, 
        point: getters.getActivePointMainTutorial, 
        action: getters.getActiveActionMainTutorial, 
        status: 'done'})

      //6. marker point
      if(getters.getIsAllActionsDone) {
        commit('SET_pointActivate', {
          step: getters.getActiveStep, 
          point: getters.getActivePointMainTutorial, 
          pointStatus: 'done'
        });
        commit('SET_activePointMainTutorial', 'next')
        commit('SET_activeActionMainTutorial', 0)
      }

      //7. check type action
      if(getters.getActivePoint.type === 'static') {
        commit('SET_activeActionMainTutorial', 0)
        for (let i = 0; i < getters.getPoints.length; i++) {
          if(getters.getPoints[i].type === 'static') {
            commit('SET_pointActivate', {
              step: getters.getActiveStep, 
              point: i,
              pointStatus: 'done'
            });
            commit('SET_activePointMainTutorial', 'next')
          }
        }
      } else {
        commit('SET_pointActivate', {
          step: getters.getActiveStep, 
          point: getters.getActivePointMainTutorial, 
          pointStatus: 'active'
        });
        console.log('2.', getters.getActivePoint.content)
      }
    }
  },
  pointsDeactivate({commit, getters}) {
    commit('SET_activeActionMainTutorial', 0)
    for(let indexPoint = 0; indexPoint < getters.getPoints.length; indexPoint++ ) {
      if(getters.getActiveStep !== 'first_instructions') {
        let point = getters.getPoints[indexPoint]
        commit('SET_pointActivate',{
          step: getters.getActiveStep, 
          point: indexPoint, 
          pointStatus: 'disabled'
        })
        for(let indexAction = 0; indexAction < point.actions.length; indexAction++) {
          commit('SET_activeAction',{
            step: getters.getActiveStep, 
            point: indexPoint, 
            action: indexAction, 
            actionStatus: 'disabled'
          })
        }
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
