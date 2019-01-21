<template lang="pug">
  .loading-status.text-disable(:class="{'loading': isLoading}") Loading...
</template>
<script>
export default {
  name: 'ViewLoading',
  data(){
    return {

    }
  },
  computed: {
    isLoading() {
      return this.$store.state.mod_login.showLoader
    },
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

