<template lang="pug">
  aside.page_toolbar
    .toggle-wrap(:class="{'hide-layers': !hideLayers}")
      button.btn.btn--toolbar(type="button" @click="toggleLayers()")
        i.icon.icon-hide-top

    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button"
          :disabled="statisticsIsOpen"
          :class="{'active': networkMode === 'edit'}"
          id="tutorial_pointer"
          v-tooltip:bottom="'Edit'"
          @click="setNetMode('edit', 'tutorial_pointer')"
        )
          i.icon.icon-select

      li.toolbar_list-arrow-wrap(
        :class="{'disable-hover': statisticsIsOpen}"
        v-tooltip:bottom="'Arrow'"
      )
        button.btn.btn--toolbar(type="button"
          :disabled="statisticsIsOpen"
          :class="{'active': networkMode === 'addArrow'}"
          id="tutorial_list-arrow"
          @click="setArrowType(arrowList[0].arrowType)"
        )
          i.icon(:class="arrowList[0].iconClass")
        ul.toolbar_list-arrow
          li(
            v-for="(arrow, index) in arrowList"
            :key="index"
            )
            button.btn.btn--toolbar(type="button"
              @click="setArrowType(arrow.arrowType, index, 'tutorial_list-arrow')"
            )
              i.icon(:class="arrow.iconClass")

    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button"
          disabled="disabled"
          v-tooltip:bottom="'Prev step'"
        )
          i.icon.icon-step-prev
      li
        button.btn.btn--toolbar(type="button"
          disabled="disabled"
          v-tooltip:bottom="'Next step'"
        )
          i.icon.icon-step-next
    ul.toolbar_list
      li(:class="{'tutorial-active': activeStepStoryboard === 4}")
        button.btn.btn--toolbar.bg-primary(type="button"
          :disabled="statusLocalCore === 'offline'"
          :class="statusStartBtn"
          v-tooltip:bottom="'Run/Stop'"
          @click="onOffBtn()"
          class="run-button"
          id="tutorial_run-training-button"
        )
          i.icon.icon-on-off
          span(v-html="statusNetworkCore === 'Training' || statusNetworkCore == 'Paused' ? 'Stop' : 'Run'")
      li
        button.btn.btn--toolbar(type="button"
          :class="{'active': statusNetworkCore === 'Paused'}"
          :disabled="!isTraining"
          class="tutorial-relative"
          id="tutorial_pause-training"
          v-tooltip:bottom="'Pause'"
          @click="trainPause()"
        )
          i.icon.icon-pause
      li
        button.btn.btn--toolbar(type="button"
          :disabled="statusNetworkCore !== 'Validation'"
          v-tooltip:bottom="'Skip'"
          @click="skipValid()"
        )
          i.icon.icon-next
    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button"
          disabled="disabled"
          v-tooltip:bottom="'Repeat'"
        )
          i.icon.icon-repeat
      li
        button.btn.btn--toolbar(type="button"
          disabled="disabled"
          v-tooltip:bottom="'Box'"
        )
          i.icon.icon-box

    .toolbar_settings
      //span.text-primary.middle-text(v-html="statusTestText")
      //- button.btn.btn--primary(type="button" disabled="disabled"
      //-   v-if="statusNetworkCore == 'Finished'"
      //-   )
      //-   span Run test
      //-   i.icon.icon-circle-o
      span.text-primary.middle-text(v-html="statusTrainingText")
      //- button.btn.btn--dark-blue-rev(type="button" disabled="disabled"
      //-   @click="openStatistics"
      //-   )
      //-   span Layer Mode
      //-   i.icon.icon-ellipse

      tutorial-instructions
</template>

<script>
//import configApp    from '@/core/globalSettings.js'
import {trainingElements, deepLearnElements}  from '@/core/constants.js'
import TutorialInstructions                   from '@/components/tutorial/tutorial-instructions.vue'
import { mapGetters, mapActions }             from 'vuex';

//const {ipcRenderer} = require('electron')
export default {
  name: 'TheToolbar',
  components: {
    TutorialInstructions
  },
  data() {
    return {
      x: null,
      y: null,
      arrowList: [
        {
          iconClass: 'icon-layer-arrow1',
          arrowType: 'solid'
        },
        // {
        //   iconClass: 'icon-layer-arrow2',
        //   arrowType: 'dash2'
        // },
        // {
        //   iconClass: 'icon-layer-arrow3',
        //   arrowType: 'dash1'
        // }
      ]
    }
  },
  computed: {
    ...mapGetters({
      tutorialActiveAction:    'mod_tutorials/getActiveAction',
    }),
    statusStartBtn() {
      return {
        'bg-error':   this.statusNetworkCore == 'Training' || this.statusNetworkCore == 'Validation',
        'bg-warning': this.statusNetworkCore == 'Paused',
        'bg-success': this.statusNetworkCore == 'Finished',
      }
    },
    statusTrainingText() {
      switch (this.statusNetworkCore) {
        case 'Training':
        case 'Validation':
          return '<i class="icon icon-repeat animation-loader"></i> Training';
          break;
        case 'Paused':
          return 'Training paused';
          break;
        case 'Finished':
          return 'Training completed';
          break;
      }
    },
    statusTestText() {
      switch (this.statusNetworkCore) {
        case 'Training':
        case 'Validation':
          return '<i class="icon icon-repeat animation-loader"></i> Test running';
          break;
        case 'Paused':
          return '<i class="icon icon-notification"></i> Test completed';
          break;
      }
    },
    isTraining() {
      return this.$store.getters['mod_workspace/GET_networkIsTraining']
    },
    hideLayers () {
      return this.$store.state.globalView.hideLayers
    },
    currentElList() {
      return this.$store.getters['mod_workspace/GET_currentNetworkElementList']
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
    statusNetworkCore() {
      return this.$store.getters['mod_workspace/GET_networkCoreStatus']
    },
    statisticsIsOpen() {
      return this.currentNetMeta.openStatistics
    },
    tutorialRunButtonActive() {
      return this.$store.state.mod_tutorials.runButtonsActive
    },
    activeStepStoryboard() {
      return this.$store.state.mod_tutorials.activeStepStoryboard
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    onOffBtn() {
      if(this.isTraining){
        this.trainStop()
      }
      else this.trainStart()
      setTimeout(()=>{this.tutorialPointActivate({way:'next', validation: 'tutorial_run-training-button'})}, 0)
    },
    trainStart() {
      let valid = this.validateNetwork();
      if (!valid) {
        return
      }
      this.$store.commit('globalView/GP_showNetGlobalSet', true);

      //if show GlobalSet once
      // if(this.networkSettings.isEmpty) {
      //   this.$store.commit('globalView/SET_showGlobalSet', true);
      // }
      // else {
      //   this.$store.commit('globalView/SET_showCoreSideSettings', true);
      // }
    },
    trainStop() {
      this.$store.dispatch('mod_api/API_stopTraining');
    },
    trainPause() {
      this.$store.dispatch('mod_api/API_pauseTraining');
      this.tutorialPointActivate({way:'next', validation: 'tutorial_pause-training'})
    },
    skipValid() {
      this.$store.dispatch('mod_api/API_skipValidTraining');
    },
    validateNetwork() {
      let net = this.currentElList;
      let typeData = net.find((element)=> element.layerType === 'Data');
      if(typeData === undefined) {
        this.$store.commit('globalView/GP_infoPopup', 'Data element missing');
        return false
      }

      let typeTraining = net.find((element)=> element.layerType === 'Training');
      if(typeTraining === undefined) {
        this.$store.commit('globalView/GP_infoPopup', 'Classic Machine Learning or Training element missing');
        return false
      }

      let trainingIncluded = net.find(element => trainingElements.includes(element.componentName));
      let deepLearnIncluded = true;
      if (trainingIncluded) {
        deepLearnIncluded = net.find(element => deepLearnElements.includes(element.componentName));
      }
      if(deepLearnIncluded === undefined) {
        this.$store.commit('globalView/GP_infoPopup', 'If you use the Training elements, you must use the Deep Learn elements');
        return false
      }

      return true;
    },
    toggleLayers () {
      this.$store.commit('globalView/SET_hideLayers', !this.hideLayers)
    },
    setArrowType(type, index, tutorial_id) {
      this.setNetMode('addArrow');
      this.$store.commit('mod_workspace/SET_arrowType', {type, store: this.$store});
      let selectArray = this.arrowList.splice(index, 1);
      this.arrowList.unshift(selectArray[0]);
      this.tutorialPointActivate({way:'next', validation: tutorial_id})
    },
    setNetMode(type, tutorial_id) {
      this.$store.dispatch('mod_workspace/SET_netMode', type)
      this.tutorialPointActivate({way:'next', validation: tutorial_id})
    },
    openStatistics() {
      //this.$store.commit('mod_workspace/SET_openStatistics', true)
    },
  }
}
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  .page_toolbar {
    //z-index: 1;
    display: flex;
    align-items: center;
    padding: 5px .5em 5px 0;
    background-color: $bg-toolbar;
    position: relative;
    grid-area: toolbar;
  }
  .toggle-wrap {
    width: $w-layersbar;
    text-align: center;
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
    border-left: 1px solid $toolbar-border;
    > li + li {
      margin-left: .3571rem;
    }
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
      /*> .btn {*/
        /*//background-color: $bg-workspace-2;*/
      /*}*/
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
      margin-left: 1rem;
    }
  }
  #tutorial_pointer {
    position: relative;
  }
</style>
