<template lang="pug">
  aside
    .main_toolbar(
      :class="{'tutorial-active': activeStepStoryboard === 4}"
      v-if="!statisticsIsOpen && !testIsOpen")

      ul.toolbar_list
        li
          button#tutorial_pointer.btn.btn--toolbar(type="button"
            :disabled="!networkIsOpen"
            :class="{'active': networkMode === 'edit'}"
            v-tooltip:bottom="'Edit'"
            v-tooltip-interactive:bottom-right="interactiveInfo.edit"
            @click="setNetMode('edit', 'tutorial_pointer')"
          )
            i.icon.icon-select

        li.toolbar_list-arrow-wrap(
          :class="{'disable-hover': statisticsIsOpen}"
        )
          button#tutorial_list-arrow.btn.btn--toolbar(type="button"
            :disabled="!networkIsOpen"
            :class="{'active': networkMode === 'addArrow'}"
            @click="setNetMode('addArrow', 'tutorial_list-arrow')"
            v-tooltip:bottom="'Arrow'"
            v-tooltip-interactive:bottom="interactiveInfo.arrow"
          )
            i.icon.icon-arrow-left

      ul.toolbar_list
        li
          button.btn.btn--toolbar(type="button"
            @click="toPrevStepHistory"
            :disabled="isDisabledPrevStep"
            v-tooltip:bottom="'Prev step'"
            v-tooltip-interactive:bottom="interactiveInfo.undo"
          )
            i.icon.icon-step-prev
        li
          button.btn.btn--toolbar(type="button"
            @click="toNextStepHistory"
            :disabled="isDisabledNextStep"
            v-tooltip:bottom="'Next step'"
            v-tooltip-interactive:bottom="interactiveInfo.redo"
          )
            i.icon.icon-step-next
      ul.toolbar_list
        li(:class="{'tutorial-active': activeStepStoryboard === 4}")
          button#tutorial_run-training-button.btn.btn--toolbar.bg-primary.run-button(type="button"
            :class="statusStartBtn"
            v-tooltip:bottom="'Run/Stop'"
            v-tooltip-interactive:bottom="interactiveInfo.runButton"
            @click="onOffBtn"
          )
            i.icon.icon-on-off
            span(v-html="statusTraining === 'training' || statusTraining === 'pause' ? 'Stop' : 'Run'")
        //- li
        //-   button#tutorial_pause-training.btn.btn--toolbar.tutorial-relative(type="button"
        //-     :class="{'active': statusNetworkCore === 'Paused'}"
        //-     :disabled="!isTraining"
        //-     v-tooltip:bottom="'Pause'"
        //-     v-tooltip-interactive:bottom="interactiveInfo.pause"
        //-     @click="trainPause"
        //-   )
        //-     i.icon.icon-pause
        //- li
        //-   button.btn.btn--toolbar(type="button"
        //-     :disabled="statusNetworkCore !== 'Validation'"
        //-     v-tooltip:bottom="'Skip'"
        //-     v-tooltip-interactive:bottom="interactiveInfo.skip"
        //-     @click="skipValid"
        //-   )
        //-     i.icon.icon-next
      //- ul.toolbar_list
      //-   li
      //-     input.search-bar(
      //-       placeholder="Search operation"
      //-     )
      ul.toolbar_list
        li
          span TensorFlow 1.15 
      ul.toolbar_list
        li
          span Python 3
          span.btn.python-status(
            :class="{'connected': statusLocalCore === 'online', 'disconnected': statusLocalCore === 'offline'}"
            v-tooltip:networkElement="kernelLabel"
          )
      //ul.toolbar_list
        li
          button.btn.btn--toolbar(type="button"
            v-tooltip:bottom="'Generate Hyperparameters'"
            v-tooltip-interactive:bottom="interactiveInfo.hyperparameters"
          )
            i.icon.icon-params
        li
          button.btn.btn--toolbar(type="button"
            v-tooltip:bottom="'BlackBox'"
            v-tooltip-interactive:bottom="interactiveInfo.blackBox"
          )
            i.icon.icon-box

      .toolbar_settings
        span.text-primary.middle-text(v-html="statusTrainingText")
        button.btn.btn--dark.btn--toolbar-settings(
          type="button"
          :class="{'active': showModelPreviews}"
          @click="toggleModelPreviews"
          v-tooltip-interactive:bottom="interactiveInfo.interactiveDoc"
        )
          span Preview
          .ring-icon
        button.btn.btn--dark.btn--toolbar-settings(
          type="button"
          :class="{'active': isNotebookMode}"
          @click="switchNotebookMode"
          v-tooltip-interactive:bottom="interactiveInfo.interactiveDoc"
        )
          span Notebook
          .ring-icon

        //- tutorial-instructions(
        //-   ref="tutorialComponent"
        //-   v-tooltip-interactive:bottom="interactiveInfo.tutorial")
        //-   button.btn.btn--dark.btn--toolbar-settings(type="button"
        //-     @click="switchTutorialMode"
        //-     :class="{'active': isTutorialMode}"
        //-   )
        //-     span Tutorial
        //-     .ring-icon

        sidebar-toggle-button
    .layers-toolbar(v-if="!statisticsIsOpen && !testIsOpen")
      layers-toolbar
</template>

<script>
import { mapGetters, mapActions, mapMutations } from 'vuex';
import { googleAnalytics }                      from '@/core/analytics';
import { trainingElements, deepLearnElements }  from '@/core/constants.js';
import { goToLink }                             from '@/core/helpers.js'

import LayersToolbar            from '@/components/toolbar/workspace-toolbar-layers.vue';
import SidebarToggleButton      from '@/components/toolbar/sidebar-toggle-button.vue';

export default {
  name: 'WorkspaceToolbar',
  components: { LayersToolbar, SidebarToggleButton },
  data() {
    return {
      x: null,
      y: null,
      interactiveInfo: {
        edit:     {title: 'Edit',     text: `Use this to being able to drag & ,<br/> drop, select, edit, etc`},
        arrow:    {title: 'Arrow',    text: `Use this to connect the <br/>layers and define the dataflow`},
        undo:     {title: 'Undo',     text: `Use this to connect the <br/>Undo`},
        redo:     {title: 'Redo',     text: `Redo`},
        runButton:{title: 'Run/Stop', text: `Start training/Stop training`},
        pause:    {title: 'Pause',    text: `Pause training/Unpause training`},
        skip:     {title: 'Skip',     text: `Skip validation`},
        hyperparameters: {title: 'Generate Hyperparameters',text: `Auto-generate the hyperparameters`},
        blackBox: {title: 'BlackBox', text: `Load the data and let our algorithm </br> build a model for you and train it`},
        interactiveDoc: {title: 'Interactive documentation', text: `Use this to find out what all </br> different operations and functions do`},
        tutorial: {title: 'Tutorial', text: `Choose an interactive tutorial`}
      },
      reportLink: 'https://join.slack.com/t/perceptilabs-com/shared_invite/enQtODQ5NzAwNDkxOTExLWUxODAwZDk0MzA1MmM4OTViNWE4MmVjYjc2OTQwMTQ4N2NmM2ZlYmI5NjZjOWRiYjBkYjBjMTMzNjEyMDNiNDk'
    }
  },
  computed: {
    ...mapGetters({
      tutorialActiveAction: 'mod_tutorials/getActiveAction',
      interactiveInfoStatus:'mod_tutorials/getInteractiveInfo',
      isTutorialMode:       'mod_tutorials/getIstutorialMode',
      currentElList:        'mod_workspace/GET_currentNetworkElementList',
      isTraining:           'mod_workspace/GET_networkIsTraining',
      statusNetworkCore:    'mod_workspace/GET_networkCoreStatus',
      statisticsIsOpen:     'mod_workspace/GET_statisticsIsOpen',
      testIsOpen:           'mod_workspace/GET_testIsOpen',
      networkIsOpen:        'mod_workspace/GET_networkIsOpen',
      networkHistory:       'mod_workspace-history/GET_currentNetHistory',
      isNotebookMode:       'mod_notebook/getNotebookMode',
    }),
    statusStartBtn() {
      return {
        // 'bg-error':   this.statusTraining === 'training',
        // 'bg-warning': this.statusTraining === 'pause',
        // 'bg-success': this.statusTraining === 'finish',
        //'bg-error': this.statusTraining === 'finish',
      }
    },
    kernelLabel() {
      if(this.statusLocalCore !== "online") {
        return "Kenerl is not connected";
      } else {
        return "Kenerl is connected";
      }
    },
    statusTraining() {
      switch (this.statusNetworkCore) {
        case 'Training':
        case 'Validation':
          return 'training';
          break;
        case 'Paused':
          return 'pause';
          break;
        case 'Finished':
          return 'finish';
          break;
      }
    },
    statusTrainingText() {
      switch (this.statusTraining) {
        case 'training':
          return '<i class="icon icon-repeat animation-loader"></i> Training';
          break;
        case 'pause':
          return 'Training paused';
          break;
        case 'finish':
          return 'Training completed';
          break;
      }
    },
    statusTestText() {
      switch (this.statusTraining) {
        case 'training':
          return '<i class="icon icon-repeat animation-loader"></i> Test running';
          break;
        case 'pause':
          return '<i class="icon icon-notification"></i> Test completed';
          break;
      }
    },
    hideLayers () {
      return this.$store.state.globalView.hideLayers
    },
    currentNetMeta() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta
    },
    networkMode() {
      return this.currentNetMeta.netMode
    },
    statusLocalCore() {
      return this.$store.state.mod_api.statusLocalCore;
    },

    tutorialRunButtonActive() {
      return this.$store.state.mod_tutorials.runButtonsActive
    },
    activeStepStoryboard() {
      return this.$store.state.mod_tutorials.activeStepStoryboard
    },
    confirmPopupAnswer() {
      return this.$store.state.globalView.confirmPopupAnswer
    },
    isDisabledPrevStep() {
      const history = this.networkHistory;
      return !!history && history.historyStep === history.historyNet.length - 1
    },
    isDisabledNextStep() {
      const history = this.networkHistory;
      return !!history && history.historyStep === 0
    },
    showCreateIssuesPopup() {
      return this.$store.state.globalView.globalPopup.showCreateIssuesPopup;
    },
    showModelPreviews() {
      return this.$store.state.mod_workspace.showModelPreviews;
    }
  },
  watch: {
    networkIsOpen(newVal) {
      if(!newVal) this.set_netMode('edit');
    }
  },
  methods: {
    ...mapMutations({
      setInteractiveInfo:     'mod_tutorials/SET_interactiveInfo',
      set_showTrainingSpinner:'mod_workspace/SET_showStartTrainingSpinner',
      set_hideLayers:         'globalView/SET_hideLayers',
      GP_showCoreSideSettings:'globalView/GP_showCoreSideSettings',
    }),
    ...mapActions({
      popupConfirm:         'globalView/GP_confirmPopup',
      showInfoPopup:        'globalView/GP_infoPopup',
      pauseTraining:        'mod_api/API_pauseTraining',
      stopTraining:         'mod_api/API_stopTraining',
      skipValidTraining:    'mod_api/API_skipValidTraining',
      tutorialPointActivate:'mod_tutorials/pointActivate',
      removeTooltip:        'mod_tutorials/removeTooltip',
      offMainTutorial:      'mod_tutorials/offTutorial',
      hideTooltip:          'mod_tutorials/hideTooltip',
      set_netMode:          'mod_workspace/SET_netMode',
      set_notebookMode:     'mod_notebook/SET_notebookMode',
      toPrevStepHistory:    'mod_workspace-history/TO_prevStepHistory',
      toNextStepHistory:    'mod_workspace-history/TO_nextStepHistory',
    }),
    switchTutorialMode() {
      this.$refs.tutorialComponent.switchTutorialMode()
    },
    switchNotebookMode() {
      this.set_notebookMode();
    },
    onOffBtn() {
      if (this.statusLocalCore === 'online') {
        if(this.isTraining)  {
          this.trainStop();
        } else {
          this.trainStart();
        }

        this.$nextTick(()=> this.tutorialPointActivate({way:'next', validation: 'tutorial_run-training-button'}))
      } else {
        this.showInfoPopup('Kernel is not connected');
      }
    
    },
    trainStart() {
      googleAnalytics.trackCustomEvent('start-training');
      let valid = this.validateNetwork();
      if (!valid) return;
      this.GP_showCoreSideSettings(true);
    },
    trainStop() {
      this.stopTraining();
      
      this.$store.dispatch('mod_tracker/EVENT_trainingCompleted');
      googleAnalytics.trackCustomEvent('training-completed');
    },
    trainPause() {
      this.pauseTraining();
      this.tutorialPointActivate({way:'next', validation: 'tutorial_pause-training'})
    },
    skipValid() {
      this.skipValidTraining();
    },
    validateNetwork() {
      let net;
      if(this.currentElList) net = Object.values(this.currentElList);
      else {
        this.showInfoPopup('You cannot Run without a Data element and a Training element');
        return false;
      }

      let typeData = net.find((element)=> element.layerType === 'Data');
      if(typeData === undefined) {
        this.showInfoPopup('Data element missing');
        return false
      }

      let typeTraining = net.find((element)=> element.layerType === 'Training');
      if(typeTraining === undefined) {
        this.showInfoPopup('Classic Machine Learning or Training element missing');
        return false
      }
      let trainingIncluded = net.find(element => trainingElements.includes(element.componentName));
      let deepLearnIncluded = true;
      if (trainingIncluded) {
        deepLearnIncluded = net.find(element => deepLearnElements.includes(element.componentName));
      }
      if(deepLearnIncluded === undefined) {
        this.showInfoPopup('If you use the Training elements, you must use the Deep Learn elements');
        return false
      }

      return true;
    },
    toggleLayers () {
      this.set_hideLayers(!this.hideLayers)
    },
    setNetMode(type, tutorial_id) {
      this.set_netMode(type);
      this.tutorialPointActivate({way:'next', validation: tutorial_id})
    },
    toggleInteractiveInfo() {
      this.removeTooltip();
      this.setInteractiveInfo(!this.interactiveInfoStatus);
    },
    toHomePage() {
      if(this.isTutorialMode) {
        this.hideTooltip();
        this.popupConfirm(
          {
            text: 'Are you sure you want to end the tutorial?',
            ok: () => {
              this.offMainTutorial();
              this.$router.push({name: 'projects'});
            }
          });
      } else {
        this.$router.push({name: 'projects'});
      }
    },
    toggleModelPreviews() {
      this.$store.dispatch('mod_workspace/TOGGLE_showModelPreviews');
    }
  },
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .main_toolbar {
    display: flex;
    align-items: center;
    padding: 5px 29px 5px 0;
    background-color: $bg-toolbar-2;
    border: 1px solid rgba(97, 133, 238, 0.4);
    border-radius: 0px;
    position: relative;
    grid-area: toolbar;
    z-index: 7;
    height: $h-toolbar;
  }
  .toggle-wrap {
    width: $w-layersbar * .87;
    text-align: center;
    border-right: 1px solid $toolbar-border;
    @include media('>=medium') {
      width: $w-layersbar;
    }
    .btn--toolbar {
      @include multi-transition(transform);

      margin: auto;
      transform: rotate(0);
    }
    &.hide-layers {
      .btn--toolbar {
        transform: rotateX(-180deg);
      }
    }
  }
  .toolbar_list {
    display: flex;
    align-items: center;
    margin: 0;
    padding: 0 .7143rem;
    list-style: none;
    > li + li {
      margin-left: .3571rem;
    }
    + .toolbar_list {
      border-left: 1px solid $toolbar-separator-color;
    }

    &:first-child {
      margin-left: 2rem;
      padding-left: 0;
    }
  }
  .run-button {

    width: 5.5rem;
    height: 2.5rem;
    padding: 0 .5rem;
    background: #2E3A5A;
    border: 1px solid #5E6F9F;

    color: $toolbar-button-border;
    margin-left: 0.2rem;
    font-size: 1.2rem;
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 600;
    font-size: 12px;
    line-height: 16px;


    &:hover {
      color: $white;
    }
  }
  .toolbar_list-arrow-wrap {
    position: relative;
    > .btn {
      position: relative;
    }
    &:hover {
      .toolbar_list-arrow {
        opacity: 1;
        max-height: 7.5rem;
      }
    }
    &.disable-hover:hover {
      .toolbar_list-arrow {
        opacity: 0;
        max-height: 0;
      }
    }
  }
  .toolbar_list-arrow {
    @include multi-transition(max-height, opacity);

    position: absolute;
    top: 0;
    left: 0;
    opacity: 0;
    overflow: hidden;
    max-height: 0;
    margin: 0;
    padding: 0;
    list-style: none;
    li + li {
      margin-top: 2px;
    }
    .btn {
      z-index: 1;
      background-color: $bg-workspace-2;
    }
  }
  .toolbar_settings {
    display: flex;
    align-items: center;
    margin-left: auto;
    > * + * {
      margin-left: .4rem;
      margin-right: .4rem;
    }

    > *:last-child {
      margin-left: .4rem;
      margin-right: 0;
    }
  }
  #tutorial_pointer {
    position: relative;
  }
  .btn--tutorial {
    font-size: 2.1rem;
    width: 2.4rem;
    height: 2.4rem;
    background: $bg-grad-blue;
    border-radius: 50%;
    margin: .4rem;
  }
  .btn--toolbar-settings {
    min-width: 0;
    color: $toolbar-button-border;
    background: $bg-toolbar-2;

    padding-right: 1rem;
    padding-left: 1rem;
    border: 1px solid $toolbar-separator-color;

    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 600;
    font-size: 12px;


    .ring-icon {
      margin-left: .7rem;
      font-size: 12px;

      width: 1rem;
      height: 1rem;
      border-radius: 50%;
      border: 2px solid $toolbar-button-border;
    }

    &.active {
      color: $color-1;
      border: 1px solid $color-1;

      & > .ring-icon {
        border: 2px solid $color-1;
      }
    }

  }

  .search-bar {
    background: #363E51;
    border: 1px solid rgba(97, 133, 238, 0.2);
    box-sizing: border-box;
    border-radius: 2px;
    width: 20rem;

  }
  .python-status {
    display: inline-block;
    margin-left: .7rem;
    font-size: 12px;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    vertical-align: baseline;
    &.connected {
      background-color: #73FEBB;
    }
    &.disconnected {
     background-color: #FE7373;
    }
  }
  
</style>
