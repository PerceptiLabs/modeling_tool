<template lang="pug">
  .popup-global(v-if="infoText")
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup_tab-set
        .popup_header.active
          h3 Info
      .popup_body
        .settings-layer_section.text-center
          p.middle-text {{ infoText }}
      .popup_foot
        button.btn.btn--primary(type="button"
        @click="closePopup()") OK

</template>

<script>
  export default {
    name: "TheInfoPopup",
    data() {
      return {
      }
    },
    computed: {
      infoText() {
        return this.$store.state.globalView.globalPopup.showInfoPopup
      },
    },
    methods: {
      closePopup() {
        this.$store.commit('globalView/HIDE_allGlobalPopups');
      }
    }
  }
</script>