<template lang="pug">
  .request-loader-wrapper
    .request-loader-wrapper_background-box(v-if="showSpinner")
      .background-box_spinner
    slot
</template>

<script>

export default {
  name: "RequestSpinner",
  props: {
    showSpinner: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {

    }
  },
  methods: {

  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .request-loader-wrapper{
    position: relative;
    min-height: 9rem;
    width: 100%;
    height: 100%;
  }
  .request-loader-wrapper_background-box {
    position: absolute;
    width: 100%;
    height: 100%;
    min-height: 2rem;
    top: 0;
    left: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 5;
  }
  .background-box_spinner {
    margin: 0 auto;
    font-size: .9rem;
    width: 1em;
    height: 1em;
    border-radius: 50%;
    position: relative;
    text-indent: -9999em;
    animation: load5 1.1s infinite ease;
    transform: translateZ(0);
  }
  @-webkit-keyframes load5 {
    0%,
    100% {
      box-shadow: 0em -2.6em 0em 0em #93AFFF, 1.8em -1.8em 0 0em rgba(79, 113, 215, 0.2), 2.5em 0em 0 0em rgba(79, 113, 215, 0.2), 1.75em 1.75em 0 0em rgba(79, 113, 215, 0.2), 0em 2.5em 0 0em rgba(79, 113, 215, 0.2), -1.8em 1.8em 0 0em rgba(79, 113, 215, 0.2), -2.6em 0em 0 0em rgba(79, 113, 215, 0.5), -1.8em -1.8em 0 0em rgba(79, 113, 215, 0.7);
    }
    12.5% {
      box-shadow: 0em -2.6em 0em 0em rgba(79, 113, 215, 0.7), 1.8em -1.8em 0 0em #6185EE, 2.5em 0em 0 0em rgba(79, 113, 215, 0.2), 1.75em 1.75em 0 0em rgba(79, 113, 215, 0.2), 0em 2.5em 0 0em rgba(79, 113, 215, 0.2), -1.8em 1.8em 0 0em rgba(79, 113, 215, 0.2), -2.6em 0em 0 0em rgba(79, 113, 215, 0.2), -1.8em -1.8em 0 0em rgba(79, 113, 215, 0.5);
    }
    25% {
      box-shadow: 0em -2.6em 0em 0em rgba(79, 113, 215, 0.5), 1.8em -1.8em 0 0em rgba(79, 113, 215, 0.7), 2.5em 0em 0 0em #4D73E1, 1.75em 1.75em 0 0em rgba(79, 113, 215, 0.2), 0em 2.5em 0 0em rgba(79, 113, 215, 0.2), -1.8em 1.8em 0 0em rgba(79, 113, 215, 0.2), -2.6em 0em 0 0em rgba(79, 113, 215, 0.2), -1.8em -1.8em 0 0em rgba(79, 113, 215, 0.2);
    }
    37.5% {
      box-shadow: 0em -2.6em 0em 0em rgba(79, 113, 215, 0.2), 1.8em -1.8em 0 0em rgba(79, 113, 215, 0.5), 2.5em 0em 0 0em rgba(79, 113, 215, 0.7), 1.75em 1.75em 0 0em #3C61CD, 0em 2.5em 0 0em rgba(79, 113, 215, 0.2), -1.8em 1.8em 0 0em rgba(79, 113, 215, 0.2), -2.6em 0em 0 0em rgba(79, 113, 215, 0.2), -1.8em -1.8em 0 0em rgba(79, 113, 215, 0.2);
    }
    50% {
      box-shadow: 0em -2.6em 0em 0em rgba(79, 113, 215, 0.2), 1.8em -1.8em 0 0em rgba(79, 113, 215, 0.2), 2.5em 0em 0 0em rgba(79, 113, 215, 0.5), 1.75em 1.75em 0 0em rgba(79, 113, 215, 0.7), 0em 2.5em 0 0em #98B2FF, -1.8em 1.8em 0 0em rgba(79, 113, 215, 0.2), -2.6em 0em 0 0em rgba(79, 113, 215, 0.2), -1.8em -1.8em 0 0em rgba(79, 113, 215, 0.2);
    }
    62.5% {
      box-shadow: 0em -2.6em 0em 0em rgba(79, 113, 215, 0.2), 1.8em -1.8em 0 0em rgba(79, 113, 215, 0.2), 2.5em 0em 0 0em rgba(79, 113, 215, 0.2), 1.75em 1.75em 0 0em rgba(79, 113, 215, 0.5), 0em 2.5em 0 0em rgba(79, 113, 215, 0.7), -1.8em 1.8em 0 0em #93AFFF, -2.6em 0em 0 0em rgba(79, 113, 215, 0.2), -1.8em -1.8em 0 0em rgba(79, 113, 215, 0.2);
    }
    75% {
      box-shadow: 0em -2.6em 0em 0em rgba(79, 113, 215, 0.2), 1.8em -1.8em 0 0em rgba(79, 113, 215, 0.2), 2.5em 0em 0 0em rgba(79, 113, 215, 0.2), 1.75em 1.75em 0 0em rgba(79, 113, 215, 0.2), 0em 2.5em 0 0em rgba(79, 113, 215, 0.5), -1.8em 1.8em 0 0em rgba(79, 113, 215, 0.7), -2.6em 0em 0 0em #86A5FF, -1.8em -1.8em 0 0em rgba(79, 113, 215, 0.2);
    }
    87.5% {
      box-shadow: 0em -2.6em 0em 0em rgba(79, 113, 215, 0.2), 1.8em -1.8em 0 0em rgba(79, 113, 215, 0.2), 2.5em 0em 0 0em rgba(79, 113, 215, 0.2), 1.75em 1.75em 0 0em rgba(79, 113, 215, 0.2), 0em 2.5em 0 0em rgba(79, 113, 215, 0.2), -1.8em 1.8em 0 0em rgba(79, 113, 215, 0.5), -2.6em 0em 0 0em rgba(79, 113, 215, 0.7), -1.8em -1.8em 0 0em #7397FE;
    }
  }

</style>
