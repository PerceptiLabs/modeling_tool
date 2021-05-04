import ContextMenu        from '@/components/network-elements/net-context-menu/net-context-menu.vue';

import baseNetDrag        from '@/core/mixins/base-net-drag.js';
import baseNetPaintArrows from '@/core/mixins/base-net-paint-arrows.js';
import mousedownOutside   from '@/core/mixins/mousedown-outside.js'
import SettingsPreview  from "@/components/network-elements/elements-settings/setting-preview.vue";

import {mapGetters, mapActions}       from 'vuex';
import {calcLayerPosition, deepCloneNetwork} from '@/core/helpers.js'
import { SHIFT_HOLDING_CONNECT_COMPONENT_MAX_DISTANCE } from '@/core/constants';
export default {
  name: 'NetBaseElement',
  mixins: [baseNetDrag, baseNetPaintArrows, mousedownOutside],
  components: { ContextMenu, SettingsPreview },
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
    document.removeEventListener('click', this.hideAllWindow, true);
    document.removeEventListener('contextmenu', this.hideAllWindow, true);
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
      isTutorialMode:       'mod_tutorials/getIsTutorialMode',
      isTraining:           'mod_workspace/GET_networkIsTraining',
      editIsOpen:           'mod_workspace/GET_networkIsOpen',
      currentSelectedEl:    'mod_workspace/GET_currentSelectedEl',
      statisticsIsOpen:     'mod_workspace/GET_statisticsIsOpen',
      modAddComponentState: 'mod_addComponent/GET_mod_addComponentState',
      networkElmentPositions: 'mod_workspace/GET_networkElmentPositions'
    }),
    showDotsArrow() {
      return this.editIsOpen && !this.settingsIsOpen && !this.contextIsOpen
    },
    showCheckpoint() {
      return this.dataEl.isTrained;
    },
    currentId() {
      return this.dataEl.layerId
    },
    beForEnd() {
      return this.dataEl.layerMeta.OutputDim
    },
    isSelectedEl() {
      return this.dataEl.layerMeta.isSelected
    },
    networkMode() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.netMode
    },
    wsZoom() {
      return this.$store.getters['mod_workspace/GET_currentNetworkZoom'];
    },
    classEl() {
      return {
        [`el-type-${this.dataEl.layerType}`]: true,
        'net-element--active': this.isSelectedEl || this.dataEl.layerId === this.closestElId,
        'element--hidden': this.dataEl.layerMeta.isInvisible
      }
    },
    classElWindow() {
      return {
        'net-element_window--left': this.openWinPosition.left,
        'net-element_window--top': this.openWinPosition.top
      }
    },
    isCodeWindowFocused() {
      return this.$store.state['mod_workspace-code-editor'].isInFocus;
    },
    isSettingInputFocused() {
      return this.$store.state.mod_workspace.isSettingInputFocused;
    },
    closestElId() {
      return this.$store.state['mod_addComponent'].closestElId;
    }
  },
  watch: {
    'modAddComponentState.draggedComponnentPosition':{
      handler(data) {
        const { isShiftPressed, isFirstComponentDragged, draggedComponnentPosition: {x, y}} = this.modAddComponentState;
        let closestElId = null;
        let distance = null;
        const el = document.getElementById('networkWorkspace') || {scrollLeft: 0, scrollTop: 0};
        const mousePositionX = x + 46 + el.scrollLeft;
        const mousePositionY = y - 130 + el.scrollTop;
        if(isShiftPressed && isFirstComponentDragged) {
          Object.keys(this.networkElmentPositions).map(elId => {
            const elPositionX = calcLayerPosition(this.networkElmentPositions[elId].left, this.wsZoom) +  75 * this.wsZoom;
            const elPositionY = calcLayerPosition(this.networkElmentPositions[elId].top, this.wsZoom) + 20 * this.wsZoom;
            const currentDistance = this.getDistance(mousePositionX , mousePositionY, elPositionX, elPositionY);
            
            if(currentDistance < distance || distance === null && currentDistance <= SHIFT_HOLDING_CONNECT_COMPONENT_MAX_DISTANCE) { 
              distance = currentDistance;
              closestElId = elId;
            }
          })
        }
        this.$store.dispatch('mod_addComponent/setClosestElementId', closestElId)
      },
      deep: true,
      immediate: true
    },
    isSelectedEl(newVal) {
      newVal
        ? this.mousedownOutsideBefore()
        : null
    },
    '$store.state.mod_events.globalPressKey.esc': {
      handler() {
        // if(!this.isTutorialMode) this.hideAllWindow();
      }
    },
    '$store.state.mod_events.globalPressKey.del': {
      handler() {
        if(this.editIsOpen
          && !this.isCodeWindowFocused
          && !this.isSettingInputFocused
          && this.isSelectedEl
        ) {
          this.elementDelete();
        }
      }
    },
  },
  methods: {
    getDistance(div1x, div1y, div2x, div2y){
      const distanceSquared = Math.pow(div1x - div2x, 2) + Math.pow(div1y - div2y, 2);
      const distance = Math.sqrt(distanceSquared);
      return distance
    },
    ...mapActions({
      setNetMode:               'mod_workspace/SET_netMode',
      setElementInfoOpen:       'mod_workspace/SET_isOpenElement',
      elementDelete:            'mod_workspace/DELETE_element',
      elementMultiSelect:       'mod_workspace/SET_elementMultiSelect',
      elementSelect:            'mod_workspace/SET_elementSelect'
    }),
    startArrowPaint(ev) {
      document.addEventListener('mouseup', this.toEditMode); // back to edit mode
      this.setNetMode('addArrow'); 
      this.Mix_paintArrow_arrowStartPaint(ev);
    },
    toEditMode() {
      this.setNetMode('edit');
      document.removeEventListener('mouseup', this.toEditMode);
    },
    switchMousedownEvent(ev) {
      if (this.isLock) return;
      // if(this.networkMode === 'addArrow') {
      //   this.Mix_paintArrow_arrowStartPaint(ev)
      // };
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
        
        this.$store.commit('mod_statistics/CHANGE_viewBoxSelectElArr', this.dataEl);
        this.$store.commit('mod_statistics/setDefaultMetric', 'viewBoxTabs');
      }
    },
    switchDblclick(event) {
      if (this.isLock) return;
      if(this.networkMode !== 'edit') {
        this.setNetMode('edit');
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
      this.hideAllWindow();
      if(!this.editIsOpen) return;

      this.setElementInfoOpen(true);
      this.settingsIsOpen = true;

      this.$nextTick(() => {
        this.calcWindowPosition();
      });
    },
    openContext(event) {
      if(!this.settingsIsOpen) {
        this.hideAllWindow();
        if(!this.currentSelectedEl.length) {
          this.elementSelect({id: this.currentId, setValue: true })
        }
        //this.calcWindowPosition();
        if(this.networkMode === 'edit' && this.editIsOpen) {
          this.setElementInfoOpen(true);
          this.contextIsOpen = true;
          document.addEventListener('click', this.hideAllWindow, true);
          document.addEventListener('contextmenu', this.hideAllWindow, true);
        }
      }
    },
    calcWindowPosition(el) {
      let windowWs = document.querySelector('.js-info-section_main');
      let windowWsWidth = windowWs.clientWidth /this.wsZoom;
      let windowWsHeight = windowWs.clientHeight /this.wsZoom;
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
    },
    setFocusEl(ev) {
      // ev.ctrlKey
      //   ? this.elementMultiSelect({id: this.currentId, setValue: true })
      //   : this.elementSelect({id: this.currentId, setValue: true })
    },
    mousedownOutsideBefore() {
      this.MousedownElementTracking = this.$refs.rootBaseElement;
      document.addEventListener('mousedown', this.mousedownOutside);
    },
    mousedownOutsideAction() {
      if (this.editIsOpen) this.deselect()
    },
    hideAllWindow() {
      this.setElementInfoOpen(false);
      this.settingsIsOpen = false;
      this.contextIsOpen = false;
      this.openWinPosition = {
        left: false,
        top: false,
        offset: 0
      }
      document.removeEventListener('click', this.hideAllWindow, true);
      document.removeEventListener('contextmenu', this.hideAllWindow, true);
    },
    deselect() {
      this.hideAllWindow();
      // this.elementSelect({id: this.currentId, setValue: false });
    },
    tutorialSearchId(event) {
      //TODO need paused in tutorial
      /// return event.target.tagName === 'I'
      //   ? event.target.parentNode.parentNode.id
      //   : event.target.parentNode.id
    }
  }
}
