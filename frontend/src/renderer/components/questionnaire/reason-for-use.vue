
<template lang="pug">
  div.questionnaire-block-wrapper
    h3 {{ q }}

    .content-groups
      .content-group

        base-radio(group-name="group" :value-input="'part-of-ml-team'" v-model="a.reasonForUse")
          span I'm part of a team doing ML
        base-radio(group-name="group" :value-input="'develop-ml-tools'" v-model="a.reasonForUse")
          span I develop ML models
        base-radio(group-name="group" :value-input="'curious-about-ml'" v-model="a.reasonForUse")
          span I'm curious about ML
        base-radio(group-name="group" :value-input="'other'" v-model="a.reasonForUse")
          span Other:

      .content-group
        textarea(
          v-model="a.optionalDetails"
          placeholder="(optional) Add some details"
          maxlength="255")
</template>

<script>

export default {
  name: 'Questionnaire-ReasonForUse',
  props: ['value'],
  data() {
    return {
      q: 'What brings you to PerceptiLabs?',
      a: {
        reasonForUse: '',
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

