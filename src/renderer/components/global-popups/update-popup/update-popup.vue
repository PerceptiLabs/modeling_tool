<template lang="pug">
  div(v-if="showPopupUpdates" :class="{'bg-mode' :  bgMode}").popup-body
    header.popup-body_header(@click="background")
      h3.header_title {{title}}
      span.header_update-status(v-if="updateStatus === 'downloading'") {{progress}}%
      span.header_update-status(v-if="updateStatus === 'done'") Done
    popup-loading(
      v-if="updateStatus === 'downloading'"
      :progressStatus="progress"
      @canceledUpdate="cancelUpdate"
      @backgroundMode="background"
    )
    popup-info(
      v-else
      @startedUpdate="startUpdate"
      @closedPopup="cancelUpdate"
      @restartApp="restartApp"
      :message="mainUpdateMessage"
      :aboutUpdateList="updateList"
      :updatePopupInfo="updateInfo"
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
      return this.$store.state.globalView.showPopupUpdates
    }
  },
  methods: {
    startUpdate(status) {
      this.$store.commit('globalView/SET_updateStatus', 'downloading')
      this.$emit('startedUpdate');
      //this.startFakeLoading();
    },
    cancelUpdate(cencel) {
      this.updateStatus = cencel.status;
      this.progress = 0;
      this.$emit('closedPopup')
      clearInterval(this.fakeTimer);
    },
    background() {
      this.bgMode = !this.bgMode;
    },
    closePopup() {
      this.$emit('closedPopup')
    },
    restartApp() {
      this.$emit('restartApp')
    },
    // startFakeLoading() {
    //   this.fakeTimer = setInterval( () => {
    //     this.progress = this.progress + 17;
    //     if (this.progress >= 100) {
    //       this.progress = 100;
    //       clearInterval(this.fakeTimer);
    //       this.updateStatus = 'done';
    //     }
    //   }, 700)
    // }
  }
}
</script>

<style lang="scss" scoped>
   @import '../../../scss/base';
   @import '../../../scss/components/update-popup';
</style>


