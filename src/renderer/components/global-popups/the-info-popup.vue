<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup_tab-set
        .popup_header.active
          h3 Info
      .popup_body
        .settings-layer_section.text-center
          p {{ infoText }}
      .popup_foot
        button.btn.btn--primary(type="button"
        @click="closePopup()") OK

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  export default {
    name: "TheInfoPopup",
    mixins: [mixinSet],
    props: {
      infoText: {
        type: [Boolean, String],
        default: ''
      }
    },
    data() {
      return {
      }
    },
    methods: {
      closePopup() {
        this.$store.commit('globalView/HIDE_allGlobalPopups');
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>
