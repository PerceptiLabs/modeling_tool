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
          )
            svg(width="10" height="9" viewBox="0 0 10 9" fill="none" xmlns="http://www.w3.org/2000/svg")
              path(d="M3.125 3.46154H6.875C7.90875 3.46154 8.75 4.39338 8.75 5.53846C8.75 6.68354 7.90875 7.61539 6.875 7.61539H3.125V9H6.875C8.59813 9 10 7.44715 10 5.53846C10 3.62977 8.59813 2.07692 6.875 2.07692H3.125V0L0 2.76923L3.125 5.53846V3.46154Z")

        li
          button.btn.btn--toolbar(type="button"
            @click="toNextStepHistory"
            :disabled="isDisabledNextStep"
          )
            svg(width="10" height="9" viewBox="0 0 10 9" fill="none" xmlns="http://www.w3.org/2000/svg")
              path(d="M6.875 3.46154H3.125C2.09125 3.46154 1.25 4.39338 1.25 5.53846C1.25 6.68354 2.09125 7.61539 3.125 7.61539H6.875V9H3.125C1.40187 9 0 7.44715 0 5.53846C0 3.62977 1.40187 2.07692 3.125 2.07692H6.875V0L10 2.76923L6.875 5.53846V3.46154Z")

      .layers-toolbar(v-if="!statisticsIsOpen && !testIsOpen")
        layers-toolbar
      //- ul.toolbar_list
      //-   li(:class="{'tutorial-active': activeStepStoryboard === 4}")
      //-     button#tutorial_run-training-button.btn-menu-bar(type="button"
      //-       :class="statusStartBtn"
      //-       v-tooltip:bottom="'Run/Stop'"
      //-       v-tooltip-interactive:bottom="interactiveInfo.runButton"
      //-       :data-tutorial-target="'tutorial-workspace-start-training'"
      //-       @click="onOffBtn(false)"
      //-     )
      //-       img(v-if="showSpinnerOnRun===true" src="static/img/spinner.gif" width="12px" style="margin-right: 5px")
      //-       i.icon.icon-on-off(v-if="showSpinnerOnRun===false")
      //-       span(v-html="statusTraining === 'training' || statusTraining === 'pause' ? 'Stop' : 'Run'")
      //-     button(v-if="modelTrainingSettings && isGlobalTrainingSettingEnabled" @click="onOffBtn(true)").btn-menu-bar.run-with-current-settings-btn
      //-       | Run with current settings

      //- ul.toolbar_list
      //-   li(v-tooltip:bottom="'Press to go to the Statistics view'")
      //-     button#tutorial_run-training-button.btn-menu-bar(type="button"
      //-       :class="{'disabled': !networkIsTrained , 'active': statisticsIsOpen && isOnModelToolPage()}"
      //-       @click="toModelStatistic"
      //-     )
      //-       | Go to statistics

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
        base-toggle.toggle(
          :value="modelWeightsActive"
          :disabled="!networkHasCheckpoint" 
          :onClick="toggleModelWeights")
          span.bold Weights

        base-toggle.toggle(
          :value="showModelPreviews" 
          :onClick="toggleModelPreviews")
          span.bold Preview
          
        sidebar-toggle-button.toggle
</template>

<script>
import { mapGetters, mapActions, mapMutations, mapState } from 'vuex';

import {goToLink, isEnvDataWizardEnabled} from '@/core/helpers.js';

import LayersToolbar            from '@/components/toolbar/workspace-toolbar-layers.vue';
import SidebarToggleButton      from '@/components/toolbar/sidebar-toggle-button.vue';

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
      showGlobalTrainingSettingsPopup:    state => state.globalPopup.showGlobalTrainingSettingsPopup.isOpen
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
      modelTrainingSettings:'mod_workspace/GET_modelTrainingSetting'
    }),
    kernelLabel() {
      if(this.statusLocalCore !== "online") {
        return "Kernel is not connected";
      } else {
        return "Kernel is connected";
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
      set_hideLayers:         'globalView/SET_hideLayers',
      GP_showCoreSideSettings:'globalView/GP_showCoreSideSettings',
    }),
    ...mapActions({
      popupConfirm:         'globalView/GP_confirmPopup',
      showInfoPopup:        'globalView/GP_infoPopup',
      removeTooltip:        'mod_tutorials/removeTooltip',
      set_netMode:          'mod_workspace/SET_netMode',
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
      this.setNextStep({currentStep:'tutorial-workspace-preview-toggle'});
      this.$store.dispatch('mod_workspace/TOGGLE_showModelPreviews');
    },
    toggleModelWeights() {
      if (!this.networkHasCheckpoint) { return; }
      this.$store.dispatch('mod_workspace/toggleModelWeightsState');

      // Should refactor this
      this.$store.dispatch('mod_workspace/UPDATE_all_previews');
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
                this.$store.commit('mod_workspace/update_network_meta', {key: 'hideStatistics', networkID: item.networkID, value: false});
                this.SET_openStatistics(true);
                this.set_chartRequests(item.networkID);
                })
          } else {
            const { statisticItemIndex } = this;
            
            if(statisticItemIndex !== null) {
              this.$store.dispatch("mod_workspace/setViewType", 'statistic');
              const item = this.workspaceModels[this.statisticItemIndex];
              this.$store.commit('mod_workspace/update_network_meta', {key: 'hideStatistics', networkID: item.networkID, value: false});
              this.SET_currentNetwork(statisticItemIndex);
              this.SET_openStatistics(true);
              this.SET_openTest(false);
            }
          }

        } else {
          const { statisticItemIndex } = this;
          if(statisticItemIndex !== null) {
            this.$store.dispatch("mod_workspace/setViewType", 'statistic');
            const item = this.workspaceModels[this.statisticItemIndex];
            this.$store.commit('mod_workspace/update_network_meta', {key: 'hideStatistics', networkID: item.networkID, value: false});
            this.SET_currentNetwork(statisticItemIndex)
              .then(() => {
                this.$router.push({name: 'app'});
                this.SET_openStatistics(true);
              });
          }
        }

        this.$nextTick(() => {
          if (!this.showNewModelPopup) {
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
    }
  },
}
</script>

<style lang="scss" scoped>
  
  .main_toolbar {
    display: flex;
    align-items: center;
    padding: 5px 29px 5px 0;
    
    background-color: $bg-toolbar-2;
    border-bottom: $border-1;
    position: relative;
    grid-area: toolbar;
    z-index: 10;
    border-radius: 4px 4px 0 0;
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
    margin-right: 32px;
    > li + li {
      margin-left: 20px;
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
      margin-left: 15px;
      margin-right: 15px;
    }

    > *:last-child {
      margin-left: 15px;
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
  .run-with-current-settings-btn {
    margin-left: 7px;
  }

  .toggle {
    font-size: 16px;
  }
</style>
