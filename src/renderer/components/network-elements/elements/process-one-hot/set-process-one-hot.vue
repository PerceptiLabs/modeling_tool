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
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          .settings-layer_section
            .form_row(v-tooltip-interactive:right="interactiveInfo")
              .form_label Number of classes:
              #tutorial_number-of-classes.form_input.tutorial-relative
                input(type="text" v-model="settings.N_class")

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
        :the-code="coreCode"
        )
    .settings-layer_foot
      button.btn.btn--primary(type="button" @click="saveSettings") Apply

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
import { mapActions } from 'vuex';

export default {
  name: 'SetProcessOneHot',
  mixins: [mixinSet],
  components: {
    SettingsCode
  },
  data() {
    return {
      tabs: ['Settings', 'Code'],
      settings: {
        N_class: '10',
      },
      interactiveInfo: {
        title: 'Number of classes',
        text: 'Set the number of classes in the data'
      }
    }
  },
  computed: {
    coreCode() {
      return `Y=tf.one_hot(tf.cast(X,dtype=tf.int32),${this.settings.N_class});`
    }
  },
  methods: {
    ...mapActions({
       tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    saveSettings() {
      this.applySettings();
      this.tutorialPointActivate({way:'next', validation: 'tutorial_number-of-classes'})
    }
  }
}
</script>
