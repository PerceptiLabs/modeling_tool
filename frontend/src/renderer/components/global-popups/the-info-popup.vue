<template lang="pug">
  .popup-global
    .popup-global_overlay(@click="closePopup()")
    section.popup
      //.popup_tab-set
        .popup_header.active
      .popup_body
        .settings-layer_section.big-text(:class="{'popup--error': !isInfo}")
          .section_attention(:class="{'header_attention--error': !isInfo}") !
          .section_text
            p(v-if="isText && !comingSoonPopup") {{ popupText }}
            p(v-else-if="isText && comingSoonPopup") This feature is coming soon. For suggestions on new features, hit us up on:&ensp;
              a.btn.btn--link.text-primary(@click="goToLink('https://join.slack.com/t/perceptilabs-com/shared_invite/enQtODQ5NzAwNDkxOTExLWUxODAwZDk0MzA1MmM4OTViNWE4MmVjYjc2OTQwMTQ4N2NmM2ZlYmI5NjZjOWRiYjBkYjBjMTMzNjEyMDNiNDk')") slack
            div(v-else-if="coreNotFoundPopup && isWeb")
              p
                | It seems we can not find any running kernel on your local machine.
                | Download the kernel by "pip install perceptilabs" and then
                | start it by entering "perceptilabs" in the installed environment.
              div
                | For more information, visit &nbsp;
                button.btn.btn--link.text-primary(target="_blank" href="https://perceptilabs.com") https://perceptilabs.com
            ul.w-100(v-else)
              li(
                v-for="(text, i) in popupText"
                :key="i"
                ) {{ text }}

          .popup_clipboard(v-if="!coreNotFoundPopup")
            button.btn.btn--icon.icon.icon-clipboard-add(type="button"
              :class="styleClipboard"
              @click="copyClipboard")
      .popup_foot
        button.btn-info-popup(type="button"
        @click="closePopup") OK

</template>

<script>
  import { goToLink }    from '@/core/helpers.js'
  import {isWeb} from "@/core/helpers";
  export default {
    name: "TheInfoPopup",
    data() {
      return {
        styleClipboard: {
          'text-error': false,
          'text-primary': false
        },
        isWeb: isWeb(),
      }
    },
    computed: {
      infoPopup() {
        return this.$store.state.globalView.globalPopup.showInfoPopup
      },
      errorPopup() {
        return this.$store.state.globalView.globalPopup.showErrorPopup
      },
      comingSoonPopup() {
        return this.$store.state.globalView.globalPopup.ComingSoonPopup
      },
      coreNotFoundPopup() {
        return this.$store.state.globalView.globalPopup.coreNotFoundPopup
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
      goToLink,
      copyClipboard() {
        navigator.clipboard.writeText(JSON.stringify(this.popupText))
          .then((data)=> { this.styleClipboard['text-primary'] = true })
          .catch((err)=> { this.styleClipboard['text-error'] = true })
      },
      closePopup() {
        this.$store.commit('globalView/HIDE_allGlobalPopups');
      },
    }
  }
</script>

<style scoped lang="scss">
  @import "../../scss/base";
  @import "../../scss/common/info-popup";
  .popup_header {
    position: relative;
  }
  .settings-layer_section {
    display: flex;
    margin-top: 1.3rem;
    &.popup--error {
      .section_text {
        max-width: none;
      }
      white-space: pre;
    }
  }
  .section_text {
    margin: 0 1.5rem;
    width: 100%;
    max-width: 30rem;
    user-select: text;
    * {
      user-select: inherit;
    }
    /*&:selection {*/
    /*  background-color: cornflowerblue;*/
    /*}*/
  }
  .popup_clipboard {
    font-size: 1.6rem;
  }
  .popup_foot {
    justify-content: flex-end;
  }
</style>
