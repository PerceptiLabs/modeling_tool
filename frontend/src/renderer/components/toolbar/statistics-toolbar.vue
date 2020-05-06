<template lang="pug">
  aside.page_toolbar(v-if="statisticsIsOpen")
    .toolbar-section
      ul.toolbar-button-group
        li.toolbar-button(@click="onPauseClick")
          i.icon.icon-player-pause

        li.toolbar-button(@click="onStopClick")
          i.icon.icon-stop2

        li.toolbar-button(@click="onSkipClick")

          i.icon.icon-player-next

    .toolbar-section
      span training
    .toolbar-section
      //- used for easily centering the training bar
      
    
</template>

<script>
import { mapGetters, mapActions, mapMutations } from 'vuex';
import { googleAnalytics }                      from '@/core/analytics';
import { trainingElements, deepLearnElements }  from '@/core/constants.js';
import { goToLink }                             from '@/core/helpers.js'

export default {
  name: 'StatisticsToolbar',
  components: {},
  data() {
    return {}
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
  },
  methods: {
    ...mapActions({
      pauseTraining:        'mod_api/API_pauseTraining',
      stopTraining:         'mod_api/API_stopTraining',
      skipValidTraining:    'mod_api/API_skipValidTraining',
    }),
    onPauseClick() {
      this.pauseTraining();
    },
    onStopClick() {
      this.stopTraining();
    },
    onSkipClick() {
      this.skipValidTraining();
    },
  }
}
</script>

<style lang="scss" scoped>
@import "../../scss/base";

.page_toolbar {
  display: flex;
  align-items: center;
  padding: 5px 2rem 5px 0;
  background-color: $bg-toolbar-2;
  border: 1px solid rgba(97, 133, 238, 0.2);
  border-radius: 2px 2px 0px 0px;
  position: relative;
  grid-area: toolbar;
  z-index: 2;
  height: $h-toolbar;
}

.toolbar-section  {
  flex: 1;
  display: flex;
  justify-content: center;

  &:first-of-type {
    justify-content: flex-start;
  }

  &:last-of-type() {
    justify-content: flex-end;
  }

  &:first-child > div {
    margin-right: auto;
  } 

  &:last-child > div {
    margin-left: auto;
  } 
}

.toolbar-button-group {
  padding-left:2rem;
  list-style: none;
  display: flex;

  .toolbar-button {
    height: 2.1rem;
    width: 2.1rem;
    border: 1px solid #5E6F9F;
    box-sizing: border-box;
    border-radius: 2px;

    display: flex;
    justify-content: center;
    align-items: center;

    i {
      color: #B6C7FB;
      height: 1rem;
    }

    & + .toolbar-button {
      margin-left: 0.5rem;
      cursor: pointer;
    }
  }
}
</style>
