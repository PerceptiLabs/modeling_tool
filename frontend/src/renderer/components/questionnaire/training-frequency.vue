
<template lang="pug">
  div.questionnaire-block-wrapper
    h3 {{ q }}

    .content-groups
      .content-group
        base-radio(group-name="group" :value-input="'never'" v-model="a.trainingFrequency")
          span Never
        base-radio(group-name="group" :value-input="'yearly'" v-model="a.trainingFrequency")
          span A few times a year
        base-radio(group-name="group" :value-input="'monthly'" v-model="a.trainingFrequency")
          span Every month
        base-radio(group-name="group" :value-input="'weekly'" v-model="a.trainingFrequency")
          span Every week
        base-radio(group-name="group" :value-input="'daily'" v-model="a.trainingFrequency")
          span Every day

      .content-group
        textarea(
          v-model="a.optionalDetails"
          placeholder="(optional) Add some details"
          maxlength="255")
</template>

<script>

export default {
  name: 'Questionnaire-TrainingFrequency',
  props: ['value'],
  data() {
    return {
      q: 'How often do you train models?',
      a: {
        trainingFrequency: '',
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
      immediate: true, // true so it populates the default value in parent questionAnswers
      handler(newVal, oldVal) {
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

<style lang="scss" scoped>
</style>

