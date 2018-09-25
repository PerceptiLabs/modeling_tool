<template lang="pug">
  ul.context-menu
    li
      button.context-menu_btn(type="button")
        span.context-menu_btn-text Copy properties
        span I
    li
      button.context-menu_btn(type="button")
        span Paste properties
        span O
    li
      button.context-menu_btn(type="button")
        span Transform
        span Y
    li
      button.context-menu_btn(type="button")
        span F_1
        span F
    li
      button.context-menu_btn(type="button")
        span F_2
        span J
    li
      button.context-menu_btn(type="button")
        span F_3
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
