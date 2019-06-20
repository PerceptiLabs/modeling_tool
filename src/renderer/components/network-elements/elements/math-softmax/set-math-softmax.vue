<template lang="pug">
  net-base-settings(
    :tab-set="tabs"
    @press-apply="saveSettings($event)"
  )
    template(slot="Code-content")
      settings-code(v-model="coreCode")

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetMathSoftmax',
  mixins: [mixinSet],
  data() {
    return {
      tabs: ['Code'],
    }
  },
  computed: {
    settingsCode() {
      return `Y=tf.nn.softmax(X);`
    }
  }
}
</script>
