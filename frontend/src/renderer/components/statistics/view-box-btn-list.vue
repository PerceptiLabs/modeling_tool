<template lang="pug">
  ul.statistics-box_tabset
    h5 View Box
    li.statistics-box_tab(
      v-for="(tabInfo, name, i) in tabSet"
      :key="name"
    )
      button.btn.tutorial-relative(type="button"
        v-if="tabInfo"
        @click="setCurrentTab(name, tabInfo)"
        v-tooltip-interactive:bottom="tabInfo.btnInteractiveInfo"
        :class="[currentTab === name ?  'btn--primary' : 'btn--secondary', tabInfo.btnClass]"
        :id="tabInfo.btnId"
      ) {{ name }}

      button.btn.btn--small(type="button"
        v-else
        @click="setCurrentTab(name)"
        :class="currentTab === name ? 'btn--primary' : 'btn--secondary'"
      ) {{ name }}
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import { deepCloneNetwork } from '@/core/helpers.js'

export default {
  name: "ViewBoxBtnList",
  props: {
    layerType: { type: String }
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
    setCurrentTab(tab, el) {
      if(el && el.type === 'component') {
        let element = this.$store.getters['mod_workspace/GET_networkSnapshotElementById'](el.layerId);
        
        this.$store.commit('mod_statistics/CHANGE_StatisticSelectedArr', deepCloneNetwork(element));
        this.$store.commit('mod_statistics/setSelectedMetric', { placeToBeChanged: 'statisticsTabs', selectedMetric: tab });
      } else {
        this.$store.commit('mod_statistics/setSelectedMetric', { placeToBeChanged: this.tabsKeyToBeChanged, selectedMetric: tab });
      }

      this.$store.dispatch('mod_tracker/EVENT_viewboxMetricSelect', {
        view: this.testIsOpen ? 'Test' : 'Statistics', // can only be in Test or Statistics view
        layerType: this.layerType,
        selectedMetric: tab
      });
      
      // Need to check if this.layerType === 'Training' because it's the same
      // component for the Training and normal (next to network map) viewboxes.
      if (this.layerType === 'Training' && this.getCurrentStepCode === 'tutorial-statistics-tabs') {
        this.setNextStep({currentStep:'tutorial-statistics-tabs'});
      }
    }
  },
  computed: {
    ...mapGetters({
      getCurrentStepCode: 'mod_tutorials/getCurrentStepCode',
    }),
    tabsKeyToBeChanged() {
      return this.layerType === 'ViewBox' ? 'viewBoxTabs' : 'statisticsTabs';
    },
    currentTab() {
      return this.$store.getters['mod_statistics/getSelectedMetric'](this.tabsKeyToBeChanged);
    },
    tabSet() {
      return this.$store.getters['mod_statistics/getLayerMetrics'](this.tabsKeyToBeChanged);
    },
    testIsOpen() {
      return this.$store.getters['mod_workspace/GET_testIsOpen'];
    }
  }
}
</script>

<style lang="scss" scoped>
  

  .statistics-box_tabset {
    // position: absolute;
    // z-index:10;
    // right: 11px;
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
      // background-color: #090f19;
      // border-top: 1px solid rgba(97, 133, 238, 0.4);
      // border-bottom: 1px solid rgba(97, 133, 238, 0.4);
      min-height: 3.0rem;
      margin-bottom: 1rem;

      h5 {
        display: block;
        font-size: 11px;
        padding-left: 1rem;
        margin-right: auto;
        margin-bottom: 0px;
        font-family: Nunito Sans;
        font-style: normal;
        font-weight: 600;
        line-height: 2.8rem;
      }
    }
  }
  .statistics-box_tab {
    display: flex;
    + .statistics-box_tab {
      padding-left: 1rem;
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
