<template lang="pug">
  .info-box
    .popup-body_info
      div.info_message(v-if="updateStatus === 'not update'") You are using the latest version of the application
      div.info_message(v-else-if="updateStatus === 'done'") A new version has been downloaded. Restart the application to apply the updates
      div.info_message(v-else) PerceptiLabs {{ updateInfo.version }} is now available!

      template(v-if="updateStatus === 'before update' && releaseNotes")
        button.info_about-update-btn(type="button"
          @click="isShowUpdateList = !isShowUpdateList") What's new:
        template(v-if="isShowUpdateList")
          ul.info_about-update-list(v-if="releaseNotes.features")
            li.about-update-list_item(
              v-for="(item, index) in releaseNotes.features"
              :key="item.index"
              ) {{item}}
          template(v-if="releaseNotes.bugs")
            .info_about-update-btn What's fixed:
            ul.info_about-update-list
              li.about-update-list_item(
                v-for="(item, index) in releaseNotes.bugs"
                :key="item.index"
              ) {{item}}


    footer.popup-body_footer
      template(v-if="updateStatus === 'not update'")
        button.btn.btn--primary(type="button" @click="closeUpdatePopup" ) Ok

      template(v-if="updateStatus === 'before update'")
        button.btn.btn--primary(type="button" @click="startUpdate" ) Install
        button.btn.btn--dark-blue-rev(type="button" @click="closeUpdatePopup" ) Cancel

      template(v-if="updateStatus === 'done'")
        button.btn.btn--primary(type="button" @click="restartApp" ) Restart
        button.btn.btn--dark-blue-rev(type="button" @click="closeUpdatePopup" ) Later

</template>
<script>
//import {ipcRenderer}  from 'electron'

export default {
  name: 'PopupInfo',
  data() {
    return {
      isShowUpdateList: false
    }
  },
  computed: {
    updateStatus() {
      return this.$store.state.mod_autoUpdate.updateStatus
    },
    updateInfo() {
      return this.$store.state.mod_autoUpdate.updateInfo
    },
    releaseNotes() {
      return this.$store.getters['mod_autoUpdate/GET_releaseNotes']
    },
  },
  methods: {
    startUpdate() {
      this.$store.commit('mod_autoUpdate/SET_updateStatus', 'downloading');
      //ipcRenderer.send('update-start')
    },
    closeUpdatePopup() {
      this.$store.commit('mod_autoUpdate/SET_showPopupUpdates', false)
    },
    restartApp () {
      //ipcRenderer.send('restart-app-after-update')
    },
  }
}
</script>

<style lang="scss" scoped>
  @import '../../../scss/base';
  @import '../../../scss/components/update-popup';
</style>


