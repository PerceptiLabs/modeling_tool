const baseNetDrag = {
  props: {
    parentScaleX: {
      type: Number, default: 1,
    },
    parentScaleY: {
      type: Number, default: 1,
    },
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
      if (!this.bodyDrag) {
        return
      }
      ev.stopPropagation();
      if (this.bodyDrag) {
        this.bodyMove(ev)
      }
    },

    up(ev) {
      if (this.bodyDrag) {
        this.bodyUp(ev)
      }
    },

    bodyDown(ev) {
      //event.stopPropagation();

      //document.documentElement.addEventListener('mousedown', this.deselect);//base-net-functional.js
      //base-net-functional.js

      if (this.contextIsOpen || this.settingsIsOpen) {
        return
      }

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
      const stickStartPos = this.stickStartPos;

      let delta = {
        x: (stickStartPos.mouseX - (ev.pageX || ev.touches[0].pageX)) / this.parentScaleX,
        y: (stickStartPos.mouseY - (ev.pageY || ev.touches[0].pageY)) / this.parentScaleY
      };

      this.top = stickStartPos.top - delta.y;
      this.left = stickStartPos.left - delta.x;

      this.$store.commit('mod_workspace/CHANGE_elementPosition', this.rect);
    },

    bodyUp() {
      this.bodyDrag = false;

      this.$store.commit('mod_workspace/CHANGE_elementPosition', this.rect);
      this.$parent.$parent.createArrowList();

      document.documentElement.removeEventListener('mousedown', this.deselect);//base-net-functional.js
      this.$parent.$parent.$el.removeEventListener('mousemove', this.move);
      this.$parent.$parent.$el.removeEventListener('mouseup', this.up);

      this.$parent.$parent.$el.removeEventListener('touchmove', this.move, true);
      this.$parent.$parent.$el.removeEventListener('touchend touchcancel', this.up, true);
      this.$parent.$parent.$el.removeEventListener('touchstart', this.up, true);
    },

  },
  computed: {
    isLock() {
      return this.dataEl.el.meta.isLock
    },
    x() {
      if(this.dataEl.el) {
        this.left = this.dataEl.el.meta.left;
        return this.dataEl.el.meta.left
      }
      else {
        this.left = 0;
        return 0
      }
    },
    y() {
      if(this.dataEl.el) {
        this.top = this.dataEl.el.meta.top;
        return this.dataEl.el.meta.top
      }
      else {
        this.top = 0;
        return 0
      }
    },
    indexEl() {
      return (this.dataEl.index >= 0 ) ? this.dataEl.index : null
    },
    style() {
      return {
        top: this.top + 'px',
        left: this.left + 'px',
      }
    },
    rect() {
      return {
        index: this.indexEl,
        left: this.left,
        top: this.top,
      }
    }
  },

  watch: {
    x() {
      return
    },

    y() {
      return
    },
  },
};

export default baseNetDrag
