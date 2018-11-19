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
              .form_label Labels:
              .form_input
                base-select(:selectOptions="settings.items")
          .settings-layer_section
            .form_row
              .form_label Cost function:
              .form_input
                base-radio(groupName="group" valueInput="None" v-model="settings.neurons")
                  span Cross-Entropy
                base-radio(groupName="group" valueInput="Sigmoid" v-model="settings.neurons")
                  span Quadratic
                base-radio(groupName="group" valueInput="ReLu" v-model="settings.neurons")
                  span Weigted Cross - Entropy
                base-radio(groupName="group" valueInput="tanh" v-model="settings.neurons")
                  span DICE
          .settings-layer_section
            .form_row
              .form_label Optimizer:
              .form_input
                base-radio(groupName="group1" valueInput="None" v-model="settings.opt")
                  span AAAA
                base-radio(groupName="group1" valueInput="Sigmoid" v-model="settings.opt")
                  span SGD
                base-radio(groupName="group1" valueInput="ReLu" v-model="settings.opt")
                  span Momentum
                base-radio(groupName="group1" valueInput="tanh" v-model="settings.opt")
                  span RMSprop
          .settings-layer_section
            .form_row
              .form_label Learning rate:
              .form_input
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Regularization:
              .form_input
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Pooling:
              .form_input
                base-checkbox(valueInput="Pooling" v-model="settings.pooling")
          .settings-layer_section
            .form_row
              .form_label Learning rate:
              .form_input
                input(type="number")


          .settings-layer_foot
            button.btn.btn--primary(type="button") Apply

      .popup_body(
        :class="{'active': tabSelected == 1}"
      )
        pc-cloud
          template(slot="pc")
            .settings-layer_section
              .form_row
                input.form_input(type="text" placeholder="c:")
                button.btn.btn--primary(type="button") Load
          template(slot="cloud")
            .settings-layer_section
              .form_row
                input.form_input(type="text" placeholder="c:")
                button.btn.btn--primary(type="button") Load Cloud
        .settings-layer
          //.settings-layer_section
            .form_row
              input.form_input(type="text" placeholder="c:")
              button.btn.btn--primary(type="button") Load
          .settings-layer_section
            .form_row
              .form_label Pooling:
              .form_input
                base-checkbox(valueInput="Pooling" v-model="settings.pooling")
          .settings-layer_section
            .form_row
              .form_label Learning rate:
              .form_input
                input(type="number")
      .popup_body(
          :class="{'active': tabSelected == 2}"
        )
        settings-code(
        :trainingMode="true"
        )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
import PcCloud        from '@/components/different/pc-cloud.vue';

export default {
  name: 'SetTrainNormal',
  mixins: [mixinSet],
  components: {
    SettingsCode,
    PcCloud
  },
  data() {
    return {
      tabs: ['Settings', 'Labels', 'Code'],
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
