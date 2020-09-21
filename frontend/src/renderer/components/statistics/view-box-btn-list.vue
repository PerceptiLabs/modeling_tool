<template lang="pug">
  ul.statistics-box_tabset
    h5 View Box
    li.statistics-box_tab(
      v-for="(tabInfo, name, i) in tabSet"
      :key="name"
    )
      button.btn.btn--tabs.statistics-box_btn.tutorial-relative(type="button"
        v-if="tabInfo"
        @click="setCurrentTab(name, tabInfo.btnId)"
        v-tooltip-interactive:bottom="tabInfo.btnInteractiveInfo"
        :class="[currentTab === name ?  'active' : '', tabInfo.btnClass]"
        :id="tabInfo.btnId"
      ) {{ name }}

      button.btn.btn--tabs.statistics-box_btn(type="button"
        v-else
        @click="setCurrentTab(name)"
        :class="{'active': currentTab === name}"
      ) {{ name }}
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: "ViewBoxBtnList",
  props: {
    layerType: { type: String }
  }, 
  activated() {
    console.log('activate');
  },
  mounted() {
    // if(this.tabSet) {
    //   const tabSetKeys = Object.keys(this.tabSet);
    //   this.setCurrentTab(tabSetKeys[0]);
    // }
  },
  data() {
    return {
      // currentTab: '',
    }
  },
  methods: {
    ...mapActions({
      setNextStep:      'mod_tutorials/setNextStep',
    }),
    setCurrentTab(tab, id) {
      // this.currentTab = tab;
      // this.$emit('set-current-btn', tab);
      this.$store.commit('mod_statistics/setSelectedMetric', { layerType: this.layerType, selectedMetric: tab });

      this.$store.dispatch('mod_tracker/EVENT_viewboxMetricSelect', {
        view: this.testIsOpen ? 'Test' : 'Statistics', // can only be in Test or Statistics view
        layerType: this.layerType,
        selectedMetric: tab
      });
      
      // Need to check if this.layerType === 'Training' because it's the same
      // component for the Training and normal (next to network map) viewboxes.
      if (this.layerType === 'Training' && this.getCurrentStepCode === 'tutorial-statistics-tabs') {
        this.setNextStep('tutorial-statistics-tabs');
      }
    }
  },
  computed: {
    ...mapGetters({
      getCurrentStepCode: 'mod_tutorials/getCurrentStepCode',
    }),
    currentTab() {
      return this.$store.getters['mod_statistics/getSelectedMetric'](this.layerType);
    },
    tabSet() {
      return this.$store.getters['mod_statistics/getLayerMetrics'](this.layerType);
    },
    testIsOpen() {
      return this.$store.getters['mod_workspace/GET_testIsOpen'];
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";

  .statistics-box_tabset {
    position: absolute;
    z-index:10;
    right: 11px;
    display: flex;
    flex-wrap: nowrap;
    flex: 0 0 auto;
    justify-content: flex-end;
    background-color: transparent;

    h5 {
      display: none;
    }
  }

  .workspace-relative .statistics-box_tabset {
    display: none;
  }

  #tutorial_view-box {
    .statistics-box_tabset {
      position: static;
      background-color: #090f19;
      border-top: 2px solid rgba(97, 133, 238, 0.4);
      border-bottom: 1px solid rgba(97, 133, 238, 0.4);
      min-height: 2.5rem;

      h5 {
        display: block;
        font-size: 11px;
        padding-left: 1rem;
        margin-right: auto;
        margin-top: 5px;
        margin-bottom: 0px;
        font-family: Nunito Sans;
        font-style: normal;
        font-weight: 600;
      }
    }
  }
  .statistics-box_tab {
    display: flex;
    + .statistics-box_tab {
      padding-left: .1rem;
    }
  }
  .statistics-box_btn {
    flex: 1;
    color: inherit;
    min-width: 11.6rem;
    background: transparent;
    font-family: Nunito Sans;
    font-weight: 600;
    font-size: 12px;
    background: #090f19;
    border: 2px solid rgba(97, 133, 238, 0.4);
    border-bottom-width: 0px;
    border-radius: 7px 7px 0px 0px;
    padding-top: 3px;
    padding-bottom: 3px;

    &:hover,
    &.active {
      color: $white;
      background: $bg-grad-blue;
      background: #6185EE;
      box-shadow: $icon-shad;
      border-color: #6185EE;
    }
  }
</style>
