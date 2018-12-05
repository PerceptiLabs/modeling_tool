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
              .form_label Clusters:
              .form_input
                input(type="text")
          template(v-if="userMode === 'advanced'")
            .settings-layer_section
              .form_row
                .form_label Max iterations:
                .form_input
                  input(type="text")
            .settings-layer_section
              .form_row
                .form_label Method:
                .form_input
                  base-radio(groupName="group" valueInput="None" v-model="settings.neurons")
                    span Kmeans++
                  base-radio(groupName="group" valueInput="Sigmoid" v-model="settings.neurons")
                    span Random
            .settings-layer_section
              .form_row
                .form_label Initialization iteractions:
                .form_input
                  input(type="text")
            .settings-layer_section
              .form_row
                .form_label Convergence tolerance:
                .form_input
                  input(type="text")

          .settings-layer_foot
            button.btn.btn--primary(type="button") Apply

      .popup_body(
          :class="{'active': tabSelected == 1}"
        )
        settings-code

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetClassicMLKMeans',
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
