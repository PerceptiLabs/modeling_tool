<template lang="pug">
  .chart-spinner-box(:class="{'invert':invert}")
    .chart-spinner
    .text(v-show="text") {{text}}
</template>

<script>

export default {
  name: "ChartSpinner",
  props: {
    text: {
      type: String,
      default: '',
    },
    invert: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style lang="scss" scoped>
  .chart-spinner-box {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
    border-radius: 15px;
    background-color: rgba($bg-workspace, .5);    

    &.invert {
      background-color: rgba($bg-setting-layer, .5);
    }
  }

  .text {
    position: absolute;
    top: calc(50% + 40px);
    z-index: 3;
    font-size: 14px;
  }
  .chart-spinner {
    margin: 0 auto;
    font-size: .9rem;
    width: 1em;
    height: 1em;
    border-radius: 50%;
    position: relative;
    text-indent: -9999em;
    animation: chartLoader 1.1s infinite ease;
    transform: translateZ(0);
  }

  $ch-spinner1: #4F71D7;

  @keyframes chartLoader {
    0%, 100% {
      box-shadow: 0em -2.6em 0em 0em #93AFFF,
                  1.8em -1.8em 0 0em rgba($ch-spinner1, .2),
                  2.5em 0em 0 0em rgba($ch-spinner1, .2),
                  1.75em 1.75em 0 0em rgba($ch-spinner1, .2),
                  0em 2.5em 0 0em rgba($ch-spinner1, .2),
                  -1.8em 1.8em 0 0em rgba($ch-spinner1, .2),
                  -2.6em 0em 0 0em rgba($ch-spinner1, .5),
                  -1.8em -1.8em 0 0em rgba($ch-spinner1, .7);
    }
    12.5% {
      box-shadow: 0em -2.6em 0em 0em rgba($ch-spinner1, .7),
                  1.8em -1.8em 0 0em #6185EE,
                  2.5em 0em 0 0em rgba($ch-spinner1, .2),
                  1.75em 1.75em 0 0em rgba($ch-spinner1, .2),
                  0em 2.5em 0 0em rgba($ch-spinner1, .2),
                  -1.8em 1.8em 0 0em rgba($ch-spinner1, .2),
                  -2.6em 0em 0 0em rgba($ch-spinner1, .2),
                  -1.8em -1.8em 0 0em rgba($ch-spinner1, .5);
    }
    25% {
      box-shadow: 0em -2.6em 0em 0em rgba($ch-spinner1, .5),
                  1.8em -1.8em 0 0em rgba($ch-spinner1, .7),
                  2.5em 0em 0 0em #4D73E1,
                  1.75em 1.75em 0 0em rgba($ch-spinner1, .2),
                  0em 2.5em 0 0em rgba($ch-spinner1, .2),
                  -1.8em 1.8em 0 0em rgba($ch-spinner1, .2),
                  -2.6em 0em 0 0em rgba($ch-spinner1, .2),
                  -1.8em -1.8em 0 0em rgba($ch-spinner1, .2);
    }
    37.5% {
      box-shadow: 0em -2.6em 0em 0em rgba($ch-spinner1, .2),
                  1.8em -1.8em 0 0em rgba($ch-spinner1, .5),
                  2.5em 0em 0 0em rgba($ch-spinner1, .7),
                  1.75em 1.75em 0 0em #3C61CD,
                  0em 2.5em 0 0em rgba($ch-spinner1, .2),
                  -1.8em 1.8em 0 0em rgba($ch-spinner1, .2),
                  -2.6em 0em 0 0em rgba($ch-spinner1, .2),
                  -1.8em -1.8em 0 0em rgba($ch-spinner1, .2);
    }
    50% {
      box-shadow: 0em -2.6em 0em 0em rgba($ch-spinner1, .2),
                  1.8em -1.8em 0 0em rgba($ch-spinner1, .2),
                  2.5em 0em 0 0em rgba($ch-spinner1, .5),
                  1.75em 1.75em 0 0em rgba($ch-spinner1, .7),
                  0em 2.5em 0 0em #98B2FF,
                  -1.8em 1.8em 0 0em rgba($ch-spinner1, .2),
                  -2.6em 0em 0 0em rgba($ch-spinner1, .2),
                  -1.8em -1.8em 0 0em rgba($ch-spinner1, .2);
    }
    62.5% {
      box-shadow: 0em -2.6em 0em 0em rgba($ch-spinner1, .2),
                  1.8em -1.8em 0 0em rgba($ch-spinner1, .2),
                  2.5em 0em 0 0em rgba($ch-spinner1, .2),
                  1.75em 1.75em 0 0em rgba($ch-spinner1, .5),
                  0em 2.5em 0 0em rgba($ch-spinner1, .7),
                  -1.8em 1.8em 0 0em #93AFFF,
                  -2.6em 0em 0 0em rgba($ch-spinner1, .2),
                  -1.8em -1.8em 0 0em rgba($ch-spinner1, .2);
    }
    75% {
      box-shadow: 0em -2.6em 0em 0em rgba($ch-spinner1, .2),
                  1.8em -1.8em 0 0em rgba($ch-spinner1, .2),
                  2.5em 0em 0 0em rgba($ch-spinner1, .2),
                  1.75em 1.75em 0 0em rgba($ch-spinner1, .2),
                  0em 2.5em 0 0em rgba($ch-spinner1, .5),
                  -1.8em 1.8em 0 0em rgba($ch-spinner1, .7),
                  -2.6em 0em 0 0em #86A5FF,
                  -1.8em -1.8em 0 0em rgba($ch-spinner1, .2);
    }
    87.5% {
      box-shadow: 0em -2.6em 0em 0em rgba($ch-spinner1, .2),
                  1.8em -1.8em 0 0em rgba($ch-spinner1, .2),
                  2.5em 0em 0 0em rgba($ch-spinner1, .2),
                  1.75em 1.75em 0 0em rgba($ch-spinner1, .2),
                  0em 2.5em 0 0em rgba($ch-spinner1, .2),
                  -1.8em 1.8em 0 0em rgba($ch-spinner1, .5),
                  -2.6em 0em 0 0em rgba($ch-spinner1, .7),
                  -1.8em -1.8em 0 0em #7397FE;
    }
  }

</style>
