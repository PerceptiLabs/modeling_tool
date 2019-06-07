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
  name: 'SetProcessEmbed',
  mixins: [mixinSet],
  data() {
    return {
      tabs: ['Code'],
    }
  },
  computed: {
    coreCode() {
      return `words = tf.string_split(X);
vocab_size=words.get_shape().as_list()[0];
embed_size=10;
embedding = tf.Variable(tf.random_uniform((vocab_size, embed_size), -1, 1));
Y = tf.nn.embedding_lookup(embedding, X)`
    }
  }
}
</script>
