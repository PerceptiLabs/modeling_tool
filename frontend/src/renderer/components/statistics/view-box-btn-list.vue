<template lang="pug">
  ul.statistics-box_tabset
    li.statistics-box_tab(
      v-for="(tabINfo, name, i) in tabSet"
      :key="name"
    )
      button.btn.btn--tabs.statistics-box_btn.tutorial-relative(type="button"
        v-if="tabINfo"
        @click="setCurrentTab(name, tabINfo.btnId)"
        v-tooltip-interactive:bottom="tabINfo.btnInteractiveInfo"
        :class="[currentTab === name ?  'active' : '', tabINfo.btnClass]"
        :id="tabINfo.btnId"
      ) {{ name }}

      button.btn.btn--tabs.statistics-box_btn(type="button"
        v-else
        @click="setCurrentTab(name)"
        :class="{'active': currentTab === name}"
      ) {{ name }}
</template>

<script>
  import { mapActions } from 'vuex';
export default {
  name: "ViewBoxBtnList",
  props: {
    tabSet: { type: Object }
  },
  activated() {
    console.log('activate');
  },
  mounted() {
    if(this.tabSet) {
      const tabSetKeys = Object.keys(this.tabSet);
      this.setCurrentTab(tabSetKeys[0]);
    }
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
    setCurrentTab(tab, id) {
      this.currentTab = tab;
      this.$emit('set-current-btn', tab);
      if(id) this.tutorialPointActivate({way: 'next', validation: id})
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
