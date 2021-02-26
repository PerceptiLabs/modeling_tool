import {calcLayerPosition} from '@/core/helpers.js'
import { workspaceGrid, shadowBoxDragIfMoreThenElementsSelected}   from '@/core/constants.js'
import {mapActions, mapGetters, mapMutations} from "vuex";
import {debounce, throttleEv} from '@/core/helpers'
import cloneDeep from 'lodash.clonedeep';

const baseNetDrag = {
  // props: {
  //   dataEl: {type: Object},
  // },
  data() {
    return {
      left: this.x,
      top: this.y,
      throttleMove: throttleEv(this.move, 33),
      initialElementsPositons: {}
    }
  },

  created() {
    this.bodyDrag = false;
    this.itemWasDragged = false;
    this.stickStartPos = {mouseX: 0, mouseY: 0, x: 0, y: 0, w: 0, h: 0};
  },

  methods: {
    ...mapActions({
      setElementSelectedAction: 'mod_workspace/SET_elementSelect',
    }),
    ...mapMutations({
      updateDragBoxContainerMutation: 'mod_workspace/updateDragBoxContainerMutation'
    }),
    ...mapGetters({
      selectedItems : 'mod_workspace/GET_currentSelectedEl',
    }),
    isCurrentItemSelected(itemId) {
      const selectedItems = {...this.selectedItems()};
      const selectedItemsIds = Object.values(selectedItems).map(el => parseInt(el.layerId, 10));
      return selectedItemsIds.includes(parseInt(itemId, 10));
    },
    isFewItemsSelected() {
      return this.selectedItems().length <= shadowBoxDragIfMoreThenElementsSelected;
    },
    getDragBoxSize() {
      const selectedItems = {...this.selectedItems()};
      const selectedItemsPositions = Object.values(selectedItems).map(el => {
        const workspaceElement = document.querySelector(`[layer-id="${el.layerId}"]`);
        const width = workspaceElement.offsetWidth * this.networkScale;
        const height = workspaceElement.offsetHeight * this.networkScale;
        let result = {
          ...el.layerMeta.position,
          right: width + el.layerMeta.position.left,
          bottom: height + el.layerMeta.position.top,
        }
        return result
      });
      const topValues = selectedItemsPositions.map(x => x.top);
      const leftValues = selectedItemsPositions.map(x => x.left);
      const rightValues = selectedItemsPositions.map(x => x.right);
      const bottomValues = selectedItemsPositions.map(x => x.bottom);

      const width = Math.max(...rightValues) - Math.min(...leftValues);
      const height = Math.max(...bottomValues) - Math.min(...topValues);
      return {width, height, top: Math.min(...topValues), left: Math.min(...leftValues)};
    },
    applyCoefficientScale(num) {
      return num;
    },
    move(ev) {
      if (!this.bodyDrag) return;
      else {
        ev.stopPropagation();
        this.bodyMove(ev)
      }
    },

    up(ev) {
      if (this.bodyDrag) {
        this.bodyUp(ev)
      }
    },
    bodyDown(ev) {
      if(!this.isCurrentItemSelected(this.dataEl.layerId)) {
        if (ev.shiftKey || ev.metaKey || ev.ctrlKey) {
          this.setElementSelectedAction({id: this.dataEl.layerId, setValue: true, resetOther: false})
        } else {
          this.setElementSelectedAction({id: this.dataEl.layerId, setValue: true, resetOther: true})
        }
      }
     
      if (this.contextIsOpen || this.settingsIsOpen) {
        this.contextIsOpen ? this.contextIsOpen = false : null;
        return;
      }

      this.initialElementsPositons = cloneDeep(this.networkElmentPositions);

      this.$parent.$parent.$el.addEventListener('mousemove', this.throttleMove);
      document.addEventListener('mouseup', this.up);

      this.$parent.$parent.$el.addEventListener('touchmove', this.throttleMove, true);
      document.addEventListener('touchend touchcancel', this.up, true);
      document.addEventListener('touchstart', this.up, true);

      this.bodyDrag = true;

      this.stickStartPos.mouseX = ev.pageX || ev.touches[0].pageX;
      this.stickStartPos.mouseY = ev.pageY || ev.touches[0].pageY;

      this.stickStartPos.left = this.left;
      this.stickStartPos.top = this.top;
      // set initial borders for dragged elements
    },

    bodyMove(ev) {
      if(this.getIsWorkspaceDragEvent) {
        return;
      }

      if(!this.isFewItemsSelected() && !this.itemWasDragged) {
        this.updateDragBoxContainerMutation({
          isVisible: true,
          ...this.getDragBoxSize(),
        });
      }
      
      this.itemWasDragged = true;

      if(this.isFewItemsSelected()) {
        this.updateItems(ev);
      } else {
        const { width, height, top: initialTop, left: initialLeft } = this.getDragBoxSize();
        if(!(ev.pageX % workspaceGrid || ev.pageY % workspaceGrid)) return;

        const stickStartPos = this.stickStartPos;
       
        const top = this.applyCoefficientScale(ev.pageY) - (this.applyCoefficientScale(stickStartPos.mouseY) - initialTop);
        const left = this.applyCoefficientScale(ev.pageX) - (this.applyCoefficientScale(stickStartPos.mouseX) - initialLeft);
        
        this.updateDragBoxContainerMutation({
          isVisible: true,
          top,
          left,
          width,
          height,
        });
      }
    },

    bodyUp(ev) {
      this.bodyDrag = false;
      // update network and remove borders
      this.updateItems(ev);

      if(!this.isFewItemsSelected()) {
        this.updateDragBoxContainerMutation({
          isVisible: false,
          top: 0,
          left: 0,
          width: 0,
          height: 0,
        });
      }
      
      if(this.isCurrentItemSelected(this.dataEl.layerId) && !this.itemWasDragged && !(ev.shiftKey || ev.metaKey || ev.ctrlKey)) {
        this.setElementSelectedAction({id: this.dataEl.layerId, setValue: true, resetOther: true})
      }

      if (this.itemWasDragged && this.wasELementsPositionChanged()) {
        this.$store.dispatch('mod_workspace-history/PUSH_newSnapshot', null, {root: true});

        this.$store.dispatch('mod_workspace-changes/updateUnsavedChanges', {
          networkId: this.currentNetworkId,
          value: true
        }, {root: true});
      }
      
      this.itemWasDragged = false;
      this.$store.dispatch('mod_workspace/CHANGE_elementPosition', this.rect);
      this.$parent.$parent.createArrowList();

      this.$parent.$parent.$el.removeEventListener('mousemove', this.throttleMove);
      this.$parent.$parent.$el.removeEventListener('touchmove', this.throttleMove, true);
      document.removeEventListener('mouseup', this.up);
      document.removeEventListener('touchend touchcancel', this.up, true);
      document.removeEventListener('touchstart', this.up, true);
      
      this.$store.dispatch('mod_workspace/afterNetworkElementIsDragged');
    },
    updateItems(ev) {
      if(!(ev.pageX % workspaceGrid || ev.pageY % workspaceGrid)) return;

      const stickStartPos = this.stickStartPos;
      const delta = {
        x: (stickStartPos.mouseX - (ev.pageX || ev.touches[0].pageX)), 
        y: (stickStartPos.mouseY - (ev.pageY || ev.touches[0].pageY)) 
      };
      
      const networkScale = this.networkScale;
      const top = this.bodyDrag ? stickStartPos.top - delta.y : calcLayerPosition(stickStartPos.top - delta.y, networkScale);
      const left = this.bodyDrag ? stickStartPos.left - delta.x : calcLayerPosition(stickStartPos.left - delta.x, networkScale);
      if((this.top !== top) || (this.left !== left)) {
        this.top = (top < 0) ? 0 : top;
        this.left = (left < 0) ? 0 : left;
        this.$store.dispatch('mod_workspace/CHANGE_elementPosition', this.rect);
      }
    },
    wasELementsPositionChanged() {
      let isPositionChanged = false
      let currentPositions = this.networkElmentPositions;
      Object.keys(this.initialElementsPositons).map(key => {
        if((this.initialElementsPositons[key].left !== currentPositions[key].left)
          || this.initialElementsPositons[key].top !== currentPositions[key].top ) {
            isPositionChanged = true;
          }
      });
      return isPositionChanged;
    }

  },
  computed: {
    currentNetworkId() {
      return this.$store.getters['mod_workspace/GET_currentNetworkId']
    },
    networkScale() {
      return this.$store.getters['mod_workspace/GET_currentNetworkZoom'];
    },
    isLock() {
      return this.dataEl.layerMeta.isLock
    },
    x() {
      if(this.dataEl) {
        let l = this.dataEl.layerMeta.position.left;
        this.left = l;
        return l
      }
      else {
        this.left = 0;
        return 0
      }
    },
    y() {
      if(this.dataEl) {
        let t = this.dataEl.layerMeta.position.top;
        this.top = t;
        return t
      }
      else {
        this.top = 0;
        return 0
      }
    },
    style() {
      let scale = `scale(${this.networkScale})`;

      return {
       'z-index': 1,
       'transform': scale,
       'transform-origin': 'left top',

        top: this.top + 'px',
        left: this.left + 'px',
      }
    },
    rect() {
      return {
        id: this.dataEl.layerId,
        left: this.left,
        top: this.top,
      }
    },
    ...mapGetters({
      getIsWorkspaceDragEvent: 'mod_events/getIsWorkspaceDragEvent',
      networkElmentPositions:  'mod_workspace/GET_networkElmentPositions',
    }),
  },

  watch: {
    x() { return },
    y() { return },
  },
};

export default baseNetDrag
