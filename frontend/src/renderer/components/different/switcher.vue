<template lang="pug">
  .switcher
    ul.switcher_tab-set
      button.btn.switcher_tab(type="button"
        v-for="(tab, i) in tabSetData"
        :key="i"
        @click="setTab(i)"
        :class="{'text-disable': tabSelected !== i}"
        :disabled="i === 1"
        ) {{ tab }}
    template(v-if="tabSelected === 0")
      slot(name="firstTab")
    template(v-if="tabSelected === 1")
      slot(name="secondTab")

</template>

<script>
export default {
  name: "BaseSwitcher",
  props: {
    tabSetData: {
      type: Array,
      default: function () {
        return ['Computer', 'Cloud']
      }
    }
  },
  data() {
    return {
      tabSelected: 0,
    }
  },
  methods: {
    setTab(i) {
      this.tabSelected = i;
      this.$emit('tab-index', i)
    }
  }
}
</script>

<style lang="scss" scoped>
  .switcher_tab-set {
    font-size: 1.4rem;
    display: flex;
    border-radius: 10rem;
    border: 1px solid $col-primary2;
    margin-bottom: 2rem;
  }
  .switcher_tab {
    flex: 0 0 50%;
    text-align: center;
    padding: .9rem .5rem;
    border-radius: 10rem 0 0 10rem;
    + .switcher_tab {
      border-radius: 0 10rem 10rem 0;
    }
    &:not(.text-disable) {
      background: $bg-grad-blue;
      box-shadow: $icon-shad;
    }
  }
</style>
