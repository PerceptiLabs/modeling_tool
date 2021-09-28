<template lang="pug">
  .loading-status(:class="{'loading': isLoading}")
    .loading-status_box
      .box_line
</template>
<script>
export default {
  name: 'ViewLoading',
  props: {
    isLoading: {
      default: false,
      type: Boolean,
    }
  },
}
</script>
<style lang="scss" scoped>
  
  .loading-status {
    opacity: 0;
    margin-bottom: 1rem;
    &.loading {
      opacity: 1;
    }
  }
  .loading-status_box{
    background: $col-txt2;
    width: 100%;
    border-radius: 20px;
    position: relative;
    height: 0.4rem;
  }
  .box_line {
    width: 0;
    height: 100%;
    position: absolute;
    left: 0;
    top: 0;
    background: $color-6;
    border-radius: 10px;
    .loading & {
      animation: loading 2s infinite;
    }
  }
  @keyframes loading {
    from {width: 0;}
    to {width: 100%;}
  }
</style>

