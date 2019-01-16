<template lang="pug">
  .loading-status.text-disable Loading...
</template>
<script>
export default {
  name: 'ViewLoading',
  data(){
    return {

    }
  }
}
</script>
<style lang="scss" scoped>
  .loading-status{
    font-size: 5rem;
    font-weight: 200;
    opacity: 0;
    &.loading{
      opacity: 1;
    }
  }
</style>

