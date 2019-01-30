<template lang="pug">
  div(v-if="isShowPopup").popup-body
    header.popup-body_header
      h3.header_title {{title}}
      span.header_update-status(v-if="updatesLoading") {{progress}}%
    popup-loading(
      v-if="loadingStatus === 'installing'"
      :updateStatus="progress"
      @canceledUpdate="cancel"
      :loadingStatus="loadingStatus"
    )
    popup-info(
      v-else
      @installStarted="install"
      @closedPopup="cancel"
      :aboutUpdateList="updateList"
      :message="mainUpdateMessage"
      :loadingStatus="loadingStatus"
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
  },
  data() {
    return {
      title: 'Software update',
      updatesLoading: false,
      loadingStatus: 'before install',
      progress: 0,
      mainUpdateMessage: 'Availible 5 new update',
      updateList: [
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
      ]
    }
  },
  methods: {
    install(loadingStatus) {
      this.loadingStatus = loadingStatus;
      this.$emit('updateStarted', loadingStatus);
      //this.startFakeLoading();
    },
    cancel(cencel) {
      this.loadingStatus = cencel.status;
      this.progress = 0;
      this.$emit('closedPopup')
      clearInterval(this.fakeTimer);
    },
    closePopup() {
      this.$emit('closedPopup')
    },
    startFakeLoading() {
      this.fakeTimer = setInterval( () => {
        this.progress = this.progress + 17;
        if (this.progress >= 100) {
          this.progress = 100;
          clearInterval(this.fakeTimer);
          this.loadingStatus = 'done';
          console.log(this.loadingStatus);
        }
      }, 700)
    }
  }
}
</script>

<style lang="scss" scoped>
   @import '../../../scss/base';
   @import '../../../scss/components/update-popup';
</style>


