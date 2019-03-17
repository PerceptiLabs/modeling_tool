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
          status:'first',
          content: '<div class="text-block">When working with AI, you can divide the process into 2 overarching steps:</div><p>1) Knowing your data</p> <p>2) Building your model</p>'
        }
      ]
    },
    import_data: {
      title: 'Step 1. Import your data',
      points: [
        {
          status:'disabled',
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
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'For this tutorial we will use the MNIST dataset'
            },
            {
              status:'disabled',
              content: 'Every input image has been flattened out to a 784x1 array.'
            }
          ]
        },
        {
          status:'disabled',
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
            }
          ],
        }
      ]
    },
    precessing_reshape: {
      title: 'Step 2. Reshape the dataset',
      points: [
        {
          status:'disabled',
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
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'We want to build an image classifier by using images as input, not a flattened array'
            },
          ]
        },
        {
          status:'disabled',
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
          status:'disabled',
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
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'Convolution means to slide several filters over the input data.',
            },
            {
              status:'disabled',
              content: 'This generates outputs called feature maps, where each feature'
            }
          ]
        },
      ]
    },
    fully_connected_layer: {
      title: 'Step 4. Use a Fully Connected layer',
      points: [
        {
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Deep Learning</div> > <div class="marker">Fully Connected</div> > Connect input > Set neurons',
          actions: [
            {
              tooltip: 'Deep Learning > Fully Connected...',
              id: 'tutorial_deep-learning', 
              status: 'disabled'
            },
            {
              tooltip: 'Deep Learning > Fully Connected...',
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
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'This operation matches the size of outputs of your network to the number of classes from your label data',
            }
          ]
        },
        {
          status:'disabled',
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
          status:'disabled',
          class_style: 'list_subtitle',
          content: 'In the <div class="marker">Operations Toolbar</div> go to <div class="marker">Processing</div> > <div class="marker">One Hot</div> > Connect input > Set classes',
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
              tooltip: 'Set 10 > Apply changes...',
              id: 'tutorial_number-of-classes',
              status: 'disabled'
            }
          ],
          static_info: [
            {
              status:'disabled',
              content: 'This operation transforms your label data to one dimension for each digit/ class (i.e. 10, in this case). '
            },
            {
              status:'disabled',
              content: 'This makes it easier for the AI to differentiate the digits so it can learn faster. '
            }
          ]
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
  getAllPointsIsDone(state, getters) {
    var count = 0;
    getters.getPoints.forEach(point => {
      if(point.status === 'done') count++
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
  SET_staticInfoValue(state, value) {
    let static_info = state.interective[value.step].points[value.point].static_info;
    static_info[value.index].status = value.status
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
    points[value.point].status = value.status;

  },
  SET_activeAction(state, value) {
    let actions = state.interective[value.step].points[value.point].actions;
    actions[value.action].status = value.status
  }
};

const actions = {
  pointActivate({commit, dispatch, getters}, value) {
    console.log(getters.getActiveAction.id, value.validation)
    if(getters.getIstutorialMode && 
      getters.getMainTutorialIsStarted && 
      getters.getActiveAction && 
      getters.getActiveAction.id === value.validation) {
      
        if(value.way === 'next')  {
          dispatch('checkActiveActionAndPoint', value)
        }
        else {
          dispatch('createTooltip', value.searchLayersbar)
          commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, status: 'active'});
        }
    }
  },
  checkActiveActionAndPoint({commit, dispatch, getters}, value) {
    commit('SET_activeAction', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, action: getters.getActiveActionMainTutorial, status: 'done'})
    commit('SET_activeActionMainTutorial', 'next')
    if(getters.getActiveAction) {
      dispatch('createTooltip', value.searchLayersbar)
    } 
    else { // all actions are done
      dispatch('nextPoint')
      if(getters.getActivePoint) {
        commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, status: 'active'});
        dispatch('createTooltip', value.searchLayersbar)
      }
      else { //all points are done
        commit('SET_activePointMainTutorial', 0)
      }
    }
  },
  createTooltip({getters}, searchLayersbar) {
    let activeTooltip = document.querySelector('.tooltip-tutorial')
    if(activeTooltip) activeTooltip.remove()
    let allElements = document.querySelectorAll(`.${getters.getActiveAction.id}.tutorial_layersbar`)
    if(allElements.length > 1) allElements[0].classList.remove('tutorial_layersbar')
    
    if(getters.getActiveAction.tooltip) {
      let workspaceElements = document.querySelectorAll(`.${getters.getActiveAction.id}:not(.tutorial_layersbar)`)
      let element = searchLayersbar ?  document.querySelector(`.${getters.getActiveAction.id}.tutorial_layersbar`) : workspaceElements[workspaceElements.length - 1]
      let tooltipBlock = document.createElement('div');
      tooltipBlock.classList.add('tooltip-tutorial');
      tooltipBlock.innerHTML = getters.getActiveAction.tooltip;
      element.appendChild(tooltipBlock)
    }
  },
  nextPoint({commit, getters}) {
    commit('SET_activeActionMainTutorial', 0)
    commit('SET_pointActivate', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, status: 'done'});
    let static_info = getters.getActivePoint.static_info;
    if(static_info) {
      for(let i = 0; i < static_info.length; i++ ) {
        commit('SET_staticInfoValue', {step: getters.getActiveStep, point: getters.getActivePointMainTutorial, index: i, status: 'done'})
      }
    }
    commit('SET_activePointMainTutorial', 'next')
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
