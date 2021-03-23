<template lang="pug">
  div.questionnaire-block-wrapper
    h3 {{ q }}
    .content-groups
      .content-group
        base-radio(group-name="group" :value-input="'Visually build and compare multiple models'" v-model="a.WhatAreYouLookingFor")
          span Visually build and compare multiple models
        base-radio(group-name="group" :value-input="'Rapid prototyping'" v-model="a.WhatAreYouLookingFor")
          span Rapid prototyping
        base-radio(group-name="group" :value-input="'Interpret and visualize models'" v-model="a.WhatAreYouLookingFor")
          span Interpret and visualize models
        base-radio(group-name="group" :value-input="'Other'" v-model="a.WhatAreYouLookingFor")
          span Other
      .content-group
        textarea(
          v-model="a.optionalDetails"
          placeholder="(optional) Add some details"
          maxlength="255")
</template>

<script>

export default {
  name: 'WhatAreYouLookingFor',
  props: ['value'],
  data() {
    return {
      q: 'What are you looking for in PerceptiLabs?',
      a: {
        WhatAreYouLookingFor: '',
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

