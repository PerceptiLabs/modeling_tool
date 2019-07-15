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
  .popup-global{
    z-index: 13;
  }

  .popup-global .popup{
    background: $bg-workspace;
    border: 1px solid #495163;
    box-shadow: 0 0 7px 3px #4a484880;
  }
  .popup_header{
    background: transparent;
    height: 5rem;
    padding-top: 1.4rem;
  }
  .header_attention {
    color: #fff;
    background: $color-6;
    padding: 0.3rem 1.1rem;
    font-weight: bold;
    font-size: 1.6rem;
    text-align: center;
    border-radius: 50%;
  }
  .header_attention--error {
    background: $col-warning;
  }
  .popup_body p{
    font-size: 1.5rem;
  }
</style>