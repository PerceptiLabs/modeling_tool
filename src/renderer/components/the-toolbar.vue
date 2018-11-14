<template lang="pug">
  aside.page_toolbar
    .toggle-wrap(:class="{'hide-layers': !hideLayers}")
      button.btn.btn--toolbar(type="button" @click="toggleLayers()")
        i.icon.icon-hide-top

    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button"
          :disabled="appMode == 'training'"
          :class="{'active': appMode == 'edit'}"
          @click="setAppMode('edit')"
        )
          i.icon.icon-select
      li.toolbar_list-arrow-wrap(
        :class="{'disable-hover': appMode == 'training'}"
      )
        button.btn.btn--toolbar(type="button"
          :disabled="appMode == 'training'"
          :class="{'active': appMode == 'addArrow'}"
          @click="setArrowType(arrowList[0].arrowType)"
        )
          i.icon(:class="arrowList[0].iconClass")
        ul.toolbar_list-arrow
          li(
            v-for="(arrow, index) in arrowList"
            :key="index")
            button.btn.btn--toolbar(type="button"
            @click="setArrowType(arrow.arrowType, index)"
            )
              i.icon(:class="arrow.iconClass")

    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-step-prev
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-step-next
    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button"
          :disabled="appMode == 'training'"
          :class="statusStartBtn"
          @click="trainStart()"
        )
          i.icon.icon-on-off
      li
        button.btn.btn--toolbar(type="button"
          :class="{'active': appMode == 'learn-pause'}"
          @click="trainPause()"
        )
          i.icon.icon-pause
      li
        button.btn.btn--toolbar(type="button"
          @click="trainStop()"
        )
          i.icon.icon-next
    ul.toolbar_list
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-repeat
      li
        button.btn.btn--toolbar(type="button")
          i.icon.icon-box

    .toolbar_settings
      span.text-primary.middle-text(v-html="statusTestText")
      button.btn.btn--primary(type="button"
        v-if="currentGlobalNet.canTestStatistics"
        @click="testStart"
      )
        span Run test
        i.icon.icon-circle-o
      span.text-primary.middle-text(v-html="statusTrainingText")
      button.btn.btn--dark-blue-rev(type="button"
        @click="openStatistics"
        )
        span Layer Mode
        i.icon.icon-ellipse
    .test-api
      button(type="button" @click="sendMain()").btn send
    //.test-api
      span.big-text Dev Mode:
        span.text-error  {{ devMode }}
      span.big-text Version:
        span.text-error  {{ versionApi }}
      input.text-error.big-text(v-model="x")
      span.big-text +
      input.text-error.big-text(v-model="y")
      button.btn.btn--settings(type="button" @click="calcPY") Calc
      span.big-text =
      span.big-text {{ resultSym }}

</template>

<script>
import configApp    from '@/core/globalSettings.js'
import {trainingElements, deepLearnElements}  from '@/core/helpers.js'

//const {ipcRenderer} = require('electron')
export default {
  name: 'TheToolbar',
  data() {
    return {
      x: null,
      y: null,
      arrowList: [
        {
          iconClass: 'icon-layer-arrow1',
          arrowType: 'solid'
        }, {
          iconClass: 'icon-layer-arrow2',
          arrowType: 'dash2'
        }, {
          iconClass: 'icon-layer-arrow3',
          arrowType: 'dash1'
        }
      ]
    }
  },
  mounted() {
    // ipcRenderer.on('asynchronous-reply', (event, arg) => {
    //   console.log(arg);
    // })
  },
  computed: {
    statusStartBtn() {
      return {
        'text-error':   this.appMode == 'training',
        'text-warning': this.appMode == 'training-pause',
        'text-success': this.appMode == 'training-done',
      }
    },
    statusTrainingText() {
      switch (this.appMode) {
        case 'training':
          return '<i class="icon icon-repeat animation-loader"></i> Training';
          break;
        case 'training-pause':
          return 'Training pause';
          break;
        case 'training-done':
          return 'Training completed';
          break;
      }
    },
    statusTestText() {
      switch (this.appMode) {
        case 'testing':
          return '<i class="icon icon-repeat animation-loader"></i> Test running';
          break;
        case 'testing-done':
          return '<i class="icon icon-notification"></i> Test completed';
          break;
      }
    },
    hideLayers () {
      return this.$store.state.globalView.hideLayers
    },
    resultSym() {
      return this.$store.state.mod_api.symPY
    },
    versionApi() {
      return configApp.version
    },
    devMode() {
      return configApp.developMode
    },
    appMode() {
      return this.$store.state.globalView.appMode
    },
    networkSettings() {
      return this.$store.getters['mod_workspace/currentNetworkSettings']
    },
    currentNet() {
      return this.$store.getters['mod_workspace/currentNetworkNet']
    },
    currentGlobalNet() {
      return this.$store.getters['mod_workspace/currentNetwork']
    }
  },
  methods: {
    sendMain() {
      ipcRenderer.send('asynchronous-message', 'ping')
    },
    trainStart() {
      let valid = this.validateNetwork();
      if (!valid) {
        return
      }
      if(this.networkSettings.isEmpty) {
        this.$store.commit('globalView/SET_showGlobalSet', true);
      }
      else {
        this.$store.commit('globalView/SET_showCoreSideSettings', true);
      }
    },
    trainPause() {
      this.setAppMode('training-pause')
    },
    trainStop() {
      this.setAppMode('training-done')
    },
    validateNetwork() {
      let net = this.currentNet;
      let typeData = net.find((element)=> element.layerType === 'Data');
      if(typeData === undefined) {
        this.$store.commit('globalView/SET_infoPopup', 'Date element missing');
        return false
      }

      let typeTraining = net.find((element)=> element.layerType === 'Training');
      if(typeTraining === undefined) {
        this.$store.commit('globalView/SET_infoPopup', 'Classic Machine Learning or Training element missing');
        return false
      }

      let trainingIncluded = net.find(element => trainingElements.includes(element.componentName));
      let deepLearnIncluded = true;
      if (trainingIncluded) {
        deepLearnIncluded = net.find(element => deepLearnElements.includes(element.componentName));
      }
      if(deepLearnIncluded === undefined) {
        this.$store.commit('globalView/SET_infoPopup', 'If you use the Training elements, you must use the Deep Learn elements');
        return false
      }

      return true;
    },
    toggleLayers () {
      this.$store.commit('globalView/SET_hideLayers', !this.hideLayers)
    },
    PY() {
      this.$store.dispatch('mod_pythonAPI/PY_console');
    },
    calcPY() {
      let x = +this.x;
      let y = +this.y;
      //this.$store.dispatch('mod_pythonAPI/PY_text', {x, y});
      this.$store.dispatch('mod_api/PY_func', {x, y});
    },
    setArrowType(type, index) {
      this.setAppMode('addArrow');
      this.$store.commit('mod_workspace/SET_arrowType', {type, store: this.$store});
      let selectArray = this.arrowList.splice(index, 1);
      this.arrowList.unshift(selectArray[0]);
    },
    setAppMode(type) {
      this.$store.commit('globalView/SET_appMode', type)
    },
    openStatistics() {
      this.$store.commit('globalView/SET_showStatistics', true)
    },
    testStart() {
      this.setAppMode('testing');
    },

    /*test load*/

  }
}
</script>

<style lang="scss" scoped>
  @import "../scss/base";
  .page_toolbar {
    grid-area: toolbar;
    background-color: $bg-toolbar;
    padding: 5px .5em 5px 0;
    //height: $h-toolbar;
    //font-size: 11px;
    display: flex;
    align-items: center;
  }
  .toggle-wrap {
    width: $w-layersbar;
    text-align: center;
    .btn--toolbar {
      @include multi-transition(transform);
      transform: rotate(0);
      margin: auto;
    }
    &.hide-layers {
      .btn--toolbar {
        transform: rotateX(-180deg);
      }
    }
  }
  .toolbar_list {
    padding: 0 .7143rem;
    margin: 0;
    list-style: none;
    display: flex;
    align-items: center;
    border-left: 1px solid $toolbar-border;
    > li + li {
      margin-left: .3571rem;
    }
  }
  .toolbar_list-arrow-wrap {
    position: relative;
    > .btn {
      //background-color: $bg-toolbar;
      position: relative;
    }
    &:hover {
      > .btn {
        //background-color: $bg-workspace-2;
      }
      .toolbar_list-arrow {
        max-height: 7.5rem;
        opacity: 1;
      }
    }
    &.disable-hover:hover {
      .toolbar_list-arrow {
        max-height: 0;
        opacity: 0;
      }
    }
  }
  .toolbar_list-arrow {
    @include multi-transition(max-height, opacity);
    padding: 0;
    margin: 0;
    list-style: none;
    position: absolute;
    top: 0;
    left: 0;
    opacity: 0;
    max-height: 0;
    overflow: hidden;
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

  /*.test-api {*/
    /*display: flex;*/
    /*align-items: center;*/
    /*font-weight: bold;*/
    /*> * {*/
      /*margin: 0 .5em;*/
    /*}*/
    /*input {*/
      /*width: 5em;*/
    /*}*/
    /*span span {*/
      /*font-weight: normal;*/
    /*}*/
  /*}*/
</style>
