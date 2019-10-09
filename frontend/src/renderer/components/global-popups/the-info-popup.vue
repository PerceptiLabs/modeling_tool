<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      .popup_tab-set
        .popup_header.active
          .header_attention(:class="{'header_attention--error': !isInfo}") !
      .popup_body
        .settings-layer_section.big-text
          p.text-center(v-if="isText") {{ popupText }}
          ul(v-else)
            li(
              v-for="(text, i) in popupText"
              :key="i"
              ) {{ text }}
          button.popup_clipboard.btn.btn--icon.icon.icon-clipboard-add(type="button"
            :class="styleClipboard"
            @click="copyClipboard")
      .popup_foot
        button.btn-info-popup(type="button"
        @click="closePopup") OK

</template>

<script>
  export default {
    name: "TheInfoPopup",
    data() {
      return {
        styleClipboard: {
          'text-error': false,
          'text-primary': false
        }
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
      copyClipboard() {
        navigator.clipboard.writeText(JSON.stringify(this.popupText))
          .then((data)=> { this.styleClipboard['text-primary'] = true })
          .catch((err)=> { this.styleClipboard['text-error'] = true })
      },
      closePopup() {
        this.$store.commit('globalView/HIDE_allGlobalPopups');
      }
    }
  }
</script>

<style scoped lang="scss">
  @import "../../scss/base";
  @import "../../scss/common/infoPopup";
  .settings-layer_section {
    position: relative;
  }
  .popup_clipboard {
    position: absolute;
    top: -1rem;
    right: 1rem;
    font-size: 1.6rem;
  }
</style>
