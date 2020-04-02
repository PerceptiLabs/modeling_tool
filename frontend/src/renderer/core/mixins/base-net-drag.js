import {calcLayerPosition} from '@/core/helpers.js'
import { workspaceGrid, shadowBoxDragIfMoreThenElementsSelected}   from '@/core/constants.js'
import {mapActions, mapGetters, mapMutations} from "vuex";

const baseNetDrag = {
  // props: {
  //   dataEl: {type: Object},
  // },
  data() {
    return {
      left: this.x,
      top: this.y,
    }
  },

  created() {
    this.bodyDrag = false;
    this.itemWasDraged = false;
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
      const selectedItemsPositions = Object.values(selectedItems).map(el => el.layerMeta.position);
      const topValues = selectedItemsPositions.map(x => x.top);
      const leftValues = selectedItemsPositions.map(x => x.left);
      const width = Math.max(...leftValues) - Math.min(...leftValues) + 60;
      const height = Math.max(...topValues) - Math.min(...topValues) + 60;
      return {width, height, top: Math.min(...topValues), left: Math.min(...leftValues)};
    },
    applyCoefficientScale(num) {
      return (num /  (this.networkScale * 100)) * 100;
    },
    move(ev) {
      if (!this.bodyDrag) return;
      else {
        ev.stopPropagation();
        this.bodyMove(ev)
      }
    },

    up(ev) {
      if (this.bodyDrag) this.bodyUp(ev)
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

      this.$parent.$parent.$el.addEventListener('mousemove', this.move);
      document.addEventListener('mouseup', this.up);

      this.$parent.$parent.$el.addEventListener('touchmove', this.move, true);
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
      if(!this.isFewItemsSelected() && !this.itemWasDraged) {
        this.updateDragBoxContainerMutation({
          isVisible: true,
          ...this.getDragBoxSize(),
        });
      }
      
      this.itemWasDraged = true;
      
      if(this.isFewItemsSelected()) {
        this.updateItems(ev);
      } else {
        const { width, height, top: initialTop, left: initialLeft } = this.getDragBoxSize();
        if(!(ev.pageX % workspaceGrid || ev.pageY % workspaceGrid)) return;

        const stickStartPos = this.stickStartPos;
       
        const top = calcLayerPosition((this.applyCoefficientScale(ev.pageY) - (this.applyCoefficientScale(stickStartPos.mouseY) - initialTop)));
        const left = calcLayerPosition((this.applyCoefficientScale(ev.pageX) - (this.applyCoefficientScale(stickStartPos.mouseX) - (initialLeft))));
        
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
      
      // update network and remove borders
      if(!this.isFewItemsSelected()) {
        this.updateItems(ev);
        this.updateDragBoxContainerMutation({
          isVisible: false,
          top: 0,
          left: 0,
          width: 0,
          height: 0,
        });
      }
      
      if(this.isCurrentItemSelected(this.dataEl.layerId) && !this.itemWasDraged && !(ev.shiftKey || ev.metaKey || ev.ctrlKey)) {
        this.setElementSelectedAction({id: this.dataEl.layerId, setValue: true, resetOther: true})
      }
      
      this.itemWasDraged = false;
      this.bodyDrag = false;
      this.$store.dispatch('mod_workspace/CHANGE_elementPosition', this.rect);
      this.$parent.$parent.createArrowList();

      this.$parent.$parent.$el.removeEventListener('mousemove', this.move);
      this.$parent.$parent.$el.removeEventListener('touchmove', this.move, true);
      document.removeEventListener('mouseup', this.up);
      document.removeEventListener('touchend touchcancel', this.up, true);
      document.removeEventListener('touchstart', this.up, true);
      
      this.$store.dispatch('mod_workspace-history/PUSH_newSnapshot', null, {root: true});
    },
    updateItems(ev) {
      if(!(ev.pageX % workspaceGrid || ev.pageY % workspaceGrid)) return;

      const stickStartPos = this.stickStartPos;
      const delta = {
        x: (stickStartPos.mouseX - (ev.pageX || ev.touches[0].pageX)) / this.networkScale,
        y: (stickStartPos.mouseY - (ev.pageY || ev.touches[0].pageY)) / this.networkScale
      };
      const top = calcLayerPosition(stickStartPos.top - delta.y);
      const left = calcLayerPosition(stickStartPos.left - delta.x);

      if((this.top !== top) || (this.left !== left)) {
        this.top = (top < 0) ? 0 : top;
        this.left = (left < 0) ? 0 : left;
        this.$store.dispatch('mod_workspace/CHANGE_elementPosition', this.rect);
      }
    }

  },
  computed: {
    networkScale() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom
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
      return {
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
    }
  },

  watch: {
    x() { return },
    y() { return },
  },
};

export default baseNetDrag
