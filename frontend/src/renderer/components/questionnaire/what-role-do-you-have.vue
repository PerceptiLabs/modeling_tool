<template lang="pug">
  div.questionnaire-block-wrapper
    h3 {{ q }}
    .content-groups
      .content-group
        base-radio(group-name="group" :value-input="'Data scientist'" v-model="a.WhatRoleDoYouHave")
          span Data scientist
        base-radio(group-name="group" :value-input="'Developer'" v-model="a.WhatRoleDoYouHave")
          span Developer
        base-radio(group-name="group" :value-input="'Researcher'" v-model="a.WhatRoleDoYouHave")
          span Researcher
        base-radio(group-name="group" :value-input="'Project Manager'" v-model="a.WhatRoleDoYouHave")
          span Project Manager
        base-radio(group-name="group" :value-input="'Other'" v-model="a.WhatRoleDoYouHave")
          span Other
      .content-group
        textarea(
          v-model="a.optionalDetails"
          placeholder="(optional) Add some details"
          maxlength="255")
</template>

<script>

export default {
  name: 'WhatRoleDoYouHave',
  props: ['value'],
  data() {
    return {
      q: 'What role do you have?',
      a: {
        WhatRoleDoYouHave: '',
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

