import {mapActions, mapGetters, mapMutations, mapState} from 'vuex';
import saveNet    from './workspace-save-net.js'
import scaleNet   from './workspace-scale.js'
import spinnerNet from './workspace-spinner.js'
import helpersNet from './workspace-helpers.js'
import {debounce} from '@/core/helpers'
import Analytics  from '@/core/analytics'
import { trainingElements, deepLearnElements }  from '@/core/constants.js';

import WorkspaceToolbar       from '../toolbar/workspace-toolbar.vue';
import StatisticsToolbar      from '../toolbar/statistics-toolbar.vue';

import TextEditable           from '@/components/base/text-editable.vue'
import NetworkField           from '@/components/network-field/network-field.vue'
import GeneralResult          from "@/components/global-popups/workspace-result";
import SelectCoreSide         from "@/components/global-popups/workspace-core-side";
import WorkspaceBeforeImport  from "@/components/global-popups/workspace-before-import";
import WorkspaceSaveNetwork   from "@/components/global-popups/workspace-save-network.vue";
import WorkspaceLoadNetwork   from "@/components/global-popups/workspace-load-network.vue";
import ExportNetwork          from "@/components/global-popups/export-network.vue";
import FilePickerPopup        from "@/components/global-popups/file-picker-popup.vue";
import TheTesting             from "@/components/statistics/the-testing.vue";
import TheViewBox             from "@/components/statistics/the-view-box";
import StartTrainingSpinner   from '@/components/different/start-training-spinner.vue'
import TheMiniMap             from '@/components/different/the-mini-map.vue'
import TheToaster             from '@/components/different/the-toaster.vue'
// import SidebarLayers          from '@/components/workspace/sidebar/workspace-sidebar-layers.vue'
import TheSidebar             from '@/components/the-sidebar.vue'
import Notebook               from '@/components/notebooks/notebook-container.vue';
import CodeWindow             from '@/components/workspace/code-window/workspace-code-window.vue';
import NotificationsWindow    from '@/components/workspace/notifications-window/workspace-notifications-window.vue';
import ResourceMonitor        from "@/components/charts/resource-monitor.vue";
import SelectModelModal       from '@/pages/projects/components/select-model-modal.vue';
import ViewBoxBtnList from '@/components/statistics/view-box-btn-list.vue'

export default {
  name: 'WorkspaceContent',
  mixins: [saveNet, scaleNet, spinnerNet, helpersNet],
  components: {
    WorkspaceToolbar, StatisticsToolbar,
    NetworkField, TextEditable,
    GeneralResult, SelectCoreSide,
    WorkspaceBeforeImport, WorkspaceSaveNetwork, WorkspaceLoadNetwork, ExportNetwork,
    TheTesting, TheViewBox, StartTrainingSpinner,
    TheToaster, TheMiniMap, FilePickerPopup, Notebook, TheSidebar,
    CodeWindow, NotificationsWindow,
    Notebook, ResourceMonitor, SelectModelModal,
    ViewBoxBtnList
  },
  mounted() {
    window.addEventListener('resize', this.onResize);
    this.$refs.tabset.addEventListener('wheel', this.onTabScroll);

    this.checkTabWidths();
    this.$nextTick().then(x => {
      this.scrollActiveTabIntoView();
    });
    
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
      },
      mouseDownIntervalTimer: null,
      showResourceView: 0,
      currentData: {
        Progress: 0,
        Memory: 0,
        CPU: 0
      },
      buffer: {},
      isCreateModelModalOpen: false
    }
  },
  computed: {
    ...mapGetters({
      currentSelectedEl:  'mod_workspace/GET_currentSelectedEl',
      currentElList:      'mod_workspace/GET_currentNetworkElementList',
      testIsOpen:         'mod_workspace/GET_testIsOpen',
      statusNetworkCore:  'mod_workspace/GET_networkCoreStatus',
      statisticsIsOpen:   'mod_workspace/GET_statisticsIsOpen',
      hasUnsavedChanges:  'mod_workspace-changes/get_hasUnsavedChanges',

      isTutorialMode:     'mod_tutorials/getIstutorialMode',
      isNotebookMode:     'mod_notebook/getNotebookMode',
      tutorialActiveStep: 'mod_tutorials/getActiveStep',
    }),
    ...mapState({
      showNewModelPopup:          state => state.globalView.globalPopup.showNewModelPopup,
      workspace:                  state => state.mod_workspace.workspaceContent,
      indexCurrentNetwork:        state => state.mod_workspace.currentNetwork,
      dragBoxContainer:           state => state.mod_workspace.dragBoxContainer,
      isCursorInsideWorkspace:    state => state.mod_workspace.positionForCopyElement.cursorInsideWorkspace,
      cursorPosition:             state => state.mod_workspace.positionForCopyElement.cursor,
      statisticsElSelected:       state => state.mod_statistics.selectedElArr,
      hideSidebar:                state => state.globalView.hideSidebar,
      showGlobalResult:           state => state.globalView.globalPopup.showNetResult,
      showWorkspaceBeforeImport:  state => state.globalView.globalPopup.showWorkspaceBeforeImport,
      showCoreSide:               state => state.globalView.globalPopup.showCoreSideSettings,
      showFilePickerPopup:        state => state.globalView.globalPopup.showFilePickerPopup,
      showLoadSettingPopup:       state => state.globalView.globalPopup.showLoadSettingPopup,
      showSaveNetworkPopup:       state => state.globalView.globalPopup.showSaveNetworkPopup,
      showExportNetworkPopup:     state => state.globalView.globalPopup.showExportNetworkPopup,
    }),

    hasStatistics() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkStatistics;
    },
    isStatistiOrTestOpened() {
      const currentItemNetwork = this.$store.getters['mod_workspace/GET_currentNetwork'];
      return currentItemNetwork.networkMeta.openStatistics === true || currentItemNetwork.networkMeta.openTest === true;
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
    },
    toolbarType() {

      if (this.statisticsIsOpen) {
        return 'StatisticsToolbar';
      }
      return 'WorkspaceToolbar';  
    },
    currentNetworkId() {
      return this.$store.getters['mod_workspace/GET_currentNetworkId'];
    },
    showCodeWindow() {
      return this.$store.getters['mod_workspace-code-editor/getCodeWindowState'](this.workspace[this.indexCurrentNetwork].networkID);
    },
    showNotificationWindow() {
      return this.$store.getters['mod_workspace-notifications/getNotificationWindowState'](this.workspace[this.indexCurrentNetwork].networkID);
    },
    workspaceErrors() {
      return this.$store.getters['mod_workspace-notifications/getErrors'](this.currentNetworkId).length;
    },
    toasterRightPosition() {

      let rightValueRm = 1;

      if (this.$store.state.globalView.hideSidebar) {
        rightValueRm += 25; // hardcoded in the-sidebar.vue file
      }

      if (this.showNotificationWindow) {
        rightValueRm += 70; // hardcoded in the workspace-code-window.vue file
      }
      
      return { right: `${rightValueRm}rem`};
    },

    statusNetworkInfo() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.coreStatus
    },
    doShowCharts() {
      return this.$store.getters['mod_workspace/GET_networkShowCharts']
    },
    isNeedWait() {
      return this.$store.getters['mod_workspace/GET_networkWaitGlobalEvent']
    },
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
    workspace(newVal) {
      // handles add/delete networks
      this.$nextTick()
        .then(x => {
          this.checkTabWidths();
          return this.$nextTick();
        })
        .then(x => {
          this.scrollActiveTabIntoView();
        });
    },
    hideSidebar(newVal) {
      const timer = setTimeout(() => {
        this.checkTabWidths();
        clearTimeout(timer);
      }, 300); // transitionDuration of .page_sidebar element
    },
    statusNetworkInfo(newVal) {
      this.isNeedWait
        ? this.buffer = newVal
        : this.currentData = newVal
    },
    doShowCharts() {
      this.isNeedWait
        ? this.currentData = this.buffer
        : null
    }
  },
  methods: {
    ...mapMutations({
      set_showTrainingSpinner:  'mod_workspace/SET_showStartTrainingSpinner',
      set_cursorPosition:       'mod_workspace/SET_CopyCursorPosition',
      set_cursorInsideWorkspace:'mod_workspace/SET_cursorInsideWorkspace',
      set_hideSidebar:          'globalView/SET_hideSidebar',
      GP_showCoreSideSettings:  'globalView/GP_showCoreSideSettings',

      setSelectedMetric:        'mod_statistics/setSelectedMetric',
      setLayerMetrics:          'mod_statistics/setLayerMetrics',
    }),
    ...mapActions({
      popupConfirm:         'globalView/GP_confirmPopup',
      net_trainingDone:     'globalView/NET_trainingDone',
      delete_network:       'mod_workspace/DELETE_network',
      set_openStatistics:   'mod_workspace/SET_openStatistics',
      set_openTest:         'mod_workspace/SET_openTest',
      set_elementUnselect:  'mod_workspace/SET_elementUnselect',
      setNetworkNameAction: 'mod_workspace/SET_networkName',
      set_currentNetwork:   'mod_workspace/SET_currentNetwork',
      event_startDoRequest: 'mod_workspace/EVENT_startDoRequest',
      set_chartRequests:    'mod_workspace/SET_chartsRequestsIfNeeded',
      tutorialPointActivate:'mod_tutorials/pointActivate',
      offMainTutorial:      'mod_tutorials/offTutorial',
      pushSnapshotToHistory:'mod_workspace-history/PUSH_newSnapshot',
      setNotificationWindowState: 'mod_workspace-notifications/setNotificationWindowState',
      popupNewModel:        'globalView/SET_newModelPopup',
    }),
    onCloseSelectModelModal() {
      this.popupNewModel(false);
    },
    startCursorListener (event) {
      const borderline = 15;
      const { x: oldX, y: oldY } = this.cursorPosition;
      const newX = event.offsetX - (event.offsetX % 10);
      const newY = event.offsetY  - (event.offsetY % 10);
      
      if((oldX !== newX) || (oldY !== newY)) {
        debounce(this.set_cursorPosition({x: newX, y: newY}), 60);
      }

      if(event.offsetX <= borderline ||
          event.offsetY <= borderline ||
          event.offsetY >= event.target.clientHeight - borderline ||
          event.offsetX >= event.target.clientWidth - borderline)
      {
        if(this.isCursorInsideWorkspace)
        this.set_cursorInsideWorkspace(false);
      } else {
        if(!this.isCursorInsideWorkspace)
        this.set_cursorInsideWorkspace(true);
      }
    },
    setResourceView(value) {
      if (this.showResourceView == 1 && value == 1) {
        this.showResourceView = 0;
      } else {
        this.showResourceView = value;
      }
    },
    toggleSidebar() {
      this.set_hideSidebar(!this.hideSidebar)
    },
    hasUnsavedChanges(networkId) {
      if (!networkId) { return false; }

      return this.$store.getters['mod_workspace-changes/get_hasUnsavedChanges'](networkId);

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

      this.notificationWindowStateHanlder(false);
    },
    deleteTabNetwork(index) {
      if(this.isTutorialMode) {
        this.popupConfirm(
          {
            text: 'Are you sure you want to end the tutorial?',
            ok: () => {
              this.offMainTutorial();
              this.delete_network(index);
            }
          });
      }
      else {
        let hasUnsavedChanges = this.hasUnsavedChanges(this.workspace[index].networkID);
        if (hasUnsavedChanges) {
          this.popupConfirm(
            {
              text: `Network ${this.workspace[index].networkName} has unsaved changes`,
              cancel: () => { return; },
              ok: () => {
                this.delete_network(index);
              }
            });
        } else {
          this.delete_network(index);
        }
      }
    },
    notificationWindowStateHanlder(value = false) {
      this.setNotificationWindowState({
        networkId: this.workspace[this.indexCurrentNetwork].networkID,
        value: value
      });
    },
    openStatistics(i) {
      this.$store.commit('mod_workspace/setViewType', 'statistic');
      this.setTabNetwork(i);
      this.$nextTick(()=>{
        this.set_openStatistics(true);
      })
    },
    openTest(i) {
      this.$store.commit('mod_workspace/setViewType', 'test');
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

      const scrollFactor = 20;
      const scrollDelta = event.deltaY > 0 ? scrollFactor : -1 * scrollFactor;
      this.$refs.tablist.scrollLeft += scrollDelta | 0;

      this.checkTabWidths();
    },
    onTabArrowMouseDown(value) {
      // when the scroll buttons are pressed

      if (!this.$refs.tablist) { return; }

      const mouseDownInterval = 100; //ms

      this.mouseDownIntervalTimer = setInterval(() => {
        this.$refs.tablist.scrollLeft += value | 0;
        this.checkTabWidths();
      }, mouseDownInterval);
    },
    onTabArrowMouseUp() {
      clearInterval(this.mouseDownIntervalTimer);
    },
    onResize() {
      debounce(this.checkTabWidths(), 100);
    },
    checkTabWidths() {
      if (!this.$refs.tablist) { return; }

      // for rounding errors because of zoom levels
      const pixelToleranceLimit = 1; 
      // scrollWidth can be less than clientWidth!!
      const scrollableDistance = Math.abs(this.$refs.tablist.scrollWidth - this.$refs.tablist.clientWidth);
      const maxScrollWidth = 
        scrollableDistance <= pixelToleranceLimit
        ? Math.min(scrollableDistance, 0) // remove the tiny rounding difference 
        : scrollableDistance;
      
      this.tabArrows.isLeftActive = (this.$refs.tablist.scrollLeft !== 0);
      this.tabArrows.isRightActive = Math.abs(Math.floor(this.$refs.tablist.scrollLeft) - maxScrollWidth) > pixelToleranceLimit;      
      this.tabArrows.show = this.tabArrows.isLeftActive || this.tabArrows.isRightActive;

      if (this.tabArrows.show && this.$refs.sidebarToggle) {
        this.$refs.sidebarToggle.style.marginLeft = 0;
      } else {
        this.$refs.sidebarToggle.style.marginLeft = 'auto';
      }

    },
    scrollActiveTabIntoView() {

      if (!this.$refs.tablist) { return; }

      const activeNetworkTab = document.querySelector('.bookmark_tab.workspace_tab.bookmark_tab--active');

      const tabArrow = document.querySelector('.tab-arrow');
      const sidebarToggle = document.querySelector('.toggle-sidebar');
  
      // adding activeNetworkTab.clientWidth so the entire tab is visible
      const widthNotVisible = 
        (activeNetworkTab.offsetLeft + activeNetworkTab.clientWidth) // position to end of tab
        + (tabArrow.clientWidth * 2) // size of arrow
        + sidebarToggle.clientWidth // size of sidebar toggle
        - this.$refs.tablist.clientWidth; // position of what's already in view

      if (widthNotVisible > 0) {
        this.$refs.tablist.scrollLeft += widthNotVisible;

        this.tabArrows.isLeftActive = true;
        this.tabArrows.isRightActive = false;
      }
      
    },
    dragBoxHorizontalTopBorder() {
      const { width, left, top,  isVisible } = this.dragBoxContainer;
      
      return {
        zIndex: 2,
        display: isVisible ? 'block' : 'none',
        width: width + 'px',
        height: 1 + 'px',
        position: 'absolute',
        top: top + 'px',
        left: left + 'px',
        borderTop: '1px dashed #22DDE5'
      }
    },
    dragBoxHorizontalBottomBorder() {
      const { width, height, left, top,  isVisible } = this.dragBoxContainer;

      return {
        zIndex: 2,
        display: isVisible ? 'block' : 'none',
        width: width + 'px',
        height: 1 + 'px',
        position: 'absolute',
        top: (top + height)  + 'px',
        left: left + 'px',
        borderTop: '1px dashed #22DDE5'
      }
    },

    dragBoxVerticalLeftBorder() {
      const { width, height, left, top,  isVisible } = this.dragBoxContainer;

      return {
        zIndex: 2,
        display: isVisible ? 'block' : 'none',
        width: 1 + 'px',
        height: height + 'px',
        position: 'absolute',
        top: top + 'px',
        left: left + 'px',
        borderLeft: '1px dashed #22DDE5'
      }
    },
    dragBoxVerticalRightBorder() {
      const { width, height, left, top,  isVisible } = this.dragBoxContainer;

      return {
        zIndex: 2,
        display: isVisible ? 'block' : 'none',
        width: 1 + 'px',
        height: height + 'px',
        position: 'absolute',
        top: top + 'px',
        left: (left + width) + 'px',
        borderRight: '1px dashed #22DDE5'
      }
    },
    addErrorNotification() {
      // used for test purposes 
      const networkId = this.workspace[this.indexCurrentNetwork].networkID;
      this.$store.dispatch('mod_workspace-notifications/addError', { networkId });
    },
    addWarningNotification() {
      // used for test purposes 
      const networkId = this.workspace[this.indexCurrentNetwork].networkID;
      this.$store.dispatch('mod_workspace-notifications/addWarning', { networkId });
    }
  }
}
