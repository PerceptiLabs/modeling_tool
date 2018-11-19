<template lang="pug">
  .settings-layer
    .settings-layer_section
      .form_holder
        label.form_label Cost function:
        textarea
      .form_holder(v-if="trainingMode")
        label.form_label Optimizer:
        textarea
      .form_holder(v-if="trainingMode")
        label.form_label Learning Rate:
        textarea
    .settings-layer_foot
      button.btn.btn--primary(type="button") Apply


</template>

<script>
export default {
  name: "SettingsCode",
  props: {
    trainingMode: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {

    }
  },
  methods: {

  }
}
</script>

<style lang="scss" scoped>

</style>
