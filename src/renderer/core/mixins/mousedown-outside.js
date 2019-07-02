/*
  ADD TO EVENT
* this.ClickElementTracking = ev.target.closest('.js-clickout');
  document.addEventListener('click', this.clickOutside);
* */
import store from '../../store'
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
          && !store.getters['mod_tutorials/getIstutorialMode']) // don`t hide all settings if tutorial mode is enable
      {
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
