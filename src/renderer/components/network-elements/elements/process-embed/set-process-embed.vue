<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
      )
        h3(v-html="tab")
    .popup_tab-body
      //-.popup_body(
        /:class="{'active': tabSelected == 0}"
        )
        .settings-layer
          .settings-layer_section
            .form_row
              .form_label Number of classes:
              .form_input
                input(type="text" v-model="settings.N_class")

          .settings-layer_foot
            button.btn.btn--primary(type="button"
            @click="applySettings"
            ) Apply

      .popup_body(
          :class="{'active': tabSelected == 0}"
        )
        settings-code(
          :the-code="coreCode"
        )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetProcessEmbed',
  mixins: [mixinSet],
  components: {
    SettingsCode
  },
  data() {
    return {
      tabs: ['Code'],
      // settings: {
      //   N_class: '10',
      // }
    }
  },
  computed: {
    coreCode() {
      return `
      words = tf.string_split(X);
      vocab_size=words.get_shape().as_list()[0];
      embed_size=10;
      embedding = tf.Variable(tf.random_uniform((vocab_size, embed_size), -1, 1));
      Y = tf.nn.embedding_lookup(embedding, X)`
    }
  }
}
</script>
