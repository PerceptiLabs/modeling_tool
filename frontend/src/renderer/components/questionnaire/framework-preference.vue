
<template lang="pug">
  div.questionnaire-block-wrapper
    h3 {{ q }}

    .content-groups
      .content-group
        base-radio(group-name="group" :value-input="'tensorflow'" v-model="a.frameworkPreference")
          span Tensorflow
        base-radio(group-name="group" :value-input="'pytorch'" v-model="a.frameworkPreference")
          span PyTorch
        base-radio(group-name="group" :value-input="'keras'" v-model="a.frameworkPreference")
          span Keras
        base-radio(group-name="group" :value-input="'scikit-learn'" v-model="a.frameworkPreference")
          span Sci-kit learn
        base-radio(group-name="group" :value-input="'other'" v-model="a.frameworkPreference")
          span Other:

      .content-group
        textarea(
          v-model="a.optionalDetails"
          placeholder="(optional) Add some details"
          maxlength="255")
</template>

<script>

export default {
  name: 'Questionnaire-FrameworkPreference',
  props: ['value'],
  data() {
    return {
      q: 'Which ML framework do you prefer?',
      a: {
        frameworkPreference: '',
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

