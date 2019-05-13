<template lang="pug">
  div.info-box
    section.popup-body_info
      span.info_process-name {{processName}}
      div.info_message Update status: {{progressStatus}}%
      
      div.info_progress-bar
        div.progress-bar_loading-line-box
          div(:style="{width:`${progressStatus}%`}").progress-bar_loading-line
    
    footer.popup-body_footer
        button(type="button" @click="bgMode" ).btn.btn--primary  Background mode
        //button(type="button" @click="cancelUpdate" ).btn.btn--dark-blue-rev  Cancel update
</template>

<script>
export default {
  name: 'PopupLoading',
  props: {
    processName: {                                // name loading process
      type: String,
      default: 'Updating Quantum Net software:'
    },
    progressStatus: {                             // updates progress (%)
      type: Number,
      default: 0
    },
    backgroundMode: {                            // hide update popup (stay only header)
      type: Boolean,
      default: false
    }
  },
  computed: {
    updateStatus() {
      return this.$store.state.globalView.updateStatus
    }
  },
  methods: {
    cancelUpdate() {
       this.$store.commit('globalView/SET_showPopupUpdates', false)
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


