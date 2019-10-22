<template lang="pug">
  section.network_info-section
    .info-section_head(v-if="!testIsOpen")
      h3 Statistics
      //-view-box-btn-list(
        v-if="!testIsOpen && tabset.length"
        /:tab-set="tabset"
        @set-current-tab="setCurrentTab"
        )

    .info-section_main(v-if="elData !== null")
      component(
        :is="elData.componentName"
        :element-data="elData.viewBox"
        :current-tab="currentTab"
        @btn-list="setBtnList"
      )
</template>

<script>


  import ViewBoxBtnList   from '@/components/statistics/view-box-btn-list.vue'

  import { mapGetters, mapMutations, mapActions } from 'vuex';

export default {
  name: "TheStatistics",
  components: {

    ViewBoxBtnList
  },
  props: {
    elData: {
      type: Object,
      default: function () {
        return {}
      }
    }
  },
  mounted() {
    this.pointActivate({way: null, validation: this.activePoint.actions[0].id})
  },
  data() {
    return {
      currentTab: '',
      tabset: [],
    }
  },
  computed: {
    ...mapGetters({
      activePoint:   'mod_tutorials/getActivePoint',
      testIsOpen:   'mod_workspace/GET_testIsOpen'
    }),
  },
  watch: {
    'elData.componentName': {
      handler() {
        this.currentTab = '';
        this.tabset = [];
      }
    }
  },
  methods: {
    ...mapActions({
      pointActivate:    'mod_tutorials/pointActivate'
    }),
    setBtnList(arrList) {
      this.tabset = arrList;
    },
    setCurrentTab(tab) {
      this.currentTab = tab;
    }
  },

}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";

</style>
