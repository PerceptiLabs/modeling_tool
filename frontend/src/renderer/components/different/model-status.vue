<template lang="pug">
    div
      div(v-if="statusData.Status === 'Finished'").d-flex.align-items-center
        img(src="./../../../../static/img/model-status-complete.svg")
        span.training-complete-text Training Complete
      div(v-else)
        //- .name {{statusData.Status === 'Waiting' || !!statusData ? 'Untrained':   statusData.Status === 'Stop' ? 'Training' :  statusData.Status}}
        .name {{statusData.Status ? statusData.Status === 'Stop' ? 'Stopped' : statusData.Status : 'Untrained'}}
        div.d-flex.align-items-center
          .train-progress-wrapper
            .train-progress-bars(:style="progressStyle") 
          .progres-in-percent {{ statusData.Status === 'Waiting' ? '' : isNaN(parseInt(statusData.Progress * 100, 10)) ? '' : `${parseInt(statusData.Progress * 100, 10)}%`}}


</template>
<script>
export default {
  name: 'ModelStatus',
  props: {
    statusData: {
      type: Object,
      default: {},
    },
    status: {
      type: Number,
      default: 0
    },
    isComplete: {
      type: Boolean,
      default: false,
    }
  },
  data: {
    progressStyle: {},
  },
  watch: {
    'statusData.Progress': function () {
      this.getProgres();
    }
  },
  created(){
    this.getProgres();
  },
  methods: {
    getProgres() {
      let progress = 0;
      const color = '#73FEBB';  // green - #73FEBB  orange - #4D556A  blue - #7397FE
      const svg = `<svg width="3" height="8" viewBox="0 0 1 8" xmlns="http://www.w3.org/2000/svg"><rect width="1" height="8" rx="0.5" fill="${color}"/></svg>`;
      const encodedSvg = `url(data:image/svg+xml;base64,${window.btoa(svg)}`
      if(this.statusData.Status === 'Stop' || this.statusData.Status === 'Training' || this.statusData.Status === 'Validation') {
        progress = parseInt(this.statusData.Progress * 100, 10);
      }
      this.progressStyle = {
        width: `${progress}px` ,
        backgroundImage: encodedSvg,
      }
    }
  }
}
// <svg width="3" height="8" viewBox="0 0 1 8" fill="#ccc" xmlns="http://www.w3.org/2000/svg"><rect width="1" height="8" rx="0.5" fill="#E48B23"/></svg>
</script>
<style lang="scss" scoped>
  .name {
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: normal;
    font-size: 14px;
    line-height: 19px;
    color: #E1E1E1;
  }
  .train-progress-wrapper {
    background: #363E51;
    border: 1px solid #4D556A;
    box-sizing: border-box;
    border-radius: 1px;
    width: 100px;
    height: 10px
  }
  .progres-in-percent {
    margin-left: 7px;
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: bold;
    font-size: 12px;
    line-height: 16px;
    vertical-align: bottom;
  }
  .train-progress-bars {
    height: 8px;
    background-repeat: repeat-x;
  }
  .training-complete-text {
    margin-left: 5px;
  }
</style>