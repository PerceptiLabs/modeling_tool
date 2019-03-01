<template lang="pug">
  .net-element.js-clickout(tabindex="0"
    ref="rootBaseElement"
    :style="style"
    :class="active ? 'active' : 'inactive'"
    @click="switchClickEvent($event)"
    @dblclick.stop.prevent="layerContainer ? $emit('dblcl') : openSettings()"
    @contextmenu.stop.prevent="openContext"
    @keyup.46="deleteEl()"
    @keyup.93.8="deleteEl()"
    )
    .net-element_btn(ref="BaseElement")
      slot

    .net-element_window(v-if="settingsIsOpen ")
      slot(name="settings")

    .net-element_window.net-element_context-menu(v-if="contextIsOpen")
      slot(name="context")

</template>

<script>
import baseNetDrag        from '@/core/mixins/base-net-drag.js';
import baseNetPaintArrows from '@/core/mixins/base-net-paint-arrows.js';
import mousedownOutside   from '@/core/mixins/mousedown-outside.js'
import {mapActions}       from 'vuex';

export default {
  name: 'NetBaseElement',
  mixins: [baseNetDrag, baseNetPaintArrows, mousedownOutside],
  props: {
    layerContainer: {type: Boolean, default: false},
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
    active() {
      return this.dataEl.el.layerMeta.isSelected
    },
    networkMode() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.netMode
    },
    statisticsIsOpen() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openStatistics
    },
    testingIsOpen() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.openTest
    },
    isTraining() {
      return this.$store.getters['mod_workspace/GET_networkIsTraining']
    },
  },
  watch: {
    statisticsIsOpen(newVal) {
      if(newVal) {
        this.deselect()
      }
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    switchMousedownEvent(ev) {
      if (this.isLock) {
        return
      }
      if(this.networkMode === 'addArrow') {
        this.arrowStartPaint(ev)
      }
      else if(this.networkMode === 'edit') {
        this.setFocusEl(ev);
        this.bodyDown(ev)
      }
    },
    switchClickEvent(ev) {
      if (this.isLock) {
        return
      }
      else if (this.statisticsIsOpen || this.testingIsOpen) {
        this.$store.commit('mod_statistics/CHANGE_selectElArr', this.dataEl)
      }
    },
    openSettings() {
      setTimeout(()=>{this.tutorialPointActivate('next')}, 0) 
      this.hideAllWindow();
      if(this.networkMode === 'edit' && !this.isTraining) {
        this.settingsIsOpen = true;
      }
    },
    openContext() {
      this.hideAllWindow();
      if(this.networkMode === 'edit' && !this.isTraining) {
        this.contextIsOpen = true;
      }
    },
    setFocusEl(ev) {
      // if(ev.ctrlKey) {
      //   this.$store.dispatch('mod_workspace/SET_elementMultiSelect', { path: [this.dataEl.index], setValue: true });
      // }
      // else {
      this.MousedownElementTracking = ev.target.closest('.js-clickout');
      document.addEventListener('mousedown', this.mousedownOutside);
      this.$store.dispatch('mod_workspace/SET_elementSelect', { path: [this.dataEl.index], setValue: true });
      //}
    },
    hideAllWindow() {
      this.settingsIsOpen = false;
      this.contextIsOpen = false;
    },
    mousedownOutsideAction() {
      if (!this.statisticsIsOpen) {
        this.deselect()
      }
    },
    deselect() {
      this.hideAllWindow();
      this.$store.dispatch('mod_workspace/SET_elementSelect', { path: [this.dataEl.index], setValue: false });
    },
    deleteEl() {
      if(!(this.contextIsOpen || this.settingsIsOpen)) {
        this.$store.dispatch('mod_workspace/DELETE_element')
      }
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
    .active & .btn {
      box-shadow: 0 0 20px #fff;
    }
  }
</style>
