<template lang="pug">
  div(v-if="showPopupUpdates" :class="{'bg-mode' :  bgMode}").popup-body
    header.popup-body_header(@click="background")
      h3.header_title {{title}}
      span.header_update-status(v-if="updateStatus === 'downloading'") {{progress}}%
      span.header_update-status(v-if="updateStatus === 'done'") Done
    popup-loading(
      v-if="updateStatus === 'downloading'"
      :progress-status="progress"
      @canceled-update="cancelUpdate"
      @background-mode="background"
    )
    popup-info(
      v-else
      @started-update="startUpdate"
      @closed-popup="cancelUpdate"
      @restart-app="restartApp"
      :message="mainUpdateMessage"
      :about-update-list="updateList"
      :update-popup-info="updateInfo"
    )
</template>

<script>
import PopupInfo      from '@/components/global-popups/update-popup/popup-info.vue'
import PopupLoading   from '@/components/global-popups/update-popup/popup-loading.vue'

export default {
  name: 'PopupUpdate',
  components: {PopupInfo, PopupLoading},
  props: {
    isShowPopup: {                  // show update popup
      type: Boolean,
      default: true
    },
    progress: {                     // progress (%)
      type: Number,
      default: 0
    },
    updateInfo: {                   // info about update (property from App.vue)
      type: Object,
      default: {}
    }
  },
  data() {
    return {
      title: 'Software update',
      updatesLoading: false,
      bgMode: false,
      mainUpdateMessage: 'Availible 5 new update',
      updateList: [
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
      ]
    }
  },
  computed: {
    updateStatus() {
      return this.$store.state.globalView.updateStatus
    },
    showPopupUpdates() {
      return this.$store.state.globalView.globalPopup.showPopupUpdates
    }
  },
  methods: {
    startUpdate() {
      this.$store.commit('globalView/SET_updateStatus', 'downloading')
      this.$emit('started-update');
    },
    cancelUpdate(cancel) {
      this.updateStatus = cancel.status;
      this.progress = 0;
      this.$emit('closed-popup');
      clearInterval(this.fakeTimer);
    },
    background() {
      this.bgMode = !this.bgMode;
    },
    closePopup() {
      this.$emit('closed-popup')
    },
    restartApp() {
      this.$emit('restart-app')
    },
  }
}
</script>

<style lang="scss" scoped>
   @import '../../../scss/base';
   @import '../../../scss/components/update-popup';
</style>


