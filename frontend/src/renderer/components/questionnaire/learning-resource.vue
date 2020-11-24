
<template lang="pug">
  div.questionnaire-block-wrapper
    h3 {{ q }}

    .content-groups
      .content-group
        base-checkbox.checkbox-group(v-model="a.university")
          span University
        base-checkbox.checkbox-group(v-model="a.onlineCourses")
          span Online Courses
        base-checkbox.checkbox-group(v-model="a.selfDirectedStudy")
          span Self-directed Study
        base-checkbox.checkbox-group(v-model="a.otherReason")
          span Other:

      .content-group
        textarea(
          v-model="a.optionalDetails"
          placeholder="(optional) Add some details"
          maxlength="255")
</template>

<script>

export default {
  name: 'Questionnaire-LearningResouce',
  props: ['value'],
  data() {
    return {
      q: 'Where are you learning about ML?',
      a: {
        university: false,
        onlineCourses: false,
        selfDirectedStudy: false,
        otherReason: false,
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

