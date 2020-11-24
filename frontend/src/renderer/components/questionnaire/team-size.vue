
<template lang="pug">
  div.questionnaire-block-wrapper
    h3 {{ q }}

    .content-groups
      .content-group
        base-radio(group-name="group" :value-input="'1-5'" v-model="a.teamSize")
          span 1-5
        base-radio(group-name="group" :value-input="'5-10'" v-model="a.teamSize")
          span 5-10
        base-radio(group-name="group" :value-input="'10-30'" v-model="a.teamSize")
          span 10-30
        base-radio(group-name="group" :value-input="'30+'" v-model="a.teamSize")
          span 30+

      .content-group
        textarea(
          v-model="a.optionalDetails"
          placeholder="(optional) Add some details"
          maxlength="255")
</template>

<script>

export default {
  name: 'Questionnaire-TeamSize',
  props: ['value'],
  data() {
    return {
      q: 'How many people are training models in your team?',
      a: {
        teamSize: '',
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

