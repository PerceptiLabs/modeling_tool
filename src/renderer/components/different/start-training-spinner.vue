<template lang="pug">
  .wrapper-training-loader(v-if="showSpinner")
    .wrapper-training-loader_spinner
      .round
</template>

<script>

  export default {
    name: "StartTrainingSpinner",
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
  }
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .wrapper-training-loader {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    background: $bg-workspace;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10;
  }

  .wrapper-training-loader_spinner  {
    animation: rotate 2s infinite;
    height: 8rem;
    width: 8rem;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
  }
  .round{
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    border-radius: 50%;
  }

  .wrapper-training-loader_spinner:before{
    border-radius: 50%;
    content: '';
    display: block;
    height: 12px;
    width: 12px;
    z-index: 1;
  }
  .wrapper-training-loader_spinner:before {
    animation: ball 2s infinite;
    //background-color: greenyellow;
    box-shadow: 0px -34px 0 #7397FE, 34px 0 0 #FE7373, -34px 0 0 #FE7373, 0px 34px 0 #61E6EE,
                24px -24px 0 #FECF73, 24px 24px 0 #FE7373, -24px -24px 0 #7397FE, -24px 24px 0 #7397FE,
  }

  @keyframes rotate {
    0% {
      -webkit-transform: rotate(0deg) scale(0.8);
      -moz-transform: rotate(0deg) scale(0.8);
    }
    50% {
      -webkit-transform: rotate(360deg) scale(1.2);
      -moz-transform: rotate(360deg) scale(1.2);
    }
    100% {
      -webkit-transform: rotate(720deg) scale(0.8);
      -moz-transform: rotate(720deg) scale(0.8);
    }
  }

  @keyframes ball {
    0% {
      box-shadow: 0px -34px 0 #7397FE, 34px 0 0 #FE7373, -34px 0 0 #FE7373, 0px 34px 0 #61E6EE,
                  24px -24px 0 #FECF73, 24px 24px 0 #FE7373, -24px -24px 0 #7397FE, -24px 24px 0 #7397FE,
    }
    50% {
      box-shadow: 0 0 0 #7397FE, 0 0 0 #FE7373, 0 0 0 #FE7373, 0 0 0 #61E6EE,
                  0 0 0 #FECF73, 0 0 0 #FE7373, 0 0 0 #7397FE, 0 0 0 #7397FE
    }
    100% {
      box-shadow: 0px -34px 0 #7397FE, 34px 0 0 #FE7373, -34px 0 0 #FE7373, 0px 34px 0 #61E6EE,
                  24px -24px 0 #FECF73, 24px 24px 0 #FE7373, -24px -24px 0 #7397FE, -24px 24px 0 #7397FE,
    }
  }

</style>
