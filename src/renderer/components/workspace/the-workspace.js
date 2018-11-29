import TextEditable     from '@/components/base/text-editable.vue'
import NetworkField     from '@/components/network-field/network-field.vue'
import GeneralSettings  from "@/components/global-popups/workspace-general-settings.vue";
import GeneralResult    from "@/components/global-popups/workspace-result";
import SelectCoreSide   from "@/components/global-popups/workspace-core-side";
import TheStatistics    from "@/components/statistics/the-statistics.vue";
import TheViewBox       from "@/components/statistics/the-view-box";

export default {
  name: 'WorkspaceContent',
  components: {
    NetworkField,
    TextEditable,
    GeneralSettings,
    GeneralResult,
    SelectCoreSide,
    TheStatistics,
    TheViewBox,
  },
  data () {
    return {
      scale: 100,
    }
  },
  mounted() {

  },
  computed: {
    styleScale() {
      return this.scale / 100
    },
    workspace() {
      return this.$store.state.mod_workspace.workspaceContent
    },
    indexCurrentNetwork() {
      return this.$store.state.mod_workspace.currentNetwork
    },
    hideSidebar() {
      return this.$store.state.globalView.hideSidebar
    },
    showGlobalSet() {
      return this.$store.state.globalView.globalPopup.showNetSettings
    },
    showGlobalResult() {
      return this.$store.state.globalView.globalPopup.showNetResult
    },
    hasStatistics() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkStatistics;
    },
    showCoreSide() {
      return this.$store.state.globalView.globalPopup.showCoreSideSettings
    },
    appMode() {
      return this.$store.state.globalView.appMode
    },
    // currentSelectedIndex() {
    //   return this.$store.getters['mod_workspace/GET_currentSelectedIndex']
    // },
    statisticsIsOpen() {
      return this.$store.state.globalView.statisticsIsOpen
    },
    statisticsElSelected() {
      return this.$store.state.mod_statistics.selectedElArr
    }

  },
  watch: {

  },
  methods: {
    deleteTabNetwork(index) {
      this.$store.commit('mod_workspace/DELETE_workspaceTab', index)
    },
    setTabNetwork(index) {
      this.$store.commit('mod_workspace/SET_currentNetwork', index);
      this.$store.commit('globalView/SET_statisticsIsOpen', false)
    },
    toggleSidebar () {
      this.$store.commit('globalView/SET_hideSidebar', !this.hideSidebar)
    },
    decScale () {
      if (this.scale < 10) {
        this.scale = 5
      }
      else this.scale = this.scale - 10
    },
    incScale () {
      if (this.scale > 90) {
        this.scale = 100
      }
      else this.scale = this.scale + 10
    },
    resize(newRect, i) {
      //console.log(newRect);
      //console.log(i);
      // this.network[i].meta.top = newRect.top;
      // this.network[i].meta.left = newRect.left;
    },
    onActivated(e) {
      //console.log(e)
    },
    editNetName(newName) {
      this.$store.commit('mod_workspace/SET_networkName', newName);
    },
    openStatistics() {
      this.$store.commit('globalView/SET_statisticsIsOpen', true)
    }
  }
}
