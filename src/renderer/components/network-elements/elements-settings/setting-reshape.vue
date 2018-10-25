<template lang="pug">
  .settings-layer
    .settings-layer_section
      .form_row
        .form_label.w-33 Data Into the Layer:
        .form_input.w-66
          input
    .settings-layer_section
      .form_row
        .form_label.w-33 Reshape data:
        .form_input.w-66
          input
    .settings-layer_section
      .form_row
        .form_label.w-33 Transpose maps:
        .form_input.w-66
          input
    .settings-layer_section
      .form_row
        .form_label.w-33 Data out from the Layer:
        .form_input.w-66
          input
    .settings-layer_foot
      button.btn.btn--primary(type="button") Apply


</template>

<script>
export default {
  name: "SettingsReshape",
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
