<template lang="pug">
  div
    section.popup-body_info
      span.info_process-name {{time}}
      div.info_message(v-if="loadingStatus === 'done'") Don't have any updates
      div.info_message(v-else) {{message}}
      
      template(v-if="loadingStatus === 'before install'")
        button(type="button" 
          @click="isShowUpdateList = !isShowUpdateList").info_about-update-btn What's new?
        ul(v-show="isShowUpdateList").info_about-update-list
          li(v-for="(item, index) in aboutUpdateList").about-update-list_item {{item}}

    footer.popup-body_footer
      button(type="button" @click="closePopup" v-if="loadingStatus === 'done'").btn.btn--primary  Ok
      button(type="button" @click="installUpdates" v-else).btn.btn--primary  Install
</template>
<script>
export default {
  name: 'PopupInfo',
  props: {
    time: {
      type: String,                       // updates time
      default: ''
    },
    message: {                            // main updates info
      type: String,
      default: 'Availible 1 new update'
    },
    aboutUpdateList: {                    // all updates info (after click 'What's new?' button)
      type: Array,
      default() {
        return []
      }
    },
    loadingStatus: {                      // loding Status ('before install', 'installing', 'done')
      type: String,
      default: 'before install'
    }
  },
  data() {
    return {
      isInstallUpdates: false,
      isNewUpdates: true,
      isShowUpdateList: false
    }
  },
  methods: {
    installUpdates() {
      this.$emit('installStarted', 'installing')
    },
    closePopup() {
      this.$emit('closedPopup');
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../../scss/base';
  @import '../../../scss/components/update-popup';
</style>


