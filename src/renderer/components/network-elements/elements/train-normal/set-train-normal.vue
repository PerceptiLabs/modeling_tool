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
          //.settings-layer_section
            .form_row
              .form_label Labels:
              .form_input
                base-select(:selectOptions="settings.items")
          .settings-layer_section
            .form_row
              .form_label Cost function:
              .form_input
                base-radio(groupName="group" valueInput="Cross_entropy" v-model="settings.Loss")
                  span Cross-Entropy
                base-radio(groupName="group" valueInput="Quadratic" v-model="settings.Loss")
                  span Quadratic
                base-radio(groupName="group" valueInput="W_cross_entropy" v-model="settings.Loss")
                  span Weighted Cross-Entropy
                base-radio(groupName="group" valueInput="Dice" v-model="settings.Loss")
                  span DICE
          .settings-layer_section
            .form_row
              .form_label Optimizer:
              .form_input
                base-radio(groupName="group1" valueInput="ADAM" v-model="settings.Optimizer")
                  span ADAM
                base-radio(groupName="group1" valueInput="SGD" v-model="settings.Optimizer")
                  span SGD
                base-radio(groupName="group1" valueInput="Momentum" v-model="settings.Optimizer")
                  span Momentum
                base-radio(groupName="group1" valueInput="RMSprop" v-model="settings.Optimizer")
                  span RMSprop
          .settings-layer_section
            .form_row
              .form_label Learning rate:
              .form_input
                input(type="text" v-model="settings.Learning_rate")
          //.settings-layer_section
            .form_row
              .form_label Regularization:
              .form_input
                input(type="text")
          //.settings-layer_section
            .form_row
              .form_label N_class:
              .form_input
                input(type="text" v-model="settings.N_class")
          //.settings-layer_section
            .form_row
              .form_label Pooling:
              .form_input
                base-checkbox(valueInput="Pooling" v-model="settings.pooling")
          //.settings-layer_section
            .form_row
              .form_label Learning rate:
              .form_input
                input(type="number")


          .settings-layer_foot
            button.btn.btn--primary(type="button"
            @click="applySettings"
            ) Apply


      .popup_body(
          :class="{'active': tabSelected == 1}"
        )
        settings-code(
          :the-code="coreCode"
        )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetTrainNormal',
  mixins: [mixinSet],
  components: { SettingsCode },
  data() {
    return {
      settings: {
        N_class: '1',
        Loss: "Cross_entropy", //#Cross_entropy, Quadratic, W_cross_entropy, Dice
        Learning_rate: "0.01",
        Optimizer: "SGD", //#SGD, Momentum, ADAM, RMSprop
        Training_iters: "20000"
      },
    }
  },
  computed: {
    coreCode() {
      return `Y=tf.reshape(X, [-1]+[${this.settings.Loss} for ${this.settings.Learning_rate} in "+str(${this.settings.Optimizer})+"]);
              Y=tf.transpose(Y,perm="+str([0]+[i+1 for i in properties["Permutation"]])+")`
    }
  }
}
</script>
