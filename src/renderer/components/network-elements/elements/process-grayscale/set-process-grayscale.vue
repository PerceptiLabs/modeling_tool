<template lang="pug">
  net-base-settings(
    :tab-set="tabs"
    :current-el="currentEl"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
  )
    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        v-model="coreCode"
      )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';

export default {
  name: 'SetProcessGrayscale',
  mixins: [mixinSet],
  data() {
    return {
      tabs: ['Code'],
    }
  },
  computed: {
    codeDefault() {
      return {
        Output: `Y=tf.image.rgb_to_grayscale(X['Y']);`
      }
    }
  }
}
</script>
