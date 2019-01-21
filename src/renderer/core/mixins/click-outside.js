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
      console.log('clickOutside mixin');
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
    console.log('beforeDestroy clickOutsideAction');
    document.removeEventListener('click', this.clickOutside);
  }
};

export default clickOutside
