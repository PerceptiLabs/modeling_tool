const baseNetPaintArrows = {
  data() {
    return {
    }
  },
  mounted() {

  },
  computed: {

  },
  methods: {
    arrowStartPaint(ev) {
      console.log('addArrow');
      event.stopPropagation();

      if (this.isLock) {
        return
      }

      this.$parent.$parent.$el.addEventListener('mousemove', this.arrowMovePaint);
      this.$parent.$parent.$el.addEventListener('mouseup', this.arrowEndPaint);
      //this.$parent.$parent.$el.addEventListener('mouseleave', this.up);

      this.$parent.$parent.$el.addEventListener('touchmove', this.arrowMovePaint, true);
      this.$parent.$parent.$el.addEventListener('touchend touchcancel', this.arrowEndPaint, true);
      this.$parent.$parent.$el.addEventListener('touchstart', this.arrowEndPaint, true);

      // this.stickStartPos.mouseX = ev.pageX || ev.touches[0].pageX;
      // this.stickStartPos.mouseY = ev.pageY || ev.touches[0].pageY;
      //
      // this.stickStartPos.left = this.left;
      // this.stickStartPos.top = this.top;

    },
    arrowMovePaint() {
      console.log('arrow Move Paint');
    },
    arrowEndPaint() {
      console.log('stop addArrow');


      this.$parent.$parent.$el.removeEventListener('mousemove', this.arrowMovePaint);
      this.$parent.$parent.$el.removeEventListener('mouseup', this.arrowEndPaint);

      this.$parent.$parent.$el.removeEventListener('touchmove', this.arrowMovePaint, true);
      this.$parent.$parent.$el.removeEventListener('touchend touchcancel', this.arrowEndPaint, true);
      this.$parent.$parent.$el.removeEventListener('touchstart', this.arrowEndPaint, true);
    }
  }
}

export default baseNetPaintArrows
