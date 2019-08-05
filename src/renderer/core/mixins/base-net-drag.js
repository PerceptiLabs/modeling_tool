import {calcLayerPosition} from '@/core/helpers.js'
import { workspaceGrid }   from '@/core/constants.js'

const baseNetDrag = {
  props: {
    dataEl: {type: Object},
  },
  data() {
    return {
      left: this.x,
      top: this.y,
    }
  },

  created() {
    this.bodyDrag = false;
    this.stickStartPos = {mouseX: 0, mouseY: 0, x: 0, y: 0, w: 0, h: 0};
  },

  methods: {
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
      if (this.contextIsOpen || this.settingsIsOpen) return;

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

    },

    bodyMove(ev) {
      if(!(ev.pageX % workspaceGrid || ev.pageY % workspaceGrid)) return;

      const stickStartPos = this.stickStartPos;
      const delta = {
        x: (stickStartPos.mouseX - (ev.pageX || ev.touches[0].pageX)) / this.networkScale,
        y: (stickStartPos.mouseY - (ev.pageY || ev.touches[0].pageY)) / this.networkScale
      };
      const top = calcLayerPosition(stickStartPos.top - delta.y);
      const left = calcLayerPosition(stickStartPos.left - delta.x);

      this.top = (top < 0) ? 0 : top;
      this.left = (left < 0) ? 0 : left;
      this.$store.dispatch('mod_workspace/CHANGE_elementPosition', this.rect);
    },

    bodyUp() {
      this.bodyDrag = false;

      this.$store.dispatch('mod_workspace/CHANGE_elementPosition', this.rect);
      this.$parent.$parent.createArrowList();

      this.$parent.$parent.$el.removeEventListener('mousemove', this.move);
      document.removeEventListener('mouseup', this.up);

      this.$parent.$parent.$el.removeEventListener('touchmove', this.move, true);
      document.removeEventListener('touchend touchcancel', this.up, true);
      document.removeEventListener('touchstart', this.up, true);
    },

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
