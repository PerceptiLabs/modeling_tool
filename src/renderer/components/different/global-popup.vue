<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closeGlobalSet()")
    section.popup
      .popup_tab-set
        .popup_header.active
          h3
            slot(name="title")
      .popup_body
        slot
</template>

<script>
export default {
  name: "",
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
