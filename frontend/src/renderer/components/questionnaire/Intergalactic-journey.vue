<template lang="pug">
  div.questionnaire-block-wrapper
    h3 {{ q }}
    .content-groups
      .content-group
        base-radio(group-name="group" :value-input="'Mars'" v-model="a.IntergalacticJourney")
          span Mars
        base-radio(group-name="group" :value-input="'The Moon'" v-model="a.IntergalacticJourney")
          span The Moon
        base-radio(group-name="group" :value-input="'The United Colonies of Kobol'" v-model="a.IntergalacticJourney")
          span The United Colonies of Kobol
        base-radio(group-name="group" :value-input="`I'm staying home`" v-model="a.IntergalacticJourney")
          span I'm staying home
        base-radio(group-name="group" :value-input="'Other'" v-model="a.IntergalacticJourney")
          span Other

      .content-group
        textarea(
          v-model="a.optionalDetails"
          placeholder="(optional) Add some details"
          maxlength="255")
</template>

<script>

export default {
  name: 'IntergalacticJourney',
  props: ['value'],
  data() {
    return {
      q: 'On your next intergalactic journey will you go to?',
      a: {
        IntergalacticJourney: '',
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
