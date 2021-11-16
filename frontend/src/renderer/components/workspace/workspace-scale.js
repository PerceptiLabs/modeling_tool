import {mapActions} from "vuex";

const workspaceScale = {
  data() {
    return {
      tempZoomValue: 100, // used for intermediate calculations
      scalingSteps: [25, 33, 50, 67, 75, 80, 90, 100, 110, 120, 133, 150, 170, 200] // must be sorted
    }
  },
  computed: {
    scaleNet: {
      get: function () {
        let zoom = this.$store.getters['mod_workspace/GET_currentNetworkZoom'] * 100;
        return Math.round(zoom);
      },
      set: function (newValue) {
        // used to store what gets typed in
        // actual system-wide zoom level gets updated on blur
        this.tempZoomValue = newValue; 
      }
    },
  },
  watch: {
    // indexCurrentNetwork() {
    //   this.scaleNet.get()
    // },
  },
  methods: {
    ...mapActions({
      set_statusNetworkZoom:          'mod_workspace/SET_statusNetworkZoom',
      updateNetworkElementPositions:  'mod_workspace/updateNetworkElementPositions'
    }),
    calcScaleMap() {
      this.$nextTick(()=> {
        const net = this.$refs.networkField[0].$refs.network;
        const scaleH = net.offsetHeight/net.scrollHeight;
        const scaleW = net.offsetWidth/net.scrollWidth;
        const maxScale = scaleH < scaleW ? scaleH : scaleW;
        this.scaleNet = +maxScale.toFixed(1) * 100;
      })
    },
    scaleScroll(event) {
      if(event.ctrlKey || event.metaKey) {
        event.preventDefault();
        event.deltaY < 0
          ? this.incScale()
          : this.decScale();
      }
    },
    scale(zoomLevel) {
      this.updateNetworkElementPositions({ zoom: zoomLevel });
      this.set_statusNetworkZoom(zoomLevel);
    },
    decScale() {
      const nextSmallest = this.scalingSteps.reduce((prev, curr) => {
        return (this.scaleNet <= curr) ? prev : curr;
      });

      const zoomLevel = nextSmallest/100;

      this.scale(zoomLevel);
    },
    incScale () {
      const nextLargest = this.scalingSteps.reduce((prev, curr) => {
        return (this.scaleNet < prev) ? prev : curr;
      });

      const zoomLevel = nextLargest/100;

      this.scale(zoomLevel);
    },   
    filterNonNumber: function(event) {
      event = event || window.event;
      const charCode = event.which || event.keyCode;

      if (charCode === 13) {
        event.currentTarget.blur();
        return true;
      }
      else if (charCode < 48 || charCode > 57) {
        event.preventDefault();
      } else {
        return true;
      }
    },
    onZoomInputBlur() {
      const smallestVal = this.scalingSteps[0];
      const largestVal = this.scalingSteps[this.scalingSteps.length - 1];

      let numberToUse = 0;

      if (this.tempZoomValue < smallestVal) { numberToUse = smallestVal; }
      else if (this.tempZoomValue > largestVal) { numberToUse = largestVal; }
      else { numberToUse = this.tempZoomValue; }

      this.scale(numberToUse/100);
    }
  }
};

export default workspaceScale
