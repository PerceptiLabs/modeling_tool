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
      .popup_body(:class="{'active': tabSelected == 0}")
        .settings-layer
          .settings-layer_section
            .form_row
              .form_label Reshape:
              .form_input
                triple-input(v-model="settings.Shape")
          //.settings-layer_section
            .form_row
              .form_label Reshape:
              .form_input
                input(type="text")
          //.settings-layer_section
            .form_row
              .form_label Transpose:
              .form_input
                input(type="text")
          .settings-layer_section
            .form_row
              .form_label Transpose:
              .form_input
                triple-input(v-model="settings.Permutation")
          .settings-layer_foot
            button.btn.btn--primary(type="button" @click="applySettings") Apply

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
  import TripleInput    from "@/components/base/triple-input";

  export default {
    name: 'SetProcessReshape',
    mixins: [mixinSet],
    components: {
      TripleInput,
      SettingsCode
    },
    data() {
      return {
        settings: {
          Shape: [28,28,1],
          Permutation: [0,1,2],
        }
      }
    },
    computed: {
      coreCode() {
        return `Y=tf.reshape(X, [-1]+[layer_output for layer_output in "+str(${this.settings.Shape})+"]);
                Y=tf.transpose(Y,perm="+str([0]+[i+1 for i in ${this.settings.Permutation}])+")`
      }
    }
  }
</script>
