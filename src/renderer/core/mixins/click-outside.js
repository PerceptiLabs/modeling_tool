/*
  ADD TO EVENT
* this.ClickElementTracking = ev.target.closest('.js-clickout');
  document.addEventListener('click', this.clickOutside);
* */

const clickOutside = {
  data() {
    return {
      ClickElementTracking: null
    }
  },
  methods: {
    clickOutside(event) {
      if (event.target.closest('.js-clickout') !== this.ClickElementTracking) {
        document.removeEventListener('click', this.clickOutside);
        this.ClickElementTracking = null;
        this.clickOutsideAction();
      }
    },
    clickOutsideAction() {
      console.log('need add method clickOutsideAction');
    },
  },
  beforeDestroy() {
    document.removeEventListener('click', this.clickOutside);
  }
};

export default clickOutside
