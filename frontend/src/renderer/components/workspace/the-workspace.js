import {mapActions, mapGetters, mapMutations, mapState} from 'vuex';
import saveNet    from './workspace-save-net.js'
import scaleNet   from './workspace-scale.js'
import spinnerNet from './workspace-spinner.js'
import helpersNet from './workspace-helpers.js'
import Analytics  from '@/core/analytics'

import TextEditable           from '@/components/base/text-editable.vue'
import NetworkField           from '@/components/network-field/network-field.vue'
import GeneralResult          from "@/components/global-popups/workspace-result";
import SelectCoreSide         from "@/components/global-popups/workspace-core-side";
import WorkspaceBeforeImport  from "@/components/global-popups/workspace-before-import";
import WorkspaceSaveNetwork   from "@/components/global-popups/workspace-save-network.vue";
import FilePickerPopup        from "@/components/global-popups/file-picker-popup.vue";
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
    TheMiniMap, FilePickerPopup
  },
  mounted() {
    window.addEventListener('resize', this.onResize);
    this.$refs.tabset.addEventListener('wheel', this.onTabScroll);

    this.checkTabWidths();
    console.log(this.$refs.networkField);
    
    window.addEventListener('mousemove',  this.startCursorListener);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResize);

    if (!this.$refs.tabset) { return; }
    this.$refs.tabset.removeEventListener('wheel', this.onTabScroll);

    window.removeEventListener('mousemove', this.startCursorListener);
  },
  data() {
    return {
      trainingWasPaused: false,
      tabArrows: {
        show: false,
        isLeftActive: false,
        isRightActive: false,
      }
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
      dragBoxContainer:           state => state.mod_workspace.dragBoxContainer,
      statisticsElSelected:       state => state.mod_statistics.selectedElArr,
      hideSidebar:                state => state.globalView.hideSidebar,
      showGlobalResult:           state => state.globalView.globalPopup.showNetResult,
      showWorkspaceBeforeImport:  state => state.globalView.globalPopup.showWorkspaceBeforeImport,
      showCoreSide:               state => state.globalView.globalPopup.showCoreSideSettings,
      showFilePickerPopup:        state => state.globalView.globalPopup.showFilePickerPopup,
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

      if (this.statisticsIsOpen === null) {
        // added statisticsIsOpen null check
        // it is possible that the status is 'Finished' and both
        // testIsOpen and statisticsIsOpen to be null

        // this happens when the core is restarted and no longer has
        // any information about the stats, making training impossible
        return;
      }

      if(newStatus === 'Finished'
        && this.testIsOpen === null
      ) {
        // user journey tracking
        this.$store.dispatch('mod_tracker/EVENT_trainingCompleted');
        Analytics.googleAnalytics.trackCustomEvent('training-completed');

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
    },
    hideSidebar(newVal) {
      const timer = setTimeout(() => {
        this.checkTabWidths();
        clearTimeout(timer);
      }, 300); // transitionDuration of .page_sidebar element
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
      setNetworkNameAction:      'mod_workspace/SET_networkName',
      set_currentNetwork:   'mod_workspace/SET_currentNetwork',
      event_startDoRequest: 'mod_workspace/EVENT_startDoRequest',
      set_chartRequests:    'mod_workspace/SET_chartsRequestsIfNeeded',
      tutorialPointActivate:'mod_tutorials/pointActivate',
      offMainTutorial:      'mod_tutorials/offTutorial',
      pushSnapshotToHistory:'mod_workspace-history/PUSH_newSnapshot',
    }),
    startCursorListener (event) {
      const borderline = 15;
      this.set_cursorPosition({x: event.offsetX, y: event.offsetY});
      this.set_cursorInsideWorkspace(true);

      if(event.offsetX <= borderline ||
          event.offsetY <= borderline ||
          event.offsetY >= event.target.clientHeight - borderline ||
          event.offsetX >= event.target.clientWidth - borderline)
      {
        this.set_cursorInsideWorkspace(false);
      }
    },
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
                .then(_ => this.checkTabWidths());
            }
          });
      }
      else {
        this.delete_network(index)
          .then(_ => this.checkTabWidths());
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
    },
    set_networkName(text) {
      this.setNetworkNameAction(text);
      this.pushSnapshotToHistory(null)
    },
    onTabScroll(event) {
      event.preventDefault();

      if (!this.$refs.tablist) { return; }
      this.$refs.tablist.scrollLeft += event.deltaY | 0;

      this.checkTabWidths();
    },
    onTabArrowClick(value) {
      // when the scroll buttons are pressed

      if (!this.$refs.tablist) { return; }
      this.$refs.tablist.scrollLeft += value | 0;

      this.checkTabWidths();
    },
    onResize() {
      this.checkTabWidths();
    },
    checkTabWidths() {
      if (!this.$refs.tablist) { return; }

      console.group('checkTabWidths');
      
      console.log('this.$refs.tablist.scrollWidth', this.$refs.tablist.scrollWidth);
      console.log('this.$refs.tablist.clientWidth', this.$refs.tablist.clientWidth);
      console.log('this.$refs.tablist.scrollLeft', this.$refs.tablist.scrollLeft);
      
      // for rounding errors because of zoom levels
      const pixelToleranceLimit = 1; 
      // scrollWidth can be less than clientWidth!!
      const scrollableDistance = Math.abs(this.$refs.tablist.scrollWidth - this.$refs.tablist.clientWidth);
      const maxScrollWidth = 
        scrollableDistance <= pixelToleranceLimit
        ? Math.min(scrollableDistance, 0) // remove the tiny rounding difference 
        : scrollableDistance;
      
      console.log('maxScrollWidth', maxScrollWidth);

      this.tabArrows.isLeftActive = (this.$refs.tablist.scrollLeft !== 0);
      this.tabArrows.isRightActive = (this.$refs.tablist.scrollLeft !== maxScrollWidth);
      
      this.tabArrows.show = this.tabArrows.isLeftActive || this.tabArrows.isRightActive;
      console.log('---------------------------------------------');
      console.log('this.tabArrows.isLeftActive', this.tabArrows.isLeftActive);
      console.log('this.tabArrows.isRightActive', this.tabArrows.isRightActive);
      console.log('this.tabArrows.show', this.tabArrows.show);

      console.groupEnd();
      if (this.tabArrows.show && this.$refs.sidebarToggle) {
        this.$refs.sidebarToggle.style.marginLeft = 0;
      } else {
        this.$refs.sidebarToggle.style.marginLeft = 'auto';
      }

    },
    dragBoxHorizontalTopBorder() {
      const { width, left, top,  isVisible } = this.dragBoxContainer;
      const scaleCoefficient = this.scaleNet / 100;
      return {
        zIndex: 2,
        display: isVisible ? 'block' : 'none',
        width: width * scaleCoefficient + 'px',
        height: 1 + 'px',
        position: 'absolute',
        top: top * scaleCoefficient  + 'px',
        left: left * scaleCoefficient + 'px',
        borderTop: '1px dashed #22DDE5'
      }
    },
    dragBoxHorizontalBottomBorder() {
      const { width, height, left, top,  isVisible } = this.dragBoxContainer;
      const scaleCoefficient = this.scaleNet / 100;
      return {
        zIndex: 2,
        display: isVisible ? 'block' : 'none',
        width: width * scaleCoefficient + 'px',
        height: 1 + 'px',
        position: 'absolute',
        top: (top + height) * scaleCoefficient  + 'px',
        left: left * scaleCoefficient + 'px',
        borderTop: '1px dashed #22DDE5'
      }
    },

    dragBoxVerticalLeftBorder() {
      const { width, height, left, top,  isVisible } = this.dragBoxContainer;
      const scaleCoefficient = this.scaleNet / 100;
      return {
        zIndex: 2,
        display: isVisible ? 'block' : 'none',
        width: 1 + 'px',
        height: height * scaleCoefficient + 'px',
        position: 'absolute',
        top: top * scaleCoefficient  + 'px',
        left: left * scaleCoefficient + 'px',
        borderLeft: '1px dashed #22DDE5'
      }
    },
    dragBoxVerticalRightBorder() {
      const { width, height, left, top,  isVisible } = this.dragBoxContainer;
      const scaleCoefficient = this.scaleNet / 100;
      return {
        zIndex: 2,
        display: isVisible ? 'block' : 'none',
        width: 1 + 'px',
        height: height * scaleCoefficient + 'px',
        position: 'absolute',
        top: top * scaleCoefficient  + 'px',
        left: (left + width) * scaleCoefficient + 'px',
        borderRight: '1px dashed #22DDE5'
      }
    },
  }
}
