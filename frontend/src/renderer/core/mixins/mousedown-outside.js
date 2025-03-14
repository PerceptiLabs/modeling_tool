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
      if (event.target.closest('.js-clickout') !== this.MousedownElementTracking
        && event.button === 0
        && !(event.target.closest('.app-header_nav'))
      ) {
        // if(event.shiftKey || event.ctrlKey) return 0;

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
    document.removeEventListener('mousedown', this.mousedownOutside);
  }
};

export default mousedownOutside
