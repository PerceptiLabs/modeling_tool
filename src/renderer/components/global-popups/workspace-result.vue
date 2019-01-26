<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup_tab-set
        .popup_header.active
          h3 Result
      .popup_body
        .settings-layer_section



      .popup_foot
        button.btn.btn--primary(type="button"
          @click="closePopup()") Cancel
        button.btn.btn--primary(type="button"
          @click="runTest()") Run test
</template>

<script>
export default {
  name: "GeneralResult",
  data() {
    return {

    }
  },
  computed: {

  },
  methods: {
    runTest() {
      this.closePopup();
      //this.$store.dispatch('mod_workspace/SET_netMode', 'training');
    },
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
      this.$store.dispatch('mod_workspace/SET_netMode', 'edit');
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
