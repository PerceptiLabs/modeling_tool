import {mapActions, mapGetters, mapMutations, mapState} from 'vuex';
import saveNet    from './workspace-save-net.js'
import scaleNet   from './workspace-scale.js'
import spinnerNet from './workspace-spinner.js'
import helpersNet from './workspace-helpers.js'

import TextEditable           from '@/components/base/text-editable.vue'
import NetworkField           from '@/components/network-field/network-field.vue'
import GeneralResult          from "@/components/global-popups/workspace-result";
import SelectCoreSide         from "@/components/global-popups/workspace-core-side";
import WorkspaceBeforeImport  from "@/components/global-popups/workspace-before-import";
import WorkspaceSaveNetwork   from "@/components/global-popups/workspace-save-network.vue";
import TheTesting             from "@/components/statistics/the-testing.vue";
import TheViewBox             from "@/components/statistics/the-view-box";
import StartTrainingSpinner   from '@/components/different/start-training-spinner.vue'
import TheMiniMap             from '@/components/different/the-mini-map.vue'

export default {
  name: 'WorkspaceContent',
  mixins: [saveNet, scaleNet, spinnerNet, helpersNet],
  components: {
    NetworkField, TextEditable,
    GeneralResult, SelectCoreSide,
    WorkspaceBeforeImport, WorkspaceSaveNetwork,
    TheTesting, TheViewBox, StartTrainingSpinner,
    TheMiniMap
  },
  mounted() {
    console.log(this.$refs.networkField);
  },
  data() {
    return {
      trainingWasPaused: false,
    }
  },
  computed: {
    ...mapGetters({
      currentSelectedEl:  'mod_workspace/GET_currentSelectedEl',
      testIsOpen:         'mod_workspace/GET_testIsOpen',
      statusNetworkCore:  'mod_workspace/GET_networkCoreStatus',
      statisticsIsOpen:   'mod_workspace/GET_statisticsIsOpen',

      isTutorialMode:     'mod_tutorials/getIstutorialMode',
      tutorialActiveStep: 'mod_tutorials/getActiveStep',
    }),
    ...mapState({
      workspace:                  state => state.mod_workspace.workspaceContent,
      indexCurrentNetwork:        state => state.mod_workspace.currentNetwork,
      statisticsElSelected:       state => state.mod_statistics.selectedElArr,
      hideSidebar:                state => state.globalView.hideSidebar,
      showGlobalResult:           state => state.globalView.globalPopup.showNetResult,
      showWorkspaceBeforeImport:  state => state.globalView.globalPopup.showWorkspaceBeforeImport,
      showCoreSide:               state => state.globalView.globalPopup.showCoreSideSettings,
    }),

    hasStatistics() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkStatistics;
    },
    networkMode() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.netMode
    },
    coreStatus() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.coreStatus
    },
    // currentNet() {
    //   this.scale = this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom;
    //   return this.$store.getters['mod_workspace/GET_currentNetworkElementList']
    // },
    networkClass() {
      this.calcScaleMap();
      return {
        'open-statistic': this.statisticsIsOpen,
        'open-test': this.testIsOpen
      }
    },
    tabSetClass() {
      return {'bookmark_tab--active': indexCurrentNetwork === i}
    }
  },
  watch: {
    statusNetworkCore(newStatus) {
      // function for showing the global training results popup
      
      // added statisticsIsOpen null check
      // it is possible that the status is 'Finished' and both 
      // testIsOpen and statisticsIsOpen to be null

      // this happens when the core is restarted and no longer has 
      // any information about the stats, making training impossible
      if (this.statisticsIsOpen === null) {
        return;
      }

      if(newStatus === 'Finished'
        && this.testIsOpen === null
      ) {
        this.net_trainingDone();
        this.event_startDoRequest(false);
      }
    },
    currentSelectedEl(newStatus) {
      if(newStatus.length > 0
        && this.isTutorialMode
        && this.tutorialActiveStep === 'training'
      ) {
        this.tutorialPointActivate({
          way: 'next',
          validation: newStatus[0].layerMeta.tutorialId
        });
      } 
    }
  },
  methods: {
    ...mapMutations({
      set_showTrainingSpinner:  'mod_workspace/SET_showStartTrainingSpinner',
      set_currentNetwork:       'mod_workspace/SET_currentNetwork',
      set_cursorPosition:       'mod_workspace/SET_CopyCursorPosition',
      set_cursorInsideWorkspace:'mod_workspace/SET_cursorInsideWorkspace',
      set_hideSidebar:          'globalView/SET_hideSidebar',
    }),
    ...mapActions({
      popupConfirm:         'globalView/GP_confirmPopup',
      net_trainingDone:     'globalView/NET_trainingDone',
      delete_network:       'mod_workspace/DELETE_network',
      set_openStatistics:   'mod_workspace/SET_openStatistics',
      set_openTest:         'mod_workspace/SET_openTest',
      set_elementUnselect:  'mod_workspace/SET_elementUnselect',
      set_networkName:      'mod_workspace/SET_networkName',
      event_startDoRequest: 'mod_workspace/EVENT_startDoRequest',
      set_chartRequests:    'mod_workspace/SET_chartsRequestsIfNeeded',
      tutorialPointActivate:'mod_tutorials/pointActivate',
      offMainTutorial:      'mod_tutorials/offTutorial',
    }),
    toggleSidebar() {
      this.set_hideSidebar(!this.hideSidebar)
    },
    // resize(newRect, i) {
    //   //console.log(newRect);
    //   //console.log(i);
    //   // this.network[i].meta.top = newRect.top;
    //   // this.network[i].meta.left = newRect.left;
    // },
    setTabNetwork(index) {
      this.set_showTrainingSpinner(false);
      if(this.statisticsIsOpen !== null) this.set_openStatistics(false);
      if(this.testIsOpen !== null) this.set_openTest(false);
      this.set_currentNetwork(index);
      this.set_elementUnselect();

      // request charts if the page has been refreshed, and 
      // the requested tab not being the first
      this.set_chartRequests(this.workspace[index].networkID);
    },
    deleteTabNetwork(index) {
      if(this.isTutorialMode) {
        this.popupConfirm(
          {
            text: 'Are you sure you want to end the tutorial?',
            ok: () => {
              this.offMainTutorial();
              this.delete_network(index)
            }
          });
      }
      else {
        this.delete_network(index)
      }
    },
    openStatistics(i) {
      this.setTabNetwork(i);
      this.$nextTick(()=>{
        this.set_openStatistics(true);
      })
    },
    openTest(i) {
      this.setTabNetwork(i);
      this.$nextTick(()=>{
        this.set_openTest(true);
      })
    },
    trainingFinished(index) {
      let networkStatus = this.workspace[index].networkMeta.coreStatus.Status;
      return networkStatus === 'Finished' || networkStatus === 'Testing';
    },
    trainingInProcess(index) {
      let networkStatus = this.workspace[index].networkMeta.coreStatus.Status;
      return networkStatus === 'Training' || networkStatus === 'Validation';
    },
    trainingWaiting(index) {
      return this.workspace[index].networkMeta.coreStatus.Status === 'Waiting';
    }
  }
}
