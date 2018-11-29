<template lang="pug">
  .net-element.js-clickout(tabindex="0"
    ref="rootBaseElement"
    :style="style"
    :class="active ? 'active' : 'inactive'"
    @dblclick.stop.prevent="layerContainer ? $emit('dblcl') : openSettings()"
    @contextmenu.stop.prevent="openContext"
    @keyup.shift.delete="deleteEl()"
    )
    .net-element_btn
      slot

    .net-element_window(v-if="settingsIsOpen ")
      slot(name="settings")

    .net-element_window.net-element_context-menu(v-if="contextIsOpen")
      slot(name="context")

</template>

<script>
import baseNetDrag        from '@/core/mixins/base-net-drag.js';
import baseNetPaintArrows from '@/core/mixins/base-net-paint-arrows.js';
import clickOutside       from '@/core/mixins/click-outside.js'

export default {
  name: 'NetBaseElement',
  mixins: [baseNetDrag, baseNetPaintArrows, clickOutside],
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
    this.$refs.rootBaseElement.addEventListener('mousedown', this.switchEvent);
    this.$refs.rootBaseElement.addEventListener('touchstart', this.switchEvent);
  },

  beforeDestroy() {
    this.$refs.rootBaseElement.removeEventListener('mousedown', this.switchEvent);
    this.$refs.rootBaseElement.removeEventListener('touchstart', this.switchEvent);
    /*appMode*/
    this.$parent.$parent.$el.removeEventListener('mousemove', this.arrowMovePaint);
    this.$refs.rootBaseElement.removeEventListener('mouseup', this.arrowEndPaint);

    this.$parent.$parent.$el.removeEventListener('touchmove', this.arrowMovePaint, true);
    this.$refs.rootBaseElement.removeEventListener('touchend touchcancel', this.arrowEndPaint, true);
    this.$refs.rootBaseElement.removeEventListener('touchstart', this.arrowEndPaint, true);
    /*clickOutsideAction*/
    document.removeEventListener('click', this.clickOutside);
  },
  computed: {
    active() {
      return this.dataEl.el.meta.isSelected
    },
    appMode() {
      return this.$store.state.globalView.appMode
    },
    statisticsIsOpen() {
      return this.$store.state.globalView.statisticsIsOpen
    }
  },
  watch: {
    appMode(newVal) {
      if(newVal == 'addArrow') {
        this.$parent.$parent.$el.addEventListener('mousemove', this.arrowMovePaint);
        this.$refs.rootBaseElement.addEventListener('mouseup', this.arrowEndPaint);

        this.$parent.$parent.$el.addEventListener('touchmove', this.arrowMovePaint, true);
        this.$refs.rootBaseElement.addEventListener('touchend touchcancel', this.arrowEndPaint, true);
        this.$refs.rootBaseElement.addEventListener('touchstart', this.arrowEndPaint, true);
      }
      else {
        this.$parent.$parent.$el.removeEventListener('mousemove', this.arrowMovePaint);
        this.$refs.rootBaseElement.removeEventListener('mouseup', this.arrowEndPaint);

        this.$parent.$parent.$el.removeEventListener('touchmove', this.arrowMovePaint, true);
        this.$refs.rootBaseElement.removeEventListener('touchend touchcancel', this.arrowEndPaint, true);
        this.$refs.rootBaseElement.removeEventListener('touchstart', this.arrowEndPaint, true);
      }
    },
    statisticsIsOpen(newVal) {
      if(newVal) {
        this.deselect()
      }
    }
  },
  methods: {
    switchEvent(ev) {
      ev.stopPropagation();
      if (this.statisticsIsOpen) {
        this.$store.commit('mod_statistics/CHANGE_selectElArr', this.dataEl)
      }
      else if (this.isLock) {
        return
      }
      else if(this.appMode == 'edit') {
        this.setFocusEl(ev);
        this.bodyDown(ev)
      }
      else if (this.appMode == 'addArrow') {
        this.arrowStartPaint(ev)
      }
    },
    openSettings() {
      this.hideAllWindow();
      this.settingsIsOpen = true;
    },
    openContext() {
      this.hideAllWindow();
      this.contextIsOpen = true;
    },
    setFocusEl(ev) {
      if(ev.ctrlKey) {
        this.$store.commit('mod_workspace/SET_metaMultiSelect', { path: [this.dataEl.index], setValue: true });
      }
      else {
        this.ClickElementTracking = ev.target.closest('.js-clickout');
        document.addEventListener('click', this.clickOutside);
        this.$store.commit('mod_workspace/SET_metaSelect', { path: [this.dataEl.index], setValue: true });
      }
    },
    hideAllWindow() {
      this.settingsIsOpen = false;
      this.contextIsOpen = false;
    },
    clickOutsideAction() {
      if (!this.statisticsIsOpen) {
        this.deselect()
      }
    },
    deselect() {
      //console.log('deselect');
      this.hideAllWindow();
      this.$store.commit('mod_workspace/SET_metaSelect', { path: [this.dataEl.index], setValue: false });
    },
    deleteEl() {
      this.$store.dispatch('mod_workspace/DELETE_netElement')
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../../scss/base";
  .net-element_window {
    position: absolute;
    z-index: 2;
    left: 100%;
    top: 0;
    padding-left: 10px;
  }
  .net-element_btn {
    padding: 0;
    margin: 0;
    background-color: transparent;
    .active & .btn{
      box-shadow: 0 0 20px #fff;
    }
  }
</style>
