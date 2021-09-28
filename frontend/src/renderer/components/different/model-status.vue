<template lang="pug">
    div.relative
      div(v-if="statusData.Status === 'Finished'").d-flex.align-items-center
        img(src="./../../../../static/img/model-status-complete-white.svg")
        span.training-complete-text Training Complete
      div(
        :class="{'show-status-inline': options.styleInlineLabel}"
        v-else
        )
        
        .name.warn-color(v-if="showError()") Error
        .name(v-else :class="{'warn-color': showError(), 'have-progress': !isNaN(parseInt(statusData.Progress * 100, 10))}") {{statusData.Status ? statusData.Status === 'Stop' ? 'Stopped' : statusData.Status : 'Untrained'}}
        
        div.d-flex.align-items-center(v-if="showProgress")
          .train-progress-wrapper
            .train-progress-bars(:style="progressStyle") 
          
          .progress-in-percent(v-if="!showError()") {{ statusData.Status === 'Waiting' ? '' : isNaN(parseInt(statusData.Progress * 100, 10)) ? '' : `${parseInt(statusData.Progress * 100, 10)}%`}}
          div.svg-warning-wrapper(v-else v-tooltip:right-wrap-text="coreError.errorMessage")
            svg(width='12' height='12' viewbox='0 0 12 12' fill='none' xmlns='http://www.w3.org/2000/svg')
              circle(cx='6' cy='6' r='6' fill='#E48B23')
              g(filter='url(#filter0_d)')
              path(d='M6.6416 6.97412H5.44189L5.25293 2.60156H6.83057L6.6416 6.97412ZM5.20898 8.33643C5.20898 8.11963 5.28662 7.94238 5.44189 7.80469C5.6001 7.66406 5.79639 7.59375 6.03076 7.59375C6.26514 7.59375 6.45996 7.66406 6.61523 7.80469C6.77344 7.94238 6.85254 8.11963 6.85254 8.33643C6.85254 8.55322 6.77344 8.73193 6.61523 8.87256C6.45996 9.01025 6.26514 9.0791 6.03076 9.0791C5.79639 9.0791 5.6001 9.01025 5.44189 8.87256C5.28662 8.73193 5.20898 8.55322 5.20898 8.33643Z' fill='white')
              defs
                filter#filter0_d(x='1.20898' y='2.60156' width='9.64355' height='14.4775' filterunits='userSpaceOnUse' color-interpolation-filters='sRGB')
                  feflood(flood-opacity='0' result='BackgroundImageFix')
                    fecolormatrix(in='SourceAlpha' type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0')
                      feoffset(dy='4')
                        fegaussianblur(stddeviation='2')
                          fecolormatrix(type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0')
                            feblend(mode='normal' in2='BackgroundImageFix' result='effect1_dropShadow')
                              feblend(mode='normal' in='SourceGraphic' in2='effect1_dropShadow' result='shape')  


</template>
<script>
export default {
  name: 'ModelStatus',
  computed: {
    showProgress: function() {
      return this.statusData.hasOwnProperty('Progress');
    }
  },
  props: {
    statusData: {
      type: Object,
      default: function() { return {}},
    },
    status: {
      type: Number,
      default: 0
    },
    coreError: {
      type: Object,
      default: function() { return {}},
    },
    options: {
      type: Object,
      default: function() { return {
        styleInlineLabel: false,
      }},
    }
  },
  data() {
    return {
      progressStyle: {},
    }
  },
  watch: {
    'statusData.Progress': function () {
      this.getProgress();
    }
  },
  created(){
    this.getProgress();
  },
  methods: {
    showError() {
      return !!(this.coreError.hasOwnProperty('Status') || this.coreError.hasOwnProperty('errorMessage')) && Object.keys(this.statusData).length === 0;
    },
    getProgress() {
      let progress = 0;
      let color = '#6185EE';  // green - #73FEBB  orange - #E48B23  blue - #7397FE
      if(this.showError()) {
        color = '#E48B23'
      }
      const svg = `<svg width="3" height="14" viewBox="0 0 1 14" xmlns="http://www.w3.org/2000/svg"><rect width="1" height="14" rx="0.5" fill="${color}"/></svg>`;
      const encodedSvg = `url(data:image/svg+xml;base64,${window.btoa(svg)}`
      if(this.statusData.Status === 'Stop' || this.statusData.Status === 'Training' || this.statusData.Status === 'Validation' || this.statusData.Status === 'Paused') {
        progress = parseInt(this.statusData.Progress * 100, 10);
      }
      this.progressStyle = {
        width: `${progress}px` ,
        borderRadius: '55px',
        background: color,
      }
    },
  }
}
</script>
<style lang="scss" scoped>
  .relative {
    position: relative;
  }
  .name {
    font-family: 'Roboto', sans-serif;
    font-style: normal;
    font-weight: normal;
    font-size: 16px;
    line-height: 19px;
    &.have-progress {
      position: absolute;
      left: 0;
      top: -21px;
    }
  }
  .train-progress-wrapper {
    box-sizing: border-box;
    width: 100px;
    height: 12px;
    background: #D9E3FF;
    border-radius: 55px;
    border: 1px solid #D9E3FF;
  }
  .progress-in-percent {
    margin-left: 7px;
    font-family: 'Roboto', sans-serif;
    font-style: normal;
    font-weight: bold;
    font-size: 16px;
    line-height: 16px;
    vertical-align: bottom;
  }
  .train-progress-bars {
    height: 10px;
    background-repeat: repeat-x;
  }
  .training-complete-text {
    margin-left: 5px;
  }
  .svg-warning-wrapper {
    margin-left: 7px;
    height: 10px;
  }
 
  .warn-color {
    color: #E48B23;
  }
  .show-status-inline {
    display: flex;
    .name {
      margin-right: 5px;
    }
  }
</style>
