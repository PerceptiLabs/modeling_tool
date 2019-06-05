<template lang="pug">
  net-base-settings(:tab-set="tabs")
    template(slot="Code-content")
      settings-code(:the-code="coreCode")

    template(slot="action")
      button.btn.btn--primary(type="button" @click="applySettings") Apply
</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetProcessGrayscale',
  mixins: [mixinSet],
  data() {
    return {
      tabs: ['Code'],
      settings: {}
    }
  },
  computed: {
    coreCode() {
      return `Y=tf.image.rgb_to_grayscale(X);`
    }
  }
}
</script>
