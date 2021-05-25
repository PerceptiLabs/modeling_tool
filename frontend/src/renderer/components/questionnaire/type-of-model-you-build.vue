<template lang="pug">
  div.questionnaire-block-wrapper
    h3 {{ q }}

    .content-groups
      .content-group
        base-radio(group-name="group" :value-input="'Computer vision'" v-model="a.TypeOfModelYouBuild")
          span Computer vision
        base-radio(group-name="group" :value-input="'Natural Language Processing'" v-model="a.TypeOfModelYouBuild")
          span Natural Language Processing
        base-radio(group-name="group" :value-input="'Generative models'" v-model="a.TypeOfModelYouBuild")
          span Generative models
        base-radio(group-name="group" :value-input="'Other'" v-model="a.TypeOfModelYouBuild")
          span Other
          
      .content-group
        textarea(
          v-model="a.optionalDetails"
          placeholder="(optional) Add some details"
          maxlength="255")
</template>

<script>

export default {
  name: 'TypeOfModelYouBuild',
  props: ['value'],
  data() {
    return {
      q: 'What type of models are you looking to build?',
      a: {
        TypeOfModelYouBuild: '',
        optionalDetails: ''
      }
    }
  },
  mounted() {
    if (!this.value || !this.value.a) { return; }

    for (const k of Object.keys(this.a)) {
      this.a[k] = this.value.a[k];
    }
  },
  watch: {
    'a': {
      deep: true,
      immediate: true,
      handler(newVal) {
        if (!newVal) { return; }

        const payload = {
          q: this.q,
          a: {
            ...newVal
          }
        };

        this.$emit('input', payload);
      },
    }
  }
}
</script>