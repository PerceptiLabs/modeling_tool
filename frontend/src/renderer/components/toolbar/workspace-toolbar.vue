<template lang="pug">
  aside
    .main_toolbar(
      :class="{'tutorial-active': activeStepStoryboard === 4}"
      v-if="!statisticsIsOpen && !testIsOpen")

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
      .horizontal-separator
      ul.toolbar_list
        li(:class="{'tutorial-active': activeStepStoryboard === 4}")
          button#tutorial_run-training-button.btn-menu-bar(type="button"
            :class="statusStartBtn"
            v-tooltip:bottom="'Run/Stop'"
            v-tooltip-interactive:bottom="interactiveInfo.runButton"
            :data-tutorial-target="'tutorial-workspace-start-training'"
            @click="onOffBtn"
          )
            i.icon.icon-on-off
            span(v-html="statusTraining === 'training' || statusTraining === 'pause' ? 'Stop' : 'Run'")
      .horizontal-separator
      ul.toolbar_list
        li(:class="{'tutorial-active': activeStepStoryboard === 4}")
          button#tutorial_run-training-button.btn-menu-bar(type="button"
            :class="{'disabled': !networkIsTrained , 'active': statisticsIsOpen && isOnModelToolPage()}"
            @click="toModelStatistic"
          )
            | Go to statistics

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
        button.btn-menu-bar(
            type="button"
            :class="{'active': modelWeightsActive, 'disabled': !networkHasCheckpoint}"
            @click="toggleModelWeights"
            v-tooltip-interactive:bottom="interactiveInfo.interactiveDoc"
            v-tooltip:bottom="networkHasCheckpoint?'Press this to load your most recent checkpoint':'You do not have any checkpoints, run a model to create some'"
            :data-tutorial-target="'tutorial-workspace-preview-toggle'"
          )
            span Weights
            .ring-icon
        button.btn-menu-bar(
          type="button"
          :class="{'active': showModelPreviews}"
          @click="toggleModelPreviews"
          v-tooltip-interactive:bottom="interactiveInfo.interactiveDoc"
          :data-tutorial-target="'tutorial-workspace-preview-toggle'"
        )
          span Preview
          .ring-icon
        
        div.horizontal-separator
        
        button.button-model-type.ml-0(
          type="button"
          :class="{'active': !isNotebookMode}"
          @click="switchNotebookMode(false)"
          v-tooltip-interactive:bottom="interactiveInfo.interactiveDoc"
          :data-tutorial-target="'tutorial-workspace-notebook-view-toggle'"          
        )
          span Modeling
        
        button.button-model-type.ml-0(
          type="button"
          :class="{'active': modelWeightsActive, 'disabled': !networkHasCheckpoint}"
          @click="toggleModelWeights"
        )
          span Weights
          .ring-icon
        button.btn.btn--dark.btn--toolbar-settings(
          type="button"
          :class="{'active': isNotebookMode}"
          @click="switchNotebookMode(true)"
          v-tooltip-interactive:bottom="interactiveInfo.interactiveDoc"
          :data-tutorial-target="'tutorial-workspace-notebook-view-toggle'"          
        )
          span Notebook
      
        sidebar-toggle-button
    .layers-toolbar(v-if="!statisticsIsOpen && !testIsOpen")
      layers-toolbar
</template>

<script>
import { mapGetters, mapActions, mapMutations, mapState } from 'vuex';
import { googleAnalytics }                      from '@/core/analytics';
import { trainingElements, deepLearnElements }  from '@/core/constants.js';
import { goToLink }                             from '@/core/helpers.js'

import LayersToolbar            from '@/components/toolbar/workspace-toolbar-layers.vue';
import SidebarToggleButton      from '@/components/toolbar/sidebar-toggle-button.vue';

import { saveModelJson as fileserver_saveModelJson } from '@/core/apiFileserver';

export default {
  name: 'WorkspaceToolbar',
  components: { LayersToolbar, SidebarToggleButton },
  created(){
    this.handleStatisticState(this.workspaceModels);
  },
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
      reportLink: 'https://join.slack.com/t/perceptilabs-com/shared_invite/enQtODQ5NzAwNDkxOTExLWUxODAwZDk0MzA1MmM4OTViNWE4MmVjYjc2OTQwMTQ4N2NmM2ZlYmI5NjZjOWRiYjBkYjBjMTMzNjEyMDNiNDk',
      haveAtLeastOneItemStatistic: false,
      statisticItemIndex: null,
    }
  },
  computed: {
    ...mapState({
      workspaceModels:      state => state.mod_workspace.workspaceContent,
      currentNetworkIndex:  state => state.mod_workspace.currentNetwork,
      showNewModelPopup:    state => state.globalView.globalPopup.showNewModelPopup,
    }),
    ...mapGetters({
      interactiveInfoStatus:'mod_tutorials/getInteractiveInfo',
      isTutorialMode:       'mod_tutorials/getIsTutorialMode',
      currentNetwork:       'mod_workspace/GET_currentNetwork',
      currentElList:        'mod_workspace/GET_currentNetworkElementList',
      isTraining:           'mod_workspace/GET_networkIsTraining',
      statusNetworkCore:    'mod_workspace/GET_networkCoreStatus',
      statisticsIsOpen:     'mod_workspace/GET_statisticsIsOpen',
      testIsOpen:           'mod_workspace/GET_testIsOpen',
      networkIsOpen:        'mod_workspace/GET_networkIsOpen',
      isUsingModelWeights:  'mod_workspace/GET_currentNetworkModeWeightsState',
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

    hideLayers () {
      return this.$store.state.globalView.hideLayers
    },
    currentNetMeta() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta
    },
    currentApiMeta() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].apiMeta
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
    },
    modelWeightsActive() {
      return this.isUsingModelWeights;
    },
    networkIsTrained() {
      return typeof this.statisticsIsOpen === 'boolean';
    },
    networkHasCheckpoint() {
      // Checking testIsOpen because it is a boolean if scanCheckpoint returns true.
      // More accurate than the following because it gets set upon training (checkpoints could be deleted)
      // return Object.values(this.currentElList).some(el => el.checkpoint && el.checkpoint.length > 0);
      return typeof this.testIsOpen === 'boolean';
    }
  },
  watch: {
    networkIsOpen(newVal) {
      if(!newVal) this.set_netMode('edit');
    },
    workspaceModels: {
        deep: true,
        handler(models) {
          this.statisticItemIndex = null;
          this.haveAtLeastOneItemStatistic = false;
          this.handleStatisticState(models);
        }
      },
  },
  methods: {
    ...mapMutations({
      setInteractiveInfo:     'mod_tutorials/SET_interactiveInfo',
      set_showTrainingSpinner:'mod_workspace/SET_showStartTrainingSpinner',
      setCurrentStatsIndex:   'mod_workspace/set_currentStatsIndex',
      set_hideLayers:         'globalView/SET_hideLayers',
      GP_showCoreSideSettings:'globalView/GP_showCoreSideSettings',
    }),
    ...mapActions({
      popupConfirm:         'globalView/GP_confirmPopup',
      showInfoPopup:        'globalView/GP_infoPopup',
      pauseTraining:        'mod_api/API_pauseTraining',
      stopTraining:         'mod_api/API_stopTraining',
      skipValidTraining:    'mod_api/API_skipValidTraining',
      removeTooltip:        'mod_tutorials/removeTooltip',
      set_netMode:          'mod_workspace/SET_netMode',
      set_notebookMode:     'mod_notebook/SET_notebookMode',
      toPrevStepHistory:    'mod_workspace-history/TO_prevStepHistory',
      toNextStepHistory:    'mod_workspace-history/TO_nextStepHistory',
      setCurrentView:       'mod_tutorials/setCurrentView',
      setNextStep:          'mod_tutorials/setNextStep',
      SET_openStatistics:   'mod_workspace/SET_openStatistics',
      set_chartRequests:    'mod_workspace/SET_chartsRequestsIfNeeded',
      SET_openTest:         'mod_workspace/SET_openTest',
      SET_currentNetwork:   'mod_workspace/SET_currentNetwork',
    }),
    switchTutorialMode() {
      this.$refs.tutorialComponent.switchTutorialMode()
    },
    switchNotebookMode(setNotebook) {
      this.$store.dispatch('mod_tracker/EVENT_toolbarNotebookButtonToggle', setNotebook);
      this.setNextStep('tutorial-workspace-notebook-view-toggle');
      this.set_notebookMode(setNotebook);
    },
    onOffBtn() {
      if (this.statusLocalCore === 'online') {
        if(this.isTraining)  {
          this.trainStop();
        } else {

          this.setCurrentStatsIndex(this.currentNetworkIndex);

          this.$store.dispatch('mod_api/API_scanCheckpoint', { 
            networkId: this.currentNetwork.networkID,
            path: this.currentNetwork.apiMeta.location
          })
            .then(result => {
              if (result.hasCheckpoint) {
                this.trainStartWithCheckpoint();

                this.$nextTick(() => {
                  this.setNextStep('tutorial-workspace-start-training');
                  this.setCurrentView('tutorial-core-side-view');
                });
              } else {
                this.trainStartWithoutCheckpoint();
              }
            });          
        }
      } else {
        this.showInfoPopup('Kernel is not connected');
      }
    
    },
    trainStartWithCheckpoint() {
      googleAnalytics.trackCustomEvent('start-training');
      let valid = this.validateNetwork();
      if (!valid) return;
      this.GP_showCoreSideSettings(true);
    },
    trainStartWithoutCheckpoint() {
      googleAnalytics.trackCustomEvent('start-training');
      // if toggle off
      // start directly

      // Refactor this and the core in workspace-core-side
      this.$store.commit('mod_workspace/updateCheckpointPaths');
    
      fileserver_saveModelJson(this.currentNetwork);

      this.$store.dispatch('mod_workspace/SET_networkSnapshot')
        .then(_ => this.$store.dispatch('mod_webstorage/saveNetwork'))
        .then(_ => {
          this.$store.dispatch('mod_api/API_startTraining', { loadCheckpoint: false });

          this.$store.dispatch('mod_workspace/SET_openStatistics', true);
          this.$store.dispatch('mod_workspace/setViewType', 'statistic');
          this.$store.dispatch('mod_workspace/SET_openTest', null);
          this.$store.commit('mod_workspace/SET_showStartTrainingSpinner', true);
          this.$store.dispatch('globalView/hideSidebarAction', false);

          this.$store.dispatch('mod_tutorials/setChecklistItemComplete', { itemId: 'startTraining' });
          this.$store.dispatch('mod_tutorials/setCurrentView', 'tutorial-statistics-view');


          this.$nextTick(() => {
            this.setNextStep('tutorial-workspace-start-training');
            this.setCurrentView('tutorial-statistics-view');
          });
        });
    },
    trainStop() {
      this.stopTraining();
      
      this.$store.dispatch('mod_tracker/EVENT_trainingCompleted', 'User stopped');
      googleAnalytics.trackCustomEvent('training-completed');
    },
    trainPause() {
      this.pauseTraining();
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
    },
    toggleInteractiveInfo() {
      this.removeTooltip();
      this.setInteractiveInfo(!this.interactiveInfoStatus);
    },
    toHomePage() {
      this.$router.push({name: 'projects'});
    },
    toggleModelPreviews() {
      this.$store.dispatch('mod_tracker/EVENT_toolbarPreviewButtonToggle', !this.showModelPreviews);
      this.setNextStep('tutorial-workspace-preview-toggle');
      this.$store.dispatch('mod_workspace/TOGGLE_showModelPreviews');
    },
    toggleModelWeights() {
      this.$store.dispatch('mod_workspace/toggleModelWeightsState');

      // Should refactor this
      const fullNetworkElementList = this.$store.getters['mod_workspace/GET_currentNetworkElementList'];
      let payload = {};
      for(let id in fullNetworkElementList) {
        payload[id] = fullNetworkElementList[id].previewVariable;
      }
      this.$store.dispatch('mod_api/API_getBatchPreviewSample', payload);
    },
    isModelPageAndNetworkHasStatistic() {
      return this.$route.name === 'app' && this.currentNetwork.networkMeta.openStatistics !== null
    },
    toModelStatistic() {
        //$route.name === 'app' && currentNetwork.networkMeta.openStatistics !== null
        if(this.$route.name === 'app') {
          // networkMeta.openStatistics !== null
          if(this.isModelPageAndNetworkHasStatistic()) {
            this.$store.dispatch("mod_workspace/setViewType", 'statistic');
            const item = this.workspaceModels[this.statisticItemIndex];
            this.SET_currentNetwork(this.statisticItemIndex)
              .then(() => { 
                this.$store.dispatch("mod_workspace/EVENT_onceDoRequest");
                this.SET_openStatistics(true);
                this.set_chartRequests(item.networkID);
                })
          } else {
            const { statisticItemIndex } = this;
            
            if(statisticItemIndex !== null) {
              this.$store.dispatch("mod_workspace/setViewType", 'statistic');
              this.SET_currentNetwork(statisticItemIndex);
              this.SET_openStatistics(true);
              this.SET_openTest(false);
            }
          }

        } else {
          const { statisticItemIndex } = this;
          if(statisticItemIndex !== null) {
            this.$store.dispatch("mod_workspace/setViewType", 'statistic');
            this.SET_currentNetwork(statisticItemIndex)
              .then(() => {
                this.$router.push({name: 'app'});
                this.SET_openStatistics(true);
              });
          }
        }

        this.$nextTick(() => {
          if (this.showNewModelPopup) {
            this.setCurrentView('tutorial-create-model-view');
          } else {
            this.setCurrentView('tutorial-statistics-view');
          }
        });
      },
    handleStatisticState(models) {
      const firsImteWithStatistcsIndex = models.findIndex(model => model.networkMeta.openStatistics !== null);
      if(firsImteWithStatistcsIndex !== -1) {
          this.haveAtLeastOneItemStatistic = true;
          this.statisticItemIndex = firsImteWithStatistcsIndex;
      } 
    },
    isOnModelToolPage(){
      return this.$route.name === 'app';
    },
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
    z-index: 12;
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
    // padding: 0 .7143rem;
    list-style: none;
    > li + li {
      margin-left: .3571rem;
    }
    // + .toolbar_list {
    //   border-left: 1px solid $toolbar-separator-color;
    // }

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

    &.active:not(.disabled) {
      color: $color-1;
      border: 1px solid $color-1;

      & > .ring-icon {
        border: 2px solid $color-1;
      }
    }

    &.disabled {
      color: #5E6F9F;
      border: 1px solid #5E6F9F;

      pointer-events: none;
      cursor: default;

      & > .ring-icon {
        border: 2px solid #5E6F9F;
      }
    }

  }
  .button-model-type {
    // margin: 16px;
    height: 30px;
    position: relative;
    display: block;
    background-color: transparent;
    // border: 1px solid red;
    color: rgba(182, 199, 251, 0.2);
    font-family: Nunito Sans;
    font-size: 12px;
    &.active {
      font-weight: bold;
      color: #B6C7FB;
      &::after {
        content: "";
        position: absolute;
        background-color: #B6C7FB;
        width: 80%;
        height: 2px;
        left: 10%;
        bottom: 0;
        border-radius: 5px 5px 0 0;
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
  .horizontal-separator {
    height: 20px;
    width: 1px;
    margin-left: 12px;
    margin-right: 12px;
    border-radius: 1px;
    background-color: #5E6F9F;
  }
  .ml-0 {
    margin-left: 0;
  }
</style>
