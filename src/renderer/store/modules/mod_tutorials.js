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
              schematic: {
                type: 'square',
                top: 16.4,
                left: 26
              },
              position_element: {
                top: 6.5,
                left: 18
              },
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
              schematic: {
                type: 'square',
                top: 32.4,
                left: 26
              },
              position_element: {
                top: 22.5,
                left: 18
              },
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
              schematic: {
                type: 'square',
                top: 16.4,
                left: 42,
              },
              position_element: {
                top: 6.5,
                left: 34
              },
              status: 'disabled'
            },
            {
              tooltip: 'Select to create a connection...',
              id: 'tutorial_list-arrow',
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              id: 'tutorial_process-reshape',
              schematic: {
                type: 'arrow'
              },
              status: 'disabled'
            },
            {
              tooltip: 'Go back to work with items...',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Open settings...',
              id: 'tutorial_process-reshape',
              status: 'disabled'
            },
            {
              status: 'disabled',
            },
          ],
        },
        {
          type: 'static',
          pointStatus:'disabled',
          content: 'We want to build an image classifier by using images as input, not a flattened array',
          actions: [
            {
              status: 'disabled',
              tooltip: ''
            }
          ],
        },
        {
          type: 'interactive',
          pointStatus:'disabled',
          class_style: 'list_subtitle',
          content: 'Reshape the dataset into images of shape 28x28x1. ',
          actions: [
            {
              tooltip: 'Reshape to 28x28x1 > Apply changes...',
              id: 'tutorial_input-reshape',
              status: 'disabled'
            }
          ],
        },
      ]
    },
    convolutional_layer: {
      title: 'Step 3. Use a Convolutional layer',
      points: [
        {
          type: 'interactive',
          pointStatus:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Deep Learning</div> > <div class="marker">Convolution</div> > Connect input > Operation settings',
          actions: [
            {
              tooltip: 'Deep Learning > Convolution...',
              id: 'tutorial_deep-learning', 
              status: 'disabled'
            },
            {
              tooltip: 'Deep Learning > Convolution...',
              id: 'tutorial_convolution',
              schematic: {
                type: 'square',
                top: 16.4,
                left: 58,
              },
              position_element: {
                top: 6.5,
                left: 50
              },
              status: 'disabled'
            },
            {
              tooltip: 'Select to create a connection...',
              id: 'tutorial_list-arrow',
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              id: 'tutorial_convolution',
              schematic: {
                type: 'arrow'
              },
              status: 'disabled'
            },
            {
              tooltip: 'Go back to work with items...',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Open settings...',
              id: 'tutorial_convolution',
              status: 'disabled'
            },
            {
              tooltip: '<div class="tooltip-tutorial_italic"><div class="tooltip-tutorial_bold">Patch size:</div> This is the size of the filter.</br> E.g. with patch size 3, the </br> filter will be a square of size 3x3.</div>',
              id: 'tutorial_patch-size',
              status: 'disabled'
            },
            {
              tooltip: '<div class="tooltip-tutorial_italic"><div class="tooltip-tutorial_bold">Stride:</div> This is the step size when </br> we slide the filter over the input </br> data to generate feature maps.</div>',
              id: 'tutorial_stride',
              status: 'disabled'
            },
            {
              tooltip: '<div class="tooltip-tutorial_italic"><div class="tooltip-tutorial_bold">Feature Maps:</div> The number of </br> feature maps correspond to the </br> number of different features to </br> look for in the input data. i.e. with </br> more complex data, it might be </br> better to increase the number </br> of feature maps.</div>',
              id: 'tutorial_feature-maps',
              status: 'disabled'
            },
            {
              tooltip: 'Apply settings',
              id: 'tutorial_apply-button',
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
          content: 'Convolution means to slide several filters over the input data.',
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
          content: 'This generates outputs called feature maps, where each feature',
          actions: [
            {
              tooltip: '',
              status: 'disabled'
            },
          ],
        },
      ]
    },
    fully_connected_layer: {
      title: 'Step 4. Use a Fully Connected layer',
      points: [
        {
          type: 'interactive',
          pointStatus:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Deep Learning</div> > <div class="marker">Fully Connected</div> > Connect input > Set neurons',
          actions: [
            {
              tooltip: 'Deep Learning > Fully Connected...',
              id: 'tutorial_deep-learning', 
              status: 'disabled'
            },
            {
              tooltip: 'Deep Learning > Convolution...',
              id: 'tutorial_fully-connected',
              schematic: {
                type: 'square',
                top: 16.4,
                left: 74,
              },
              position_element: {
                top: 6.5,
                left: 66
              },
              status: 'disabled'
            },
            {
              tooltip: 'Select to create a connection...',
              id: 'tutorial_list-arrow',
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              id: 'tutorial_fully-connected',
              schematic: {
                type: 'arrow'
              },
              status: 'disabled'
            },
            {
              tooltip: 'Go back to work with items...',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Open settings...',
              id: 'tutorial_fully-connected',
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
          content: 'This operation matches the size of outputs of your network to the number of classes from your label data',
          actions: [
            {
              status: 'disabled',
              tooltip: ''
            }
          ],
        },
        {
          type: 'interactive',
          pointStatus:'disabled',
          content: 'Set the same number of neurons as there are classes, which in this case is 10 since the images represent digits 0-9. ',
          actions: [
            {
              tooltip: 'Set neurons > Apply changes...',
              id: 'tutorial_neurons',
              status: 'disabled'
            },
          ],
        },
      ]
    },
    one_hot_encoding: {
      title: 'Step 5. One Hot encoding on labels',
      points: [
        {
          type: 'interactive',
          pointStatus:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Processing</div> > <div class="marker">One Hot/div> > Connect input > Set classes',
          actions: [
            {
              tooltip: 'Processing > One Hot...',
              id: 'tutorial_processing', 
              status: 'disabled'
            },
            {
              tooltip: 'Processing > One Hot...',
              id: 'tutorial_one-hot',
              schematic: {
                type: 'square',
                top: 32.4,
                left: 42,
              },
              position_element: {
                top: 22.5,
                left: 34
              },
              status: 'disabled'
            },
            {
              tooltip: 'Select to create a connection...',
              id: 'tutorial_list-arrow',
              status: 'disabled'
            },
            {
              tooltip: 'Connect input...',
              id: 'tutorial_one-hot',
              schematic: {
                type: 'arrow'
              },
              status: 'disabled'
            },
            {
              tooltip: 'Go back to work with items...',
              id: 'tutorial_pointer',
              status: 'disabled'
            },
            {
              tooltip: 'Set classes...',
              id: 'tutorial_one-hot',
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
          content: 'This operation transforms your label data to one dimension for each digit/ class (i.e. 10, in this case). ',
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
          content: 'This makes it easier for the AI to differentiate the digits so it can learn faster. ',
          actions: [
            {
              tooltip: '',
              status: 'disabled'
            },
          ],
        },
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
        dispatch('changeElementPosition', getters.getActiveAction.position_element)
        if(value.way === 'next') commit('SET_activeActionMainTutorial', 'next')
        //dispatch('removeSchematicElement')
        if(getters.getActiveAction) {
          if(getters.getActiveAction.schematic) dispatch('drawSchematicElement', getters.getActiveAction.schematic)
          dispatch('checkAndSetActiveStep')
          dispatch('createTooltip', value.makeClass)
          commit('SET_activeAction', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, action: getters.getActiveActionMainTutorial, status: 'done'})
        }
      }

      if(getters.getIsAllActionsDone) {
        commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, pointStatus: 'done'});
        if(getters.getActivePointMainTutorial < getters.getPoints.length - 1) commit('SET_activePointMainTutorial', 'next')
        commit('SET_activeActionMainTutorial', 0)

        if(getters.getAllPointsIsDone) {
          commit('SET_activePointMainTutorial', 0) 
        } else {
          dispatch('checkAndSetActiveStep')
          if(getters.getActivePoint) {
            dispatch('createTooltip')
            dispatch('removeIdInWorkspace')
            commit('SET_activeAction', {
              step: getters.getActiveStep, 
              point: getters.getActivePointMainTutorial, 
              action: getters.getActiveActionMainTutorial, 
              status: 'done'
            })
          } else {
            commit('SET_activePointMainTutorial', 0)
          }
        }
      }

    }
  },
  createTooltip({getters}, makeClass) {
    let activeTooltip = document.querySelector('.tooltip-tutorial')
    if(activeTooltip) activeTooltip.remove()
    if(getters.getActiveAction.tooltip) {
      //console.log(getters.getActiveAction.id)
      let workspaceElements = document.querySelectorAll(`.${getters.getActiveAction.id}`)
      let element = makeClass && workspaceElements[workspaceElements.length - 1] ? workspaceElements[workspaceElements.length - 1] : document.getElementById(getters.getActiveAction.id)
      let tooltipBlock = document.createElement('div');
      tooltipBlock.classList.add('tooltip-tutorial');
      tooltipBlock.innerHTML = getters.getActiveAction.tooltip;
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
  },
  drawSchematicElement({getters}, schematic) {
    let infoSection = document.querySelector('.info-section_main')
    let element = document.createElement('div');
    element.classList.add('schematic');
    infoSection.insertBefore(element, infoSection.firstChild)
    switch (schematic.type) {
      case 'square':
        element.classList.add('schematic--square');
        element.style.top = schematic.top + 'rem'
        element.style.left = schematic.left + 'rem'
        break;
      case 'arrow':
        element.classList.add('schematic--arrow');
        let activeElementPosition =  document.querySelector(`.${getters.getActiveAction.id}`).getBoundingClientRect()
        element.style.top = activeElementPosition.top + (activeElementPosition.height / 2)  + 'px'
        element.style.left = activeElementPosition.left - (activeElementPosition.width + activeElementPosition.width / 2) +  'px'
        break;
    }
    
  },
  removeSchematicElement() {
    let schematicElement = document.querySelector('.schematic')
    if(schematicElement) schematicElement.remove()
  },
  changeElementPosition({getters}, position_element) {
    if(position_element) {
      let workspaceElements = document.querySelectorAll(`.${getters.getActiveAction.id}`)
      let activeElement = workspaceElements[workspaceElements.length - 1]
      let parent = activeElement.parentElement.parentElement
      parent.style.top = position_element.top + 'rem'
      parent.style.left = position_element.left + 'rem'
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
