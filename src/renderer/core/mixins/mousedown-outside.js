/*
  ADD TO EVENT
* this.ClickElementTracking = ev.target.closest('.js-clickout');
  document.addEventListener('click', this.clickOutside);
* */

const mousedownOutside = {
  data() {
    return {
      MousedownElementTracking: null
    }
  },
  methods: {
    mousedownOutside(event) {
      console.log('clickOutside mixin');
      if (event.target.closest('.js-clickout') !== this.MousedownElementTracking) {
        document.removeEventListener('mousedown', this.mousedownOutside);
        this.MousedownElementTracking = null;
        this.mousedownOutsideAction();
      }
    },
    mousedownOutsideAction() {
      console.log('need add method clickOutsideAction');
    },
  },
  beforeDestroy() {
    console.log('beforeDestroy clickOutsideAction');
    document.removeEventListener('mousedown', this.mousedownOutside);
  }
};

export default mousedownOutside
