<template lang="pug">
  .net-element.js-clickout(tabindex="0"
    ref="rootBaseElement"
    :style="style"
    :id="dataEl.layerMeta.tutorialId"
    :class="classEl"

    @click="switchClickEvent($event)"
    @dblclick.stop.prevent="switchDblclick($event)"
    @contextmenu.stop.prevent="openContext"
    )
    .net-element_be-for-end(v-if="beForEnd") {{ beForEnd }}
    .net-element_btn(ref="BaseElement")
      slot

    .net-element_window(v-if="settingsIsOpen")
      slot(name="settings")

    .net-element_window.net-element_context-menu(v-if="contextIsOpen")
      slot(name="context")

</template>

<script>
import baseNetDrag        from '@/core/mixins/base-net-drag.js';
import baseNetPaintArrows from '@/core/mixins/base-net-paint-arrows.js';
import mousedownOutside   from '@/core/mixins/mousedown-outside.js'
import {mapGetters, mapActions}       from 'vuex';

export default {
  name: 'NetBaseElement',
  mixins: [baseNetDrag, baseNetPaintArrows, mousedownOutside],
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
  data() {
    return {
      contextIsOpen: false,
      settingsIsOpen: false,
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
  computed: {
    ...mapGetters({
      tutorialActiveAction: 'mod_tutorials/getActiveAction',
      isTraining:           'mod_workspace/GET_networkIsTraining',
      editIsOpen:           'mod_workspace/GET_networkIsOpen'
    }),
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
    statisticsIsOpen() {
      return this.$store.getters['mod_workspace/GET_statisticsIsOpen']
    },
    classEl() {
      return {
        'net-element--hide-layer': this.dataEl.layerMeta.displayNone,
        'net-element--active': this.isSelectedEl,
        'element--hidden': this.dataEl.layerMeta.isInvisible
      }
    }
  },
  watch: {
    statisticsIsOpen(newVal) {
      if(newVal) {
        this.deselect()
      }
    },
    isSelectedEl(newVal) {
      newVal
        ? this.mousedownOutsideBefore()
        : null
    },
  },
  methods: {
    ...mapActions({
      tutorialPointActivate: 'mod_tutorials/pointActivate',
    }),
    switchMousedownEvent(ev) {
      if (this.isLock) return;

      else if(this.networkMode === 'addArrow') {
        this.arrowStartPaint(ev)
      }
      else if(this.networkMode === 'edit' && this.editIsOpen) {
        this.setFocusEl(ev);
        this.bodyDown(ev)
      }
    },
    switchClickEvent(ev) {
      if (this.isLock) return;

      else if (!this.editIsOpen) {
        this.$store.commit('mod_statistics/CHANGE_selectElArr', this.dataEl)
      }
    },
    switchDblclick(event) {
      this.layerContainer
        ? this.openLayerContainer()
        : this.openSettings(event)
    },
    openLayerContainer() {
      this.$store.dispatch('mod_workspace/OPEN_container', this.dataEl)
    },
    openSettings(event) {
      this.hideAllWindow();
      if(this.networkMode === 'edit' && this.editIsOpen) {
        this.settingsIsOpen = true;
        this.$nextTick(()=> {this.tutorialPointActivate({way:'next', validation: this.tutorialSearchId(event)})})
      }
    },
    openContext() {
      this.hideAllWindow();
      if(this.networkMode === 'edit' && this.editIsOpen) {
        this.contextIsOpen = true;
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
    },
    deselect() {
      this.hideAllWindow();
      this.$store.dispatch('mod_workspace/SET_elementSelect', {id: this.currentId, setValue: false });
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
    z-index: 2;
    top: 0;
    left: 100%;
    padding-left: 10px;
  }
  .net-element_btn {
    margin: 0;
    padding: 0;
    background-color: transparent;
    .net-element--active & .btn {
      box-shadow: 0 0 20px #fff;
    }
  }
  .net-element_be-for-end {
    font-size: 1.2rem;
    position: absolute;
    top: -2.5rem;
    left: 50%;
    transform: translateX(-50%);
    white-space: nowrap;
    background-color: rgba($bg-workspace, .5);
  }
  .net-element--hide-layer {
    opacity: 0;
    visibility: hidden;
  }
</style>
