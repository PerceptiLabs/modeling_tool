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
    //this.$refs.rootBaseElement.addEventListener('mousedown', this.switchMousedownEvent);
    this.$refs.rootBaseElement.addEventListener('touchstart', this.switchMousedownEvent);
  },

  beforeDestroy() {
    //this.$refs.rootBaseElement.removeEventListener('mousedown', this.switchMousedownEvent);
    this.$refs.rootBaseElement.removeEventListener('touchstart', this.switchMousedownEvent);
    /*appMode*/
    this.$parent.$parent.$el.removeEventListener('mousemove', this.arrowMovePaint);
    this.$refs.rootBaseElement.removeEventListener('mouseup', this.Mix_paintArrow_arrowEndPaint);

    this.$parent.$parent.$el.removeEventListener('touchmove', this.arrowMovePaint, true);
    this.$refs.rootBaseElement.removeEventListener('touchend touchcancel', this.Mix_paintArrow_arrowEndPaint, true);
    this.$refs.rootBaseElement.removeEventListener('touchstart', this.Mix_paintArrow_arrowEndPaint, true);
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
      return this.dataEl.checkpoint && this.dataEl.checkpoint.length
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
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom;
    },
    // hotKeyPressEsc() {
    //   return this.$store.state.mod_events.globalPressKey.esc;
    // },
    // hotKeyPressDelete() {
    //   return this.$store.state.mod_events.globalPressKey.del
    // },
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
    '$store.state.mod_events.globalPressKey.esc': {
      handler() {
        if(!this.isTutorialMode) this.hideAllWindow();
      }
    },
    '$store.state.mod_events.globalPressKey.del': {
      handler() {
        if(this.editIsOpen
          && !this.settingsIsOpen
          && this.isSelectedEl
        ) {
          this.$store.dispatch('mod_workspace/DELETE_element');
        }
      }
    },
    // hotKeyPressDelete() {
    //   if(!this.settingsIsOpen) {
    //     console.log('hotKeyPressDelete()', this.settingsIsOpen);
    //     this.$store.dispatch('mod_workspace/DELETE_element');
    //   }
    // }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
      tutorialShowHideTooltip:  'mod_tutorials/showHideTooltip',
      setNetMode:               'mod_workspace/SET_netMode',
    }),
    startArrowPaint(ev) {
      document.addEventListener('mouseup', this.toEditMode);
      this.$store.dispatch('mod_workspace/SET_netMode', 'addArrow');
      this.Mix_paintArrow_arrowStartPaint(ev);
    },
    toEditMode() {
      this.$store.dispatch('mod_workspace/SET_netMode', 'edit');
      document.removeEventListener('mouseup', this.toEditMode);
    },
    switchMousedownEvent(ev) {
      if (this.isLock) return;
      //console.log('switchMousedownEvent', ev);
      if(this.networkMode === 'addArrow') this.Mix_paintArrow_arrowStartPaint(ev);

      if(this.networkMode === 'edit'
        && this.editIsOpen
        && ev.button === 0
      ) {
        this.setFocusEl(ev);
        this.bodyDown(ev)
      }
    },
    switchClickEvent(ev) {
      if (this.isLock) return;

      if (!this.editIsOpen
        && !this.layerContainer
      ) {
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
      if(!this.isTutorialMode) {
        this.hideAllWindow();
        if(!this.currentSelectedEl.length) {
          this.setFocusEl(event);
        }
        //this.calcWindowPosition();
        if(this.networkMode === 'edit' && this.editIsOpen) {
          this.contextIsOpen = true;
        }
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
      if(!this.isTutorialMode) this.hideAllWindow();
      this.$store.dispatch('mod_workspace/SET_elementSelect', {id: this.currentId, setValue: false });
      this.tutorialShowHideTooltip();
    },
    tutorialSearchId(event) {
      return event.target.tagName === 'I'
        ? event.target.parentNode.parentNode.parentNode.id
        : event.target.parentNode.parentNode.id
    }
  }
}
