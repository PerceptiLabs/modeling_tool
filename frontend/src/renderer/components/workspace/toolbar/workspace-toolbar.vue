<template lang="pug">
  aside.page_toolbar(:class="{'tutorial-active': activeStepStoryboard === 4}")

    toolbar-layers
    
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
          :disabled="statusLocalCore === 'offline'"
          :class="statusStartBtn"
          v-tooltip:bottom="'Run/Stop'"
          v-tooltip-interactive:bottom="interactiveInfo.runButton"
          @click="onOffBtn"
        )
          i.icon.icon-on-off
          span(v-html="statusTraining === 'training' || statusTraining === 'pause' ? 'Stop' : 'Run'")
      li
        button#tutorial_pause-training.btn.btn--toolbar.tutorial-relative(type="button"
          :class="{'active': statusNetworkCore === 'Paused'}"
          :disabled="!isTraining"
          v-tooltip:bottom="'Pause'"
          v-tooltip-interactive:bottom="interactiveInfo.pause"
          @click="trainPause"
        )
          i.icon.icon-pause
      li
        button.btn.btn--toolbar(type="button"
          :disabled="statusNetworkCore !== 'Validation'"
          v-tooltip:bottom="'Skip'"
          v-tooltip-interactive:bottom="interactiveInfo.skip"
          @click="skipValid"
        )
          i.icon.icon-next
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
        :class="{'btn--tutorial-active': false}"
        v-coming-soon="true"
        v-tooltip-interactive:bottom="interactiveInfo.interactiveDoc"
      )
        span Notebook
        i.icon.icon-ellipse

      button.btn.btn--dark.btn--toolbar-settings(
        type="button"
        :class="{'btn--tutorial-active': interactiveInfoStatus}"
        @click="toggleInteractiveInfo"
        v-tooltip-interactive:bottom="interactiveInfo.interactiveDoc"
      )
        span Help
        i.icon.icon-ellipse

      tutorial-instructions(
        ref="tutorialComponent"
        v-tooltip-interactive:bottom="interactiveInfo.tutorial")
        button.btn.btn--dark.btn--toolbar-settings(type="button"
          @click="switchTutorialMode"
          :class="{'btn--tutorial-active': isTutorialMode}"
        )
          span Tutorial
          i.icon.icon-ellipse
</template>

<script>
import { mapGetters, mapActions, mapMutations } from 'vuex';
import { googleAnalytics }                      from '@/core/analytics';
import { trainingElements, deepLearnElements }  from '@/core/constants.js'

import TutorialInstructions     from '@/components/tutorial/tutorial-instructions.vue'
import ToolbarLayers            from '@/components/workspace/toolbar/workspace-toolbar-layers.vue'

export default {
  name: 'WorkspaceToolbar',
  components: { TutorialInstructions, ToolbarLayers },
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
      }
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
      networkIsOpen:        'mod_workspace/GET_networkIsOpen',
      networkHistory:       'mod_workspace-history/GET_currentNetHistory',
    }),
    statusStartBtn() {
      return {
        'bg-error':   this.statusTraining === 'training',
        'bg-warning': this.statusTraining === 'pause',
        'bg-success': this.statusTraining === 'finish',
        //'bg-error': this.statusTraining === 'finish',
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
      toPrevStepHistory:    'mod_workspace-history/TO_prevStepHistory',
      toNextStepHistory:    'mod_workspace-history/TO_nextStepHistory',
    }),
    switchTutorialMode() {
      this.$refs.tutorialComponent.switchTutorialMode()
    },
    onOffBtn() {
      if(this.isTraining) this.trainStop();
      else this.trainStart();
      this.$nextTick(()=> this.tutorialPointActivate({way:'next', validation: 'tutorial_run-training-button'}))
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
      Analytics.googleAnalytics.trackCustomEvent('training-completed');
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
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../../scss/base";
  .page_toolbar {
    display: flex;
    align-items: center;
    padding: 5px .5em 5px 0;
    background-color: $bg-toolbar-2;
    border: 1px solid rgba(97, 133, 238, 0.2);
    border-radius: 2px 2px 0px 0px;
    position: relative;
    grid-area: toolbar;
    z-index: 2;
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
    }
  }
  .btn--toolbar-home {
    color: #7397fe;
  }
  .run-button {
    color: $col-txt2;
    font-weight: 700;
    width: auto;
    font-size: 1.3rem;
    padding: 0 .5rem;
    &:hover {
      color: $col-primary;
    }
    span {
      margin-left: 0.2rem;
      font-size: 1.2rem;
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
    color: inherit;
    padding-right: 1rem;
    padding-left: 1rem;

    .icon {
      margin-left: .7rem;
    }
  }
  .btn--tutorial-active {
    .icon {
      color: $color-1;;
    }
  }
  .btn-toolbar--home {
    color: $color-5;
  }
</style>
