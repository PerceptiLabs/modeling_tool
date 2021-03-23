<template lang="pug">
  div.questionnaire-block-wrapper
    h3 {{ q }}

    .content-groups
      .content-group
        base-radio(group-name="group" :value-input="'New to the field, using PerceptiLabs to learn'" v-model="a.DeepLearningExperience")
          span New to the field, using PerceptiLabs to learn
        base-radio(group-name="group" :value-input="'Intermediate'" v-model="a.DeepLearningExperience")
          span Intermediate
        base-radio(group-name="group" :value-input="'Experienced'" v-model="a.DeepLearningExperience")
          span Experienced
        base-radio(group-name="group" :value-input="'Other'" v-model="a.DeepLearningExperience")
          span Other


      .content-group
        textarea(
          v-model="a.optionalDetails"
          placeholder="(optional) Add some details"
          maxlength="255")
</template>

<script>

export default {
  name: 'DeepLearningExperience',
  props: ['value'],
  data() {
    return {
      q: 'What\'s your Deep Learning experience?',
      a: {
        DeepLearningExperience: '',
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
