import Vue    from 'vue';

/****************************************************************************
 * Notes:
 * 
 * The tutorial here is setup based on views and a number of steps in it.
 * How many steps have progressed in each view is independent of the other
 * views.
 * 
 * setCurrentView: sets the view
 * setNextStep: triggers the next step if the element is the one currently
 *    targeted. Or else, clicking on "Got it" in the notifications will
 *    advance the steps as well.
 * 
 * To change the order of the notifications, just reorder the steps in the
 * steps array under a view.
 * 
 * The actual creation of the notifications are in tutorial-notification.vue
 ***************************************************************************/

const namespaced = true;

const state = {
  isTutorialMode: true, // controls both checklist and tips
  isChecklistExpanded: true,
  showTips: true,
  showChecklist: true,
  hasShownWhatsNew: false,
  checklistItems: [
    {
      itemId: 'createModel',
      label: 'Create a model',
      isCompleted: false
    },
    {
      itemId: 'startTraining',
      label: 'Start training your model',
      isCompleted: false
    },
    {
      itemId: 'finishTraining',
      label: 'Finish training and see TEST view',
      isCompleted: false
    }
  ],
  currentView: '',
  tutorialSteps: [
    {
      viewName: 'tutorial-whats-new-view',
      isCompleted: false,
      currentStepCode: '',
      steps: []
    },
    {
      viewName: 'tutorial-model-hub-view',
      isCompleted: false,
      currentStepCode: 'tutorial-model-hub-new-button',
      steps: [
        {
          stepCode: 'tutorial-model-hub-new-button',
          displayText: 'Get started by creating a model.',
          arrowDirection: 'left'
        },
        {
          stepCode: 'tutorial-model-hub-import-button',
          displayText: 'Import a model folder.',
          arrowDirection: 'left'
        },
        {
          stepCode: 'tutorial-model-hub-user-gravatar',
          displayText: 'Hover to see your user info or log out.',
          arrowDirection: 'top-right'
        },
        {
          stepCode: 'tutorial-model-hub-question-mark',
          displayText: 'Press to get access to help or resources.',
          arrowDirection: 'top-right'
        },
        {
          stepCode: 'tutorial-model-hub-report-button',
          displayText: 'If something goes wrong, you can report it and we will make sure it gets fixed!',
          arrowDirection: 'top-right'
        }
      ]
    },
    {
      viewName: 'tutorial-create-model-view',
      isCompleted: false,
      currentStepCode: 'tutorial-create-model-new-model',
      steps: [
        {
          stepCode: 'tutorial-create-model-new-model',
          displayText: 'Choose a model template, empty if you want to build your model from scratch.',
          arrowDirection: 'right'
        },
        {
          stepCode: 'tutorial-create-model-description',
          displayText: 'A quick overview of the model.',
          arrowDirection: 'left'
        },
        {
          stepCode: 'tutorial-create-model-model-name',
          displayText: 'This is where you give the model a name.',
          arrowDirection: 'left'
        },
        {
          stepCode: 'tutorial-create-model-model-path',
          displayText: 'This is where the model folder will be saved.',          
          arrowDirection: 'left'
        }
      ]
    },
    {
      viewName: 'tutorial-workspace-view',
      isCompleted: false,
      currentStepCode: 'tutorial-workspace-layer-menu',
      steps: [
        {
          stepCode: 'tutorial-workspace-layer-menu',
          displayText: 'You build out your model by combining components. You can find the components in these categories.',
          arrowDirection: 'left'
        },
        {
          stepCode: 'tutorial-workspace-layer-data',
          displayText: 'Drag out a component to start building your model.',
          overrideActions: {
            setup: 'tutorial-workspace-layer-data-setup',
            teardown: 'tutorial-workspace-layer-data-teardown'
          }
        },
        {
          stepCode: 'tutorial-workspace-settings',
          displayText: 'Here you can modify your component. If something is missing you can press <strong>Open Code</strong> to custom-edit the component.',
          overrideActions: {
            setup: 'tutorial-workspace-settings-setup',
          }
        },
        {
          stepCode: 'tutorial-workspace-preview-toggle',
          displayText: 'Toggle <strong>Preview</strong> button to see all visualizations at once.',
          arrowDirection: 'right'
        },
        {
          stepCode: 'tutorial-workspace-notebook-view-toggle',
          displayText: 'Toggle notebook view to see your model in a Jupyter notebook format.',
          arrowDirection: 'right'
        },
        {
          stepCode: 'tutorial-workspace-start-training',
          displayText: 'When you are happy with your model press Run to start training it.',
          arrowDirection: 'left'
        },
        {
          stepCode: 'tutorial-workspace-settings-code',
          displayText: 'Here you can view and customize the code of the component.',
          arrowDirection: 'right'
        },
      ]
    },
    {
      viewName: 'tutorial-core-side-view',
      isCompleted: false,
      currentStepCode: '',
      steps: []
    },
    {
      viewName: 'tutorial-statistics-view',
      isCompleted: false,
      currentStepCode: 'tutorial-statistics-tabs',
      steps: [
        {
          stepCode: 'tutorial-statistics-tabs',
          displayText: 'Click on different tabs to get different overview statistics of how the training is going.',
          overrideActions: {
            setup: 'tutorial-statistics-tabs-setup',
          }
        },
        {
          stepCode: 'tutorial-statistics-map',
          displayText: 'Click on a component on the map to change the content in the Viewbox to the right, this will let you peek into each component.',
          arrowDirection: 'left'
        },
        {
          stepCode: 'tutorial-statistics-controls',
          displayText: 'Here you can pause, stop or skip validation.',
          arrowDirection: 'left'
        },
      ]
    },
    {
      viewName: 'tutorial-general-results-view',
      isCompleted: false,
      currentStepCode: '',
      steps: []
    },
    {
      viewName: 'tutorial-test-view',
      isCompleted: false,
      currentStepCode: 'tutorial-test-right-chart',
      steps: [
        {
          stepCode: 'tutorial-test-right-chart',
          displayText: 'Here you can see the prediction of your model for a specific sample.',
          arrowDirection: 'right'
        },
        {
          stepCode: 'tutorial-test-left-chart',
          displayText: 'The content here can be changed by clicking on the map below, just like with the Viewbox.',
          arrowDirection: 'left'
        },
        {
          stepCode: 'tutorial-test-controls',
          displayText: 'Press here to go to the next sample.',
          arrowDirection: 'left'
        },
      ]
    }, 
    {
      viewName: 'data-wizard-onboarding',
      isCompleted: false,
      currentStepCode: 'tutorial-data-wizard-load-csv',
      steps: [
        {
          stepCode: 'tutorial-data-wizard-load-csv',
          displayText: '<p style="text-align: center;">Load your CSV data here. Each column will represent one input or output feature.</p> <p style="text-align: center;">Here is an example of how Image Classification can look like.</p> <img src="/static/img/tutorial/load-csv.png" style="width: 80%;margin: 5px auto;display: block;">',
          arrowDirection: 'left'
        },
        {
          stepCode: 'tutorial-data-wizard-csv-explanation',
          displayText: '<p style="text-align: center;">Here you can see a preview of the data which you have loaded. Make sure that the column names are at the top.</p>',
          arrowDirection: 'left'
        },
        {
          stepCode: 'tutorial-data-wizard-io-explanation',
          displayText: '<p style="text-align: center;">Here you get to set if a column is an input or an output feature, as well as what type they are.<br/>Output features are your targets and Input features is the data you feed your model.</p> <p style="text-align:center;">Make sure to set the correct type so that your data will be treated properly.</p>',
          arrowDirection: 'left'
        }
      ]
    }
  ],
  activeNotifications: []
};

const getters = {
  getIsTutorialMode(state) {
    return state.isTutorialMode;
  },
  getHasShownWhatsNew(state) {
    return state.hasShownWhatsNew;
  },  
  getShowTutorialTips(state) {
    return state.showTips;
  },
  getIsChecklistExpanded(state) {
    return state.isChecklistExpanded;
  },
  getShowChecklist(state) {
    return state.showChecklist;
  },
  getChecklistItems(state) {
    return state.checklistItems;
  },
  getCurrentView(state) {
    return state.currentView;
  },
  getTutorialNotificationDisplayText: state => stepCode => {
    try {
      const tutorialStep = state.tutorialSteps.find(ts => ts.viewName === state.currentView);
      const step = tutorialStep.steps.find(s => s.stepCode === stepCode);

      return step.displayText;
    } catch (err) {
      return '';
    }
  },
  getStep: state => stepCode => {
    try {
      for(const ts of state.tutorialSteps) {
        for(const s of ts.steps) {
          if(s.stepCode === stepCode) {
            return s;
          }
        }
      }
      
      return null;
    } catch (err) {
      // console.log('Error: getStep', err)
    }
  },
  getCurrentViewSteps(state) {
    try {
      const tutorialStep = state.tutorialSteps.find(ts => ts.viewName === state.currentView);
      return tutorialStep;
    } catch (err) {
      return null;
    }
  },
  getCurrentStep(state) {
    try {
      const tutorialStep = state.tutorialSteps.find(ts => ts.viewName === state.currentView);
      // console.log('getCurrentStep', tutorialStep)
      
      if (!tutorialStep || tutorialStep.isCompleted) { return null; }
      
      const step = tutorialStep.steps.find(s => s.stepCode === tutorialStep.currentStepCode);
      return step;
    } catch (err) {
      return null;
    }
  },
  getCurrentStepCode(state) {

    const tutorialSteps = state.tutorialSteps.find(ts => ts.viewName === state.currentView);
    // console.log('getCurrentStepCode - tutorialSteps', tutorialSteps);

    return tutorialSteps && tutorialSteps.currentStepCode ? tutorialSteps.currentStepCode : '';
  },
  getActiveNotifications(state) {
    return state.activeNotifications;
  },
};

const mutations = {
  
  setTutorialMode(state, value) {
    state.isTutorialMode = value;
  },
  setHasShownWhatsNew(state, value) {
    state.hasShownWhatsNew = value;
  },
  setTutorialNotificationsState(state, value) {
    state.showTips = value;
  },
  setChecklistExpandedState(state, value) {
    state.isChecklistExpanded = !!value
  },
  setShowChecklist(state, value) {
    state.showChecklist = !!value
  },
  setChecklistItemComplete(state, { itemId }) {
    const item = state.checklistItems.find(cli => cli.itemId === itemId);
    if (!item) { return; }

    item.isCompleted = true;
  },
  setChecklistStateClosedIfAllItemsComplete(state) {
    if (!state.checklistItems.every(cli => cli.isCompleted)) { return; }

    state.showChecklist = false;
  },
  setCurrentView(state, value) {
    state.currentView = value;
  },
  setToFirstStepIfNeeded(state) {
    const tutorialStep = state.tutorialSteps.find(ts => ts.viewName === state.currentView);
    if (!tutorialStep ||
        !tutorialStep.isCompleted ||
        !tutorialStep.steps ||
        tutorialStep.steps.length === 0) { return; }

    const firstStep = tutorialStep.steps[0];
    tutorialStep.isCompleted = false;
    tutorialStep.currentStepCode = firstStep.stepCode;
  },
  setNextStep(state) {
    const tutorialStep = state.tutorialSteps.find(ts => ts.viewName === state.currentView);
    if (!tutorialStep.steps || tutorialStep.steps.length === 0) { return ''; }

    const currentIdx = tutorialStep.steps.findIndex(s => s.stepCode === tutorialStep.currentStepCode);
    if (currentIdx === tutorialStep.steps.length - 1) {
      tutorialStep.currentStepCode = '';
      tutorialStep.isCompleted = true;
    } else {
      tutorialStep.currentStepCode = tutorialStep.steps[currentIdx + 1].stepCode;
    }

    return tutorialStep.currentStepCode;
  },
  addNotification(state, {stepCode, arrowDirection}) {
    // check if notification exists
    const notification = state.activeNotifications.find(an => an.stepCode === stepCode);


    // set current StepCode
    const tutorialStep = state.tutorialSteps.find(ts => ts.viewName === state.currentView)
    tutorialStep.currentStepCode = stepCode;

    if (notification) {
      Vue.set(notification, 'arrowDirection', arrowDirection);
    } else {
      state.activeNotifications.splice(0, 0, {
        stepCode, 
        arrowDirection
      });
    }
  },
  removeNotification(state, {stepCode}) {
    const notificationIdx = state.activeNotifications.findIndex(an => an.stepCode === stepCode);

    if (notificationIdx === -1) { return; }

    state.activeNotifications.splice(notificationIdx, 1);
  },
  removeAllNotifications(state) {
    if (!state.activeNotifications || state.activeNotifications.length === 0) { return; }

    while (state.activeNotifications.length > 0) {
      state.activeNotifications.splice(0, 1);
    }
  },
  saveTutorialProgress(state) {
    
    const tutorialProgress = {
      isTutorialMode: state.isTutorialMode,
      isChecklistExpanded: state.isChecklistExpanded,
      showTips: state.showTips,
      showChecklist: state.showChecklist,
      hasShownWhatsNew: state.hasShownWhatsNew,
      checklistItems: state.checklistItems.map(cli => (
        {
          itemId: cli.itemId, 
          isCompleted: cli.isCompleted
        })),
      tutorialSteps: state.tutorialSteps.map(ts => ({
        viewName: ts.viewName,
        isCompleted: ts.isCompleted,
        currentStepCode: ts.currentStepCode
      }))
    };

    localStorage.setItem('tutorialProgress', JSON.stringify(tutorialProgress));

  },
  loadTutorialProgress(state) {
    
    const progress = localStorage.getItem('tutorialProgress');
    if (!progress) { return; }

    const parsedProgress = JSON.parse(progress);
    // console.log('loadTutorialProgress', JSON.parse(progress));

    state.isTutorialMode = parsedProgress.isTutorialMode;
    state.isChecklistExpanded = parsedProgress.isChecklistExpanded;
    state.showTips = parsedProgress.showTips;
    state.showChecklist = parsedProgress.showChecklist,

    state.hasShownWhatsNew = parsedProgress.hasShownWhatsNew;

    for (const pcli of parsedProgress.checklistItems) {
      const scli = state.checklistItems.find(cli => cli.itemId === pcli.itemId);

      if (!scli) { return; }

      // For testing:
      // scli.isCompleted = false;
      scli.isCompleted = pcli.isCompleted;
    }

    for (const pts of parsedProgress.tutorialSteps) {
      const sts = state.tutorialSteps.find(ts => ts.viewName === pts.viewName);

      if (!sts) { return; }
      // For testing:
      // sts.isCompleted = false;
      // sts.currentStepCode = sts.steps[0] ? sts.steps[0].stepCode : '';
      sts.isCompleted = pts.isCompleted;
      sts.currentStepCode = pts.currentStepCode;
    }
  },
};

const actions = {
  activateChecklist({commit, dispatch}) {
    commit('setTutorialMode', true);
    commit('setChecklistExpandedState', true);
    dispatch('activateCurrentStep');
  },
  activateCurrentStep({dispatch, getters}) {
    // Check if no notifications, delegate the last one
    if (getters.getShowTutorialTips && getters.getActiveNotifications.length === 0) {
      // console.log('activateCurrentStep', getters.getCurrentStepCode);
      const step =  getters.getStep(getters.getCurrentStepCode);
      setTimeout(() => {
        dispatch('setupDelegator', { step: step });
      }, 0);
    }
  },
  deactivateCurrentStep({dispatch, getters}) {
    const step =  getters.getStep(getters.getCurrentStepCode);

    setTimeout(() => {
      dispatch('teardownDelegator', { step: step });
    }, 0);
  },
  setChecklistItemComplete({commit, dispatch, getters}, { itemId = '' }) {
    commit('setChecklistItemComplete', { itemId });
    commit('setChecklistStateClosedIfAllItemsComplete', { itemId });
  },
  setShowChecklist({commit, dispatch, getters}, value = true) {
    commit('setShowChecklist', value);
  },
  setTutorialMode({commit, dispatch, getters}, value = false) {
    commit('setTutorialMode', value);

    if (value === false) {
      dispatch('removeAllNotifications');
    }
  },
  setHasShownWhatsNew({commit, dispatch, getters}, value = true) {
    commit('setHasShownWhatsNew', value);
    dispatch('saveTutorialProgress');
  },
  setTutorialNotificationsState({commit, dispatch, getters}, value = false) {
    commit('setTutorialNotificationsState', value);

    if (value) {
      commit('setToFirstStepIfNeeded');

      setTimeout(() => {
        dispatch('activateNotification');
      }, 0);
    } else {
      dispatch('removeAllNotifications');
    }
  },


  /****************************************************************************
   * Setup view/next step and the delegating function
   ***************************************************************************/
  setCurrentView({commit, dispatch, getters}, value = '') {
    // if (!getters.getShowTutorialTips) { return; }
    
    dispatch('removeAllNotifications');
    commit('setCurrentView', value);
    // console.log('%csetCurrentView', 'background: #222; color: #bada55', value);
    
    dispatch('activateNotification');
  },
  setNextStep({commit, dispatch, getters}, {currentStep = '', activateNextStep = true}) {
    if (!getters.getShowTutorialTips) { return; }

    if (currentStep !== '' && currentStep !== getters.getCurrentStepCode) {
      // The currentStep arg shows the parameter of the element triggering the next step.
      // If the names don't match, don't advance the progress of the tutorial. 
      dispatch('activateCurrentStep');
      return;
    }

    const oldStep = getters.getCurrentStep;

    commit('setNextStep', currentStep);
    const newStep = getters.getCurrentStep;


    setTimeout(() => {
      // Adds ability to disable setup so certain triggers can work well:
      // Clicking on Create in the projects view will cause an extra notification to
      // appear if activateNextStep is not deactivated.
      if (activateNextStep) {
        dispatch('setupDelegator', { step: newStep });
      }

      dispatch('teardownDelegator', { step: oldStep });
      dispatch('saveTutorialProgress');
    }, 0);
  },
  setupDelegator({commit, dispatch, getters}, { step }) {
    if (!getters.getShowTutorialTips) { return; }
    if (!step) { return; }

    if (step.overrideActions && step.overrideActions.setup) {
      dispatch(step.overrideActions.setup);
    } else if (step.stepCode !== '') {
      dispatch('commonNotificationSetup', { 
        stepCode: step.stepCode,
        arrowDirection: step.arrowDirection
      });
    }
  },
  teardownDelegator({commit, dispatch, getters}, { step }) {
    if (!step) { return; }

    if (step.overrideActions && step.overrideActions.teardown) {
      dispatch(step.overrideActions.teardown);
    } else if (step.stepCode !== '') {
      dispatch('commonNotificationTeardown', { 
        stepCode: step.stepCode
      });
    }
  },

  
  /****************************************************************************
   * Activate/remove notifications
   ***************************************************************************/
  activateNotification({commit, dispatch, getters}) {
    // Used when a view gets toggled:
    // For instance: Mode lHub -> Created model -> Model Hub
    // Without this action, the unclicked notification will not be shown

    setTimeout(() => {
      dispatch('setupDelegator', { step: getters.getCurrentStep });
    }, 0);
  },
  removeAllNotifications({commit, dispatch, getters}) {
    if (!getters.getActiveNotifications || getters.getActiveNotifications.length === 0) { return; }
    
    const notificationsCopy = getters.getActiveNotifications;

    while (notificationsCopy.length > 0) {      
      const notification = notificationsCopy.pop();
      
      const step = getters.getStep(notification.stepCode);
      dispatch('teardownDelegator', { step });
    }

    commit('removeAllNotifications');
  },

  /****************************************************************************
   * Tutorial progress
   ***************************************************************************/
  saveTutorialProgress({commit}) {
    commit('saveTutorialProgress');
  },
  loadTutorialProgress({commit}) {
    return new Promise((resolve, reject) => {
      commit('loadTutorialProgress');
      resolve();
    });
  },

  /****************************************************************************
   * Common setup/teardown actions
   ***************************************************************************/
  commonNotificationSetup({commit, dispatch, getters}, { stepCode, arrowDirection = 'left' }) {

    try {
      let tutorialTarget = document.querySelector(`*[data-tutorial-target="${stepCode}"]`);
      if (!tutorialTarget) { return; }

      commit('addNotification', { 
        stepCode,
        arrowDirection
      });

    } catch(error) {
      console.log('Error when creating elements to insert', error);
    }

  },
  commonNotificationTeardown({commit, dispatch, getters}, { stepCode }) {

    commit('removeNotification', {
      stepCode: stepCode
    });

  },
  doNothing({commit, dispatch, getters}) {
    // If you don't want to invoke a setup or teardown action
  },

  /****************************************************************************
   * Step specific actions
   ***************************************************************************/
  ['tutorial-model-hub-new-button-setup']({commit, dispatch, getters}) {

    if (getters.getCurrentStepCode !== 'tutorial-model-hub-new-button') { return; }
  
    let fileMenuElement;

    try {

      fileMenuElement = document.querySelector('.header-nav_sublist[data-tutorial-marker="MenuItem_File"]');
      fileMenuElement.style.display = 'block';
      
    } catch(error) {
      console.log('Error when creating elements to insert', error);
    }
    
    commit('addNotification', { 
      stepCode: 'tutorial-model-hub-new-button',
      arrowDirection: 'left'
    });

  },
  ['tutorial-model-hub-new-button-teardown']({commit, dispatch, getters}) {

    let fileMenuElement;

    try {
      fileMenuElement = document.querySelector('.header-nav_sublist[data-tutorial-marker="MenuItem_File"]');
      fileMenuElement.style.display = '';

    } catch(error) {
      console.log('Error when removing elements', error);
    }
    
    commit('removeNotification', {
      stepCode: 'tutorial-model-hub-new-button'
    });

  },
  ['tutorial-workspace-layer-data-setup']({commit, dispatch, getters}) {

    try {
      const layerMenuItemElement = document.querySelector('.layer-list-header[data-tutorial-marker="LayerMenuItem_Data"]');
      if (!layerMenuItemElement) { return; }
      
      layerMenuItemElement.classList.add('active');
      
    } catch(error) {
      console.log('Error when creating elements to insert', error);
    }
    
    commit('addNotification', { 
      stepCode: 'tutorial-workspace-layer-data',
      arrowDirection: 'left'
    });

  },
  ['tutorial-workspace-layer-data-teardown']({commit, dispatch, getters}) {

    try {
      const layerMenuItemElement = document.querySelector('.layer-list-header[data-tutorial-marker="LayerMenuItem_Data"]');
      if (!layerMenuItemElement) { return; }

      layerMenuItemElement.classList.remove('active');

    } catch(error) {
      console.log('Error when removing elements', error);
    }
    
    commit('removeNotification', {
      stepCode: 'tutorial-workspace-layer-data'
    });

  },
  ['tutorial-workspace-settings-setup']({commit, dispatch, getters}) {

    try {
      commit('setChecklistExpandedState', false);
    } catch(error) {
      console.log('Error when creating elements to insert', error);
    }
    
    commit('addNotification', { 
      stepCode: 'tutorial-workspace-settings',
      arrowDirection: 'right'
    });

  },
  ['tutorial-statistics-tabs-setup']({commit, rootGetters, getters}) {

    const statisticsTabs = document.querySelector('.statistics-tabs[data-tutorial-target="tutorial-statistics-tabs"]');
    const isSpinnerActive = rootGetters['mod_workspace/GET_showStartTrainingSpinner'];

    if (!statisticsTabs || isSpinnerActive) { return; }

    if (!getters.getCurrentViewSteps.isCompleted) {
      commit('addNotification', { 
        stepCode: 'tutorial-statistics-tabs',
        arrowDirection: 'right'
      });
    }
    
  },
  
};

export default {
  namespaced,
  state,
  getters,
  mutations,
  actions
}
