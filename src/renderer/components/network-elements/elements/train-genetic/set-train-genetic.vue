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
            .form_row
              .form_label Population:
              .form_input
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Generations:
              .form_input
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Retain:
              .form_input
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Random select:
              .form_input
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Mutate chance:
              .form_input
                input(type="text")

          .settings-layer_foot
            button.btn.btn--primary(type="button") Apply

      .popup_body(
          :class="{'active': tabSelected == 1}"
        )
        settings-code(
        :trainingMode="true"
        )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetTrainGenetic',
  mixins: [mixinSet],
  components: {
    SettingsCode,
  },
  data() {
    return {
      settings: {
        pooling: false,
        neurons: 'None',
        opt: 'None',
        items: ['Data_1', 'Data_2', 'Data_3', 'Data_4', 'Data_5',]
      }
    }
  },
  methods: {

  }
}
</script>
