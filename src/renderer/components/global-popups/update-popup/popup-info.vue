<template lang="pug">
  div.info-box
    section.popup-body_info
      span.info_process-name {{time}}
      div.info_message(v-if="updateStatus === 'not update'") You are using the latest version of the application
      div.info_message(v-if="updateStatus === 'done'") A new version has been downloaded. Restart the application to apply the updates
      div.info_message(v-else) {{updatePopupInfo.path}}
      
      template(v-if="updateStatus === 'before update'")
        button(type="button" 
          @click="isShowUpdateList = !isShowUpdateList").info_about-update-btn What's new?
        ul(v-show="isShowUpdateList").info_about-update-list
          //li(v-for="(item, index) in aboutUpdateList").about-update-list_item {{item}}
          li.about-update-list_item {{updatePopupInfo.path}} - version {{updatePopupInfo.version}}

    footer.popup-body_footer
      template(v-if="updateStatus === 'done'")
        button(type="button" @click="restartApp" ).btn.btn--primary  Restart
        button(type="button" @click="closeUpdatePopup" ).btn.btn--dark-blue-rev  Later
      template(v-if="updateStatus === 'not update'")
        button(type="button" @click="closeWithoutUpdate" ).btn.btn--primary  Ok
      template(v-if="updateStatus === 'before update'")
        button(type="button" @click="startUpdate" ).btn.btn--primary  Install
        button(type="button" @click="closeUpdatePopup" ).btn.btn--dark-blue-rev  Cancel
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
    updatePopupInfo: {                    // info about update (property from update-popup.vue)
      type: Object
    }
  },
  data() {
    return {
      isShowUpdateList: false
    }
  },
  computed: {
    updateStatus() {
      return this.$store.state.globalView.updateStatus
    }
  },
  methods: {
    startUpdate() {
      this.$store.commit('globalView/SET_updateStatus', 'downloading')
      this.$emit('startedUpdate')
    },
    closeUpdatePopup() {
      this.$store.commit('globalView/SET_showPopupUpdates', false)
    },
    restartApp () {
      this.$emit('restartApp')
    },
    closeWithoutUpdate () {
      this.$store.commit('globalView/SET_showPopupUpdates', false)
      this.$store.commit('globalView/SET_updateStatus', 'before update')
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../../scss/base';
  @import '../../../scss/components/update-popup';
</style>


