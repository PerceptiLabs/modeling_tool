<template lang="pug">
  .theme-button(@click="onClick") 
    img(v-if="value" src="../../../../static/img/icon-light-theme.svg" alt="white")
    img(v-else src="../../../../static/img/icon-dark-theme.svg" alt="dark")
    
</template>

<script>
export default {
  name: 'BaseSwitchTheme',

  props: {
    value: Boolean,
    onClick: {
      type: Function,
      default: () => {},
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
