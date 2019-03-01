<template lang="pug">
  .settings-layer
    .settings-layer_section
      .form_holder
        label.form_label Cost function:
        code-hq( v-model="theCode")
        //textarea(v-model="theCode" readonly="true")
      //-.form_holder(v-if="trainingMode")
        label.form_label Optimizer:
        textarea
      //-.form_holder(v-if="trainingMode")
        label.form_label Learning Rate:
        textarea
    .settings-layer_foot
      button.btn.btn--primary(type="button" disabled="true") Apply


</template>

<script>
  import codeHq    from "@/components/network-elements/elements-settings/code-hq.vue";

export default {
  name: "SettingsCode",
  components: {codeHq},
  props: {
    trainingMode: {
      type: Boolean,
      default: false
    },
    theCode: {
      type: String,
      default: ''
    },
  }
}
</script>

<style lang="scss" scoped>

</style>
