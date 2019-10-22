<template lang="pug">
  ul.statistics-box_tabset
    li.statistics-box_tab(
      v-for="(tabINfo, name, i) in tabSet"
      :key="name"
    )
      button.btn.btn--tabs.statistics-box_btn.tutorial-relative(type="button"
        v-if="tabINfo"
        @click="setCurrentTab(name)"
        v-tooltip-interactive:bottom="tabINfo.interactiveInfo"
        :class="{'active': currentTab === name}"
      ) {{ name }}

      button.btn.btn--tabs.statistics-box_btn(type="button"
        v-else
        @click="setCurrentTab(name)"
        :class="[currentTab === name ?  'active' : '', tabINfo.btnClass]"
        :id="tabINfo.id"
      ) {{ name }}

  //-ul.statistics-box_tabset(v-if="!testIsOpen")
      li.statistics-box_tab(
      v-for="(tab, i) in tabset"
      /:key="i"
      )
        button.btn.btn--tabs.tutorial-relative(
        type="button"
        v-tooltip-interactive:right="tab.interactiveInfo"
        @click="setTab(tab.name, tab.id)"
        /:class="{'active': currentTab === tab.name}"
        /:id="tab.id"
        ) {{ tab.name }}
</template>

<script>
  import { mapActions } from 'vuex';
export default {
  name: "ViewBoxBtnList",
  props: {
    tabSet: { type: Object }
  },
  mounted() {
    const tabSetKeys = Object.keys(this.tabSet);
    this.setCurrentTab(tabSetKeys[0]);
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
      this.$emit('set-current-btn', tab);
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
