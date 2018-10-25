<template lang="pug">
  ul.action-list
    li
      button.action-list_btn(type="button")
        span.action-list_btn-text Copy properties
        span I
    li
      button.action-list_btn(type="button")
        span.action-list_btn-text Paste properties
        span O
    li
      button.action-list_btn(type="button")
        span.action-list_btn-text Transform
        span Y
    li
      button.action-list_btn(type="button")
        span.action-list_btn-text F_1
        span F
    li
      button.action-list_btn(type="button")
        span.action-list_btn-text F_2
        span J
    li
      button.action-list_btn(type="button")
        span.action-list_btn-text F_3
        span L
</template>

<script>
export default {
  name: 'NetContextMenu',
  data() {
    return {

    }
  },
  methods: {

  }
}
</script>

<style lang="scss" scoped>

</style>
