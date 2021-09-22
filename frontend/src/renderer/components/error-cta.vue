<template lang="pug">
  div.error-cta
    span Need help?
    | &nbsp;
    a.cta(@click="onClickCTA()") Contact Support
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: "ErrorCta",
  created() {},
  methods: {
    ...mapActions({
      trackIntercom: "mod_tracker/TRACK_toggleIntercom"
    }),
    onClickCTA() {
      if (!this.$intercom.visible) {
        this.trackIntercom({ action: "show" });
        this.$intercom.show();
      }
    }
  }
};
</script>
<style scoped>
.error-cta {
  font-size: 14px;
  line-height: 1.5;
}

.error-cta.small {
  font-size: 12px;
}

.cta {
  color: #b6c7fb;
  text-decoration: underline;
  cursor: pointer;
}
</style>
