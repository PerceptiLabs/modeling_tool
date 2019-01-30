<template lang="pug">
  div.info-box
    section.popup-body_info
      span.info_process-name {{processName}}
      div.info_message Update status: {{updateStatus}}%
      
      div.info_progress-bar
        div.progress-bar_loading-line-box
          div(:style="{width:`${updateStatus}%`}").progress-bar_loading-line
    
    footer.popup-body_footer
        button(type="button" @click="bgMode" ).btn.btn--primary  Background mode
        button(type="button" @click="cancelUpdate" ).btn.btn--dark-blue-rev  Cancel update
</template>

<script>
export default {
  name: 'PopupLoading',
  props: {
    processName: {                                // name loading process
      type: String,
      default: 'Updating Quantum Net software:'
    },
    updateStatus: {                               // updates progress (%)
      type: Number,
      default: 0
    },
    loadingStatus: {                              // loading Status ('before install', 'installing', 'done')
      type: String,
      default: 'before install'
    },
    backgroundMode: {                              // hide update popup (stay only header)
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      
    }
  },
  methods: {
    cancelUpdate() {
      this.$emit('canceledUpdate', {status: 'before install', show: false});
    },
    bgMode() {
      this.$emit('backgroundMode')
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../../scss/base';
  @import '../../../scss/components/update-popup';
</style>


