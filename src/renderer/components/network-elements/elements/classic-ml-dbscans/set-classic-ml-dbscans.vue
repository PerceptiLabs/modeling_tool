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
              .form_label Max sample distance to be in same neighborhood:
              .form_input
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Min samples in neighborhood:
              .form_input
                input(type="text")
          template(v-if="userMode === 'advanced'")
            .settings-layer_section
              .form_row
                .form_label Initialization method:
                .form_input
                  base-radio(groupName="group" valueInput="None" v-model="settings.neurons")
                    span Auto
                  base-radio(groupName="group" valueInput="Sigmoid" v-model="settings.neurons")
                    span Ball tree
                  base-radio(groupName="group" valueInput="None1" v-model="settings.neurons")
                    span KD tree
                  base-radio(groupName="group" valueInput="Sigmoid2" v-model="settings.neurons")
                    span Brute force
            .settings-layer_section
              .form_row
                .form_label Leaf size:
                .form_input
                  input(type="text")

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
        :the-code="coreCode"
        )
    .settings-layer_foot
      button.btn.btn--primary(type="button" @click="applySettings") Apply

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetClassicMLDbscans',
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
