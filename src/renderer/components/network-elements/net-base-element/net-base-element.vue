<template lang="pug">
  .net-element.js-clickout(tabindex="0"
    ref="rootBaseElement"
    :style="style"
    :id="dataEl.layerMeta.tutorialId"
    :class="classEl"

    @click="switchClickEvent($event)"
    @dblclick.stop.prevent="switchDblclick($event)"
    @contextmenu.stop.prevent="openContext($event)"
    )
    .net-element_be-for-end(v-if="beForEnd") {{ beForEnd }}
    .net-element_checkpoint-icon(v-if="showCheckpoint") t
    .net-element_btn(ref="BaseElement")
      slot
    //-
    .net-element_window(
      v-if="settingsIsOpen"
      :class="classElWindow"
      :style="styleElWindow"
      ref="elementSettings"
      )
      slot(name="settings")

    .net-element_window.net-element_context-menu(
      v-if="contextIsOpen"
      :class="classElWindow"
      :style="styleElWindow"
      )
      context-menu(
        :data-el="dataEl"
        @open-settings.stop="switchDblclick($event)"
        )

</template>

<script>
import ContextMenu        from '@/components/network-elements/net-context-menu/net-context-menu.vue';

import baseNetDrag        from '@/core/mixins/base-net-drag.js';
import baseNetPaintArrows from '@/core/mixins/base-net-paint-arrows.js';
import mousedownOutside   from '@/core/mixins/mousedown-outside.js'
import {mapGetters, mapActions}       from 'vuex';

export default {
  name: 'NetBaseElement',
  mixins: [baseNetDrag, baseNetPaintArrows, mousedownOutside],
  components: { ContextMenu },
  props: {
    layerContainer: {
      type: Boolean,
      default: false
    },
    dataEl: {
      type: Object,
      default: function () {
        return {}
      }
    },
  },
  provide () {
    return {
      hideAllWindow: this.hideAllWindow
    }
  },
  mounted() {
    this.$refs.rootBaseElement.addEventListener('mousedown', this.switchMousedownEvent);
    this.$refs.rootBaseElement.addEventListener('touchstart', this.switchMousedownEvent);
  },

  beforeDestroy() {
    this.$refs.rootBaseElement.removeEventListener('mousedown', this.switchMousedownEvent);
    this.$refs.rootBaseElement.removeEventListener('touchstart', this.switchMousedownEvent);
    /*appMode*/
    this.$parent.$parent.$el.removeEventListener('mousemove', this.arrowMovePaint);
    this.$refs.rootBaseElement.removeEventListener('mouseup', this.arrowEndPaint);

    this.$parent.$parent.$el.removeEventListener('touchmove', this.arrowMovePaint, true);
    this.$refs.rootBaseElement.removeEventListener('touchend touchcancel', this.arrowEndPaint, true);
    this.$refs.rootBaseElement.removeEventListener('touchstart', this.arrowEndPaint, true);
    /*clickOutsideAction*/
    document.removeEventListener('mousedown', this.mousedownOutside);
  },
  data() {
    return {
      contextIsOpen: false,
      settingsIsOpen: false,
      openWinPosition: {
        left: false,
        top: false,
        offset: 0
      }
    }
  },
  computed: {
    ...mapGetters({
      tutorialActiveAction: 'mod_tutorials/getActiveAction',
      isTutorialMode:       'mod_tutorials/getIstutorialMode',
      isTraining:           'mod_workspace/GET_networkIsTraining',
      editIsOpen:           'mod_workspace/GET_networkIsOpen',
      currentSelectedEl:    'mod_workspace/GET_currentSelectedEl',
      statisticsIsOpen:     'mod_workspace/GET_statisticsIsOpen',
    }),
    showCheckpoint() {
      return this.dataEl.checkpoint && this.dataEl.checkpoint.length ? true : false
    },
    currentId() {
      return this.dataEl.layerId
    },
    beForEnd() {
      //console.log('NetBaseElement beForEnd', this.dataEl.el.layerMeta);
      return this.dataEl.layerMeta.OutputDim
    },
    isSelectedEl() {
      return this.dataEl.layerMeta.isSelected
    },
    networkMode() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.netMode
    },
    wsZoom() {
      return  this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom;
    },
    classEl() {
      return {
        'net-element--active': this.isSelectedEl,
        'element--hidden': this.dataEl.layerMeta.isInvisible
      }
    },
    classElWindow() {
      return {
        'net-element_window--left': this.openWinPosition.left,
        'net-element_window--top': this.openWinPosition.top
      }
    },
    styleElWindow() {
      let style = {zoom: `${(100 / (this.wsZoom * 100)) * 100}%`};
      let offsetWin = this.openWinPosition.offset;
      if(offsetWin !== 0) {
        this.openWinPosition.top
          ? style.bottom = `-${offsetWin}px`
          : style.top = `-${offsetWin}px`
      }
      return style
    },
  },
  watch: {
    isSelectedEl(newVal) {
      newVal
        ? this.mousedownOutsideBefore()
        : null
    },
  },
  methods: {
    ...mapActions({
      tutorialPointActivate: 'mod_tutorials/pointActivate',
      tutorialShowHideTooltip: 'mod_tutorials/showHideTooltip',
    }),
    switchMousedownEvent(ev) {
      if (this.isLock) return;
      //console.log('switchMousedownEvent', ev);
      if(this.networkMode === 'addArrow') this.arrowStartPaint(ev);

      if(this.networkMode === 'edit' && this.editIsOpen && ev.button === 0) {
        this.setFocusEl(ev);
        this.bodyDown(ev)
      }
    },
    switchClickEvent(ev) {
      if (this.isLock) return;

      if (!this.editIsOpen && !this.layerContainer) {
        this.$store.commit('mod_statistics/CHANGE_selectElArr', this.dataEl)
      }
    },
    switchDblclick(event) {
      if (this.isLock) return;
      if(this.networkMode !== 'edit') {
        this.$store.dispatch('mod_workspace/SET_netMode', 'edit');
        this.setFocusEl(event);
      }
      this.layerContainer
        ? this.openLayerContainer()
        : this.openSettings(event)
    },
    openLayerContainer() {
      this.$emit('open-container')
    },
    openSettings(event) {
      this.tutorialShowHideTooltip();
      this.hideAllWindow();
      if(!this.editIsOpen) return;
      this.settingsIsOpen = true;

      this.$nextTick(() => {
        this.calcWindowPosition();
        this.tutorialPointActivate({
          way: 'next',
          validation: this.tutorialSearchId(event)
        })
      })
    },
    openContext(event) {

      this.hideAllWindow();
      if(!this.currentSelectedEl.length) {
        this.setFocusEl(event);
      }
      //this.calcWindowPosition();
      if(this.networkMode === 'edit' && this.editIsOpen) {
        this.contextIsOpen = true;
      }
    },
    calcWindowPosition(el) {
      let windowWs = document.querySelector('.js-info-section_main');
      let windowWsWidth = windowWs.clientWidth/this.wsZoom;
      let windowWsHeight = windowWs.clientHeight/this.wsZoom;
      let elementSettingsHeight = this.$refs.elementSettings.clientHeight/this.wsZoom;
      let layerHeight = this.$refs.rootBaseElement.clientHeight;
      let layerTop = this.dataEl.layerMeta.position.top;
      let winCenterWidth = windowWs.scrollLeft + (windowWsWidth - layerHeight)/2;
      let winCenterHeight = windowWs.scrollTop + (windowWsHeight - layerHeight)/2;

      winCenterWidth < this.dataEl.layerMeta.position.left
        ? this.openWinPosition.left = true
        : this.openWinPosition.left = false;
      winCenterHeight < layerTop
        ? this.openWinPosition.top = true
        : this.openWinPosition.top = false;

      if(this.openWinPosition.top) {
        if(layerTop < elementSettingsHeight) {
          this.openWinPosition.offset = (elementSettingsHeight - layerTop - layerHeight + 10)*this.wsZoom
        }
      }
      else {
        if((windowWsHeight - layerTop) < elementSettingsHeight) {
          this.openWinPosition.offset = (elementSettingsHeight - (windowWsHeight - layerTop) + 10)*this.wsZoom
        }
      }
    },
    setFocusEl(ev) {
      ev.ctrlKey
        ? this.$store.dispatch('mod_workspace/SET_elementMultiSelect', {id: this.currentId, setValue: true })
        : this.$store.dispatch('mod_workspace/SET_elementSelect',      {id: this.currentId, setValue: true })
    },
    mousedownOutsideBefore() {
      this.MousedownElementTracking = this.$refs.rootBaseElement;
      document.addEventListener('mousedown', this.mousedownOutside);
    },
    mousedownOutsideAction() {
      if (this.editIsOpen) this.deselect()
    },
    hideAllWindow() {
      this.settingsIsOpen = false;
      this.contextIsOpen = false;
      this.openWinPosition = {
        left: false,
        top: false,
        offset: 0
      }
    },
    deselect() {
      this.hideAllWindow();
      this.$store.dispatch('mod_workspace/SET_elementSelect', {id: this.currentId, setValue: false });
      this.tutorialShowHideTooltip();
    },
    deleteEl() {
      if(this.editIsOpen) {
        this.$store.dispatch('mod_workspace/DELETE_element');
        this.$store.dispatch('mod_api/API_getOutputDim');
      }
    },
    tutorialSearchId(event) {
       return event.target.tagName === 'I'
         ? event.target.parentNode.parentNode.parentNode.id
         : event.target.parentNode.parentNode.id
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../../scss/base";

  .net-element_window {
    position: absolute;
    z-index: 4;
    top: 0;
    left: 100%;
    padding-left: 10px;
    padding-right: 10px;
    &.net-element_window--left {
      left: auto;
      right: 100%;
    }
    &.net-element_window--top {
      top: auto;
      bottom: 0;
    }
  }
  .net-element_btn {
    position: relative;
    z-index: 3;
    margin: 0;
    padding: 0;
    background-color: transparent;
    box-shadow: $layer-shad;
    .net-element--active & .btn {
      box-shadow: 0 0 20px #fff;
    }
  }
  .net-element_be-for-end {
    font-size: 1.2rem;
    position: absolute;
    top: -20px; //zoom need px!
    left: 50%;
    z-index: 2;
    transform: translateX(-50%);
    white-space: nowrap;
    background-color: rgba($bg-workspace, .5);
  }
  .net-element_checkpoint-icon {
    position: absolute;
    font-size: 1.4rem;
    top: 2px;
    right: 7px;
    z-index: 4;
  }
  .net-element--hide-layer {
    opacity: 0;
    visibility: hidden;
  }
</style>
