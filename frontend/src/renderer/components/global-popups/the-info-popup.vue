<template lang="pug">
  .popup-global(v-if="isShowPopup")
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup_tab-set
        .popup_header.active
          .header_attention(:class="{'header_attention--error': !isInfo}") !
      .popup_body
        .settings-layer_section
          p.middle-text.text-center(v-if="isText") {{ popupText }}
          ul(v-else)
            li(
              v-for="(text, i) in popupText"
              :key="i"
              ) {{ text }}
      .popup_foot
        button.btn-info-popup(type="button"
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
      infoPopup() {
        return this.$store.state.globalView.globalPopup.showInfoPopup
      },
      errorPopup() {
        return this.$store.state.globalView.globalPopup.showErrorPopup
      },
      isShowPopup() {
        return this.errorPopup.length || this.infoPopup.length
      },
      isText() {
        return typeof this.popupText === 'string'
      },
      isInfo() {
        return !!(this.isShowPopup && this.infoPopup.length);
      },
      popupText() {
        return this.isInfo
          ? this.infoPopup
          : this.errorPopup;
      }
    },
    methods: {
      closePopup() {
        this.$store.commit('globalView/HIDE_allGlobalPopups');
      }
    }
  }
</script>

<style scoped lang="scss">
  @import "../../scss/base";
  @import "../../scss/common/infoPopup";
</style>