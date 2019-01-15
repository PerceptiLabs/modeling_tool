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
      this.$emit('closedPopup')
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


