<template lang="pug">
  ul.statistics-box_tabset
    li.statistics-box_tab(
      v-for="(tab, i) in tabSet"
      :key="i"
    )
      button.btn.btn--tabs(
        type="button"
        @click="setCurrentTab(tab)"
        :class="{'active': currentTab === tab}"
      ) {{ tab }}

</template>

<script>

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
    setCurrentTab(tab) {
      this.currentTab = tab;
      this.$emit('set-current-tab', tab)
    }
  }
}
</script>

<style lang="scss">
  @import "../../scss/base";
  /*.statistics-box--horizontally {*/
  /*  flex-direction: column;*/
  /*}*/
  /*.statistics-box--horizontally .statistics-box_tabset{*/
  /*  flex-wrap: nowrap;*/
  /*  max-width: 100%;*/
  /*  flex: 0 0 auto;*/
  /*  justify-content: flex-end;*/
  /*  position: absolute;*/
  /*  top: 0;*/
  /*  right: 0;*/
  /*  background: none;*/
  /*}*/
  .statistics-box_tabset {
    display: flex;
    flex-wrap: nowrap;
    flex: 0 0 auto;
    justify-content: flex-end;
    //max-width: 10.4rem;
    //background-color: $bg-window;

  }
  .statistics-box_tab {
    display: flex;
   // padding: 3px 3px 0 1px;
    + .statistics-box_tab {
      padding-left: .8rem;
    }
    .btn {
      flex: 1;
      color: inherit;
      background: linear-gradient(270deg, #5C6680 0%, #5D698D 100%);
    }
  }
</style>
