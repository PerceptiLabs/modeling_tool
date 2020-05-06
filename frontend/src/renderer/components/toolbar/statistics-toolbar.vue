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
      model-status(
        :statusData="currentNetwork.networkMeta.coreStatus"
      )
    .toolbar-section
      //- used for easily centering the training bar
      
    
</template>

<script>

import ModelStatus  from '@/components/different/model-status.vue';

import { mapGetters, mapActions, mapMutations } from 'vuex';

export default {
  name: 'StatisticsToolbar',
  components: { ModelStatus },
  data() {
    return {}
  },
  computed: {
    ...mapGetters({
      statusNetworkCore:    'mod_workspace/GET_networkCoreStatus',
      statisticsIsOpen:     'mod_workspace/GET_statisticsIsOpen',
      currentNetwork:       'mod_workspace/GET_currentNetwork',
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
      height: 0.9rem;
      font-size: 1rem;
    }

    & + .toolbar-button {
      margin-left: 0.5rem;
      cursor: pointer;
    }
  }
}
</style>
