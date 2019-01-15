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
  components: {
    PopupInfo,
    PopupLoading
  },
  name: 'UpdatePopup',
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
      this.startFakeLoading();
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

  .popup-body {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: $bg-toolbar;
    z-index: 100;
    width: 40rem;
    border-radius: 0.5rem;
    overflow: hidden;
    padding-bottom: 1rem; 
  }
  .popup-body_header {
    background: $col-txt2;
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    font-size: 1.4rem;
  }
  .header_title {
    font-size: 1.4rem;
    color: $col-txt;
    margin: 0;
  }

  .popup-body_info {
    padding: 2rem 1.5rem 3rem 1.5rem;
  }
  .info_process-name {
    color: $col-placeholder;
    margin-bottom: 1rem;
    display: block;
    font-size: 1.2rem;
  }
  .info_message {
    font-size: 1.2rem;
  }

  .info_progress-bar {
    margin: 1rem 0;
  }
  .progress-bar_update-status {
    font-size: 1.2rem;
    display: block;
    margin-bottom: 2rem;
  }
  .progress-bar_loading-line-box {
    background:#535b71;
    border-radius: .5rem;
    width: 100%;
    height: 2rem;

  }
  .progress-bar_loading-line {
    background: linear-gradient(#73FEBB, #61E6EE);
    width: 28%;
    height: inherit;
    border-radius: .5rem;
    transition: width .5s linear;
  }

  .info_about-update-btn {
    background: none;
    padding: 0.5rem 0;
    margin: 0.5rem 0;
    text-decoration: underline;
  }
  .about-update-list_item {
    margin-bottom: 1rem;
    line-height: 1.4rem;
    font-size: 1rem;

    &:before {
      content: '-';
      margin-right: 0.5rem;
    }
  }

  .popup-body_footer {
    padding: 0 1.5rem;
    margin-bottom: 1rem;
    button{
      min-width: 12rem;
      display: inline-block;
      height: auto;
      padding: .65em .5em;
      margin-right: 1rem;
    }
  }
</style>


