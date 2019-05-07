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
      //event.stopPropagation();

      //document.documentElement.addEventListener('mousedown', this.deselect);//base-net-functional.js
      //base-net-functional.js

      if (this.contextIsOpen || this.settingsIsOpen) return;

      this.$parent.$parent.$el.addEventListener('mousemove', this.move);
      this.$parent.$parent.$el.addEventListener('mouseup', this.up);
      //this.$parent.$parent.$el.addEventListener('mouseleave', this.up);

      this.$parent.$parent.$el.addEventListener('touchmove', this.move, true);
      this.$parent.$parent.$el.addEventListener('touchend touchcancel', this.up, true);
      this.$parent.$parent.$el.addEventListener('touchstart', this.up, true);

      this.bodyDrag = true;

      this.stickStartPos.mouseX = ev.pageX || ev.touches[0].pageX;
      this.stickStartPos.mouseY = ev.pageY || ev.touches[0].pageY;

      this.stickStartPos.left = this.left;
      this.stickStartPos.top = this.top;

    },

    bodyMove(ev) {
      if(!(ev.pageX % 10 || ev.pageY % 10)) return;

      const stickStartPos = this.stickStartPos;
      const delta = {
        x: (stickStartPos.mouseX - (ev.pageX || ev.touches[0].pageX)) / this.networkScale,
        y: (stickStartPos.mouseY - (ev.pageY || ev.touches[0].pageY)) / this.networkScale
      };
      const top = Math.round((stickStartPos.top - delta.y)/10)*10;
      const left = Math.round((stickStartPos.left - delta.x)/10)*10;

      this.top = (top < 0) ? 0 : top;
      this.left = (left < 0) ? 0 : left;
      this.$store.dispatch('mod_workspace/CHANGE_elementPosition', this.rect);
    },

    bodyUp() {
      this.bodyDrag = false;

      this.$store.dispatch('mod_workspace/CHANGE_elementPosition', this.rect);
      this.$parent.$parent.createArrowList();

      //document.documentElement.removeEventListener('mousedown', this.deselect);//base-net-functional.js
      this.$parent.$parent.$el.removeEventListener('mousemove', this.move);
      this.$parent.$parent.$el.removeEventListener('mouseup', this.up);

      this.$parent.$parent.$el.removeEventListener('touchmove', this.move, true);
      this.$parent.$parent.$el.removeEventListener('touchend touchcancel', this.up, true);
      this.$parent.$parent.$el.removeEventListener('touchstart', this.up, true);
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
        let l = this.dataEl.layerMeta.position.left + this.dataEl.layerMeta.containerDiff.left;
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
        let t = this.dataEl.layerMeta.position.top + this.dataEl.layerMeta.containerDiff.top;
        this.top = t;
        return t
      }
      else {
        this.top = 0;
        return 0
      }
    },
    // indexEl() {
    //   return (this.dataEl.index >= 0 ) ? this.dataEl.index : null
    // },
    style() {
      return {
        top: this.top + 'px',
        left: this.left + 'px',
      }
    },
    rect() {
      return {
        index: this.dataEl.layerId,
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
