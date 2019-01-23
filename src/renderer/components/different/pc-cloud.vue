<template lang="pug">
  .pc-cloud
    .pc-cloud_tab-set
      button.btn.pc-cloud_tab(type="button"
        v-for="(tab, i) in tabs"
        :key="i"
        @click="setTab(i)"
        :class="{'active': tabSelected === i}"
        )
        i.icon(:class="tab")
    template(v-if="tabSelected === 0")
      slot(name="pc")
    template(v-if="tabSelected === 1")
      slot(name="cloud")

</template>

<script>
export default {
  name: "PcCloud",
  data() {
    return {
      tabSelected: 0,
      tabs: ['icon-Computer', 'icon-cloud-add']
    }
  },
  methods: {
    setTab(i) {
      this.tabSelected = i
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .pc-cloud {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
  .pc-cloud_tab-set {
    display: flex;
    align-items: center;
    justify-content: center;
    padding-bottom: 1rem;
  }
  .pc-cloud_tab {
    font-size: 2rem;
    line-height: 1;
    color: $bg-input;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 10rem;
    height: 4.6rem;
    transition: none;
    border: 2px solid;
    &:hover,
    &.active {
      box-shadow: $icon-shad;
    }
    &.active {
      color: $col-txt;
      border: none;
      background: $bg-grad-blue;
    }
    + .pc-cloud_tab {
      margin-left: 1rem;
    }
  }
</style>
