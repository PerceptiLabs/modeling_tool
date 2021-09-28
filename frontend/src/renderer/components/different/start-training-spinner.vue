<template lang="pug">
  .wrapper-training-loader
    .wrapper-training-loader_spinner
      .round
</template>

<script>
  export default {
    name: "StartTrainingSpinner",
  }
</script>

<style lang="scss" scoped>
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
    content: '';
    border-radius: 50%;
    display: block;
    height: 12px;
    width: 12px;
    z-index: 1;
  }

  $spinner1: #7397FE;
  $spinner2: #FE7373;
  $spinner3: #61E6EE;
  $spinner4: #FECF73;
  .wrapper-training-loader_spinner:before {
    animation: ball 2s infinite;
    box-shadow: 0px -34px 0 $spinner1,    34px 0 0 $spinner2,     -34px 0 0 $spinner2,      0px 34px 0 $spinner3,
                24px -24px 0 $spinner4,   24px 24px 0 $spinner2,  -24px -24px 0 $spinner1,  -24px 24px 0 $spinner1;
  }

  @keyframes rotate {
    0% {
      transform: rotate(0deg) scale(.8);
    }
    50% {
      transform: rotate(360deg) scale(1.2);
    }
    100% {
      transform: rotate(720deg) scale(.8);
    }
  }

  @keyframes ball {
    0% {
      box-shadow: 0px -34px 0 $spinner1,  34px 0 0 $spinner2,     -34px 0 0 $spinner2,      0px 34px 0 $spinner3,
                  24px -24px 0 $spinner4, 24px 24px 0 $spinner2,  -24px -24px 0 $spinner1,  -24px 24px 0 $spinner1;
    }
    50% {
      box-shadow: 0 0 0 $spinner1, 0 0 0 $spinner2, 0 0 0 $spinner2, 0 0 0 $spinner3,
                  0 0 0 $spinner4, 0 0 0 $spinner2, 0 0 0 $spinner1, 0 0 0 $spinner1;
    }
    100% {
      box-shadow: 0px -34px 0 $spinner1,  34px 0 0 $spinner2,     -34px 0 0 $spinner2,      0px 34px 0 $spinner3,
                  24px -24px 0 $spinner4, 24px 24px 0 $spinner2,  -24px -24px 0 $spinner1,  -24px 24px 0 $spinner1;
    }
  }

</style>
