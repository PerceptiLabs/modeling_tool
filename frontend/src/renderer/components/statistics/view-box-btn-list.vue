<template lang="pug">
  ul.statistics-box_tabset
    li.statistics-box_tab(
      v-for="(tab, i) in tabSet"
      :key="i"
    )
      button.btn.btn--tabs.statistics-box_btn(
        type="button"
        @click="setCurrentTab(tab)"
        :class="{'active': currentTab === tab}"
      ) {{ tab }}

</template>

<script>
  import { mapActions } from 'vuex';
export default {
  name: "ViewBoxBtnList",
  props: {
    tabSet: { type: Array }
  },
  mounted() {
    this.setCurrentTab(this.tabSet[0]);
  },
  data() {
    return {
      currentTab: '',
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    setCurrentTab(tab) {
      this.currentTab = tab;
      this.$emit('set-current-tab', tab);
      if(false)  this.tutorialPointActivate({way: 'next', validation: id})
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .statistics-box_tabset {
    display: flex;
    flex-wrap: nowrap;
    flex: 0 0 auto;
    justify-content: flex-end;
  }
  .statistics-box_tab {
    display: flex;
    + .statistics-box_tab {
      padding-left: .8rem;
    }
  }
  .statistics-box_btn {
    flex: 1;
    color: inherit;
    min-width: 11.6rem;
    background: linear-gradient(270deg, #5C6680 0%, #5D698D 100%);
  }
</style>
