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
              .form_label Method:
              .form_input
                base-radio(groupName="group" valueInput="Q_learning" v-model="settings.ReinforceType")
                  span Q-learning
                base-radio(groupName="group" valueInput="Policy_learning" v-model="settings.ReinforceType")
                  span Policy-learning
                base-radio(groupName="group" valueInput="A3C" v-model="settings.ReinforceType")
                  span A3C
                base-radio(groupName="group" valueInput="A2C" v-model="settings.ReinforceType")
                  span A2C
                base-radio(groupName="group" valueInput="PPO" v-model="settings.ReinforceType")
                  span PPO
          .settings-layer_section
            .form_row
              .form_label Optimizer:
              .form_input
                base-radio(groupName="group1" valueInput="SGD" v-model="settings.Optimizer")
                  span SGD
                base-radio(groupName="group1" valueInput="Adam" v-model="settings.Optimizer")
                  span Adam
                base-radio(groupName="group1" valueInput="Momentum" v-model="settings.Optimizer")
                  span Momentum
                base-radio(groupName="group1" valueInput="RMSprop" v-model="settings.Optimizer")
                  span RMSprop
          .settings-layer_section
            .form_row
              .form_label Learning rate:
              .form_input
                input(type="text" v-model="settings.Learning_rate")
          //-.settings-layer_section
            .form_row
              .form_label Regularization:
              .form_input
                input(type="text" disabled="disabled")
          //-.settings-layer_section
            .form_row
              .form_label Gradient clipping:
              .form_input
                base-checkbox(valueInput="Pooling" v-model="settings.pooling")
          //-.settings-layer_section
            .form_row
              .form_label Clip at:
              .form_input
                input(type="number" disabled="disabled")

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
  name: 'SetLearnClassKMeans',
  mixins: [mixinSet],
  components: {
    SettingsCode,
  },
  data() {
    return {
      settings: {
        ReinforceType: 'Q_learning',
        Optimizer: 'SGD',
        Learning_rate: '0.01',
        Update_freq: '4',
        Gamma: '0.95',
        Loss: 'Quadratic',
        Eps: '1',
        Eps_min: '0.1',
        Eps_decay: '0.2',
      }
    }
  }
}
</script>
