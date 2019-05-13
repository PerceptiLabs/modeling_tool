<template lang="pug">
  .settings-layer
    .settings-layer_section
      .form_holder
        code-hq( v-model="theCode")

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
