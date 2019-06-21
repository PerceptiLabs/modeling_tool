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
  name: 'SetProcessEmbed',
  mixins: [mixinSet],
  data() {
    return {
      tabs: ['Code'],
    }
  },
  computed: {
    settingsCode() {
      return `words = tf.string_split(X);
vocab_size=words.get_shape().as_list()[0];
embed_size=10;
embedding = tf.Variable(tf.random_uniform((vocab_size, embed_size), -1, 1));
Y = tf.nn.embedding_lookup(embedding, X)`
    }
  }
}
</script>
