<template lang="pug">
  .info-box
    .popup-body_info
      span.info_process-name Updating Quantum Net software:
      .info_message Update status: {{progressStatus}}%
      
      .info_progress-bar
        .progress-bar_loading-line(:style="{width:`${progressStatus}%`}")
    
    footer.popup-body_footer
        button.btn.btn--primary(type="button" @click="bgMode" ) Background mode
        //button(type="button" @click="cancelUpdate" ).btn.btn--dark-blue-rev  Cancel update
</template>

<script>
export default {
  name: 'PopupLoading',
  props: {
    progressStatus: {                             // updates progress (%)
      type: Number,
      default: 0
    },
  },
  methods: {
    cancelUpdate() {
       this.$store.commit('globalView/SET_showPopupUpdates', false)
    },
    bgMode() {
      this.$emit('background-mode')
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../../scss/base';
  @import '../../../scss/components/update-popup';
</style>


