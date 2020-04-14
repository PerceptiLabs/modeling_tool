import {mapActions} from "vuex";

const workspaceScale = {
  data() {
    return {
      scalingSteps: [25, 33, 50, 67, 75, 80, 90, 100, 110, 120, 133, 150, 170, 200] // must be sorted
    }
  },
  computed: {
    scaleNet: {
      get: function () {
        let zoom = this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom * 100;
        return Math.round(zoom);
      },
      set: function (newValue) {

        let numberToUse = this.scaleNet;
        if (newValue >= 25 &&  newValue <= 200) {
          numberToUse = newValue;
        }
        
        this.set_statusNetworkZoom(numberToUse/100);
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
      set_statusNetworkZoom: 'mod_workspace/SET_statusNetworkZoom',
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
    decScale() {
      // if (this.scaleNet <= 100) {
      //   this.scaleNet = this.scaleNet - 5;
      //   return;
      // }

      const nextSmallest = this.scalingSteps.reduce((prev, curr) => {
        return (this.scaleNet <= curr) ? prev : curr;
      });

      this.scaleNet = nextSmallest;

    },
    incScale () {
      // if (this.scaleNet < 95) { //Old zoom steps, 5% each
      //   this.scaleNet = this.scaleNet + 5;
      //   return; 
      // } 

      const nextLargest = this.scalingSteps.reduce((prev, curr) => {
        return (this.scaleNet < prev) ? prev : curr;
      });

      this.scaleNet = nextLargest;
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
    }
  }
};

export default workspaceScale
