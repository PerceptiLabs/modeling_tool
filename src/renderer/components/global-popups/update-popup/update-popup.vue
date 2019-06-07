<template lang="pug">
  section.popup-body(v-if="showPopupUpdates" :class="{'bg-mode': bgMode}")
    header.popup-body_header(@click="toggleBgMode")
      h3.header_title Software update
      span.header_update-status(v-if="updateStatus === 'downloading'") {{progress}}%
      span.header_update-status(v-if="updateStatus === 'done'") Done
    popup-loading(
      v-if="updateStatus === 'downloading'"
      :progress-status="progress"
      @background-mode="toggleBgMode"
    )
    popup-info(v-else)
</template>

<script>
import PopupInfo      from '@/components/global-popups/update-popup/popup-info.vue'
import PopupLoading   from '@/components/global-popups/update-popup/popup-loading.vue'

export default {
  name: 'PopupUpdate',
  components: {PopupInfo, PopupLoading},
  data() {
    return {
      updatesLoading: false,
      bgMode: false,
    }
  },
  computed: {
    updateStatus() {
      return this.$store.state.mod_autoUpdate.updateStatus
    },
    showPopupUpdates() {
      return this.$store.state.mod_autoUpdate.showPopupUpdates
    },
    updateProgress() {
      return this.$store.state.mod_autoUpdate.updateProgress
    },
  },
  methods: {
    toggleBgMode() {
      this.bgMode = !this.bgMode;
    },
  }
}
</script>

<style lang="scss" scoped>
   @import '../../../scss/base';
   @import '../../../scss/components/update-popup';
</style>


