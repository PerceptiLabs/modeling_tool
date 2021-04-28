import {mapActions, mapGetters, mapMutations, mapState} from 'vuex';
import saveNet    from './workspace-save-net.js'
import scaleNet   from './workspace-scale.js'
import spinnerNet from './workspace-spinner.js'
import helpersNet from './workspace-helpers.js'
import {debounce} from '@/core/helpers'
import { 
  TRACKER_SCREENNAME_WORKSPACE,
  TRACKER_SCREENNAME_WORKSPACE_TRAINING,
  TRACKER_SCREENNAME_STATISTICS,
  TRACKER_SCREENNAME_STATISTICS_TRAINING,
  TRACKER_SCREENNAME_TEST,
  TRACKER_SCREENNAME_TEST_TRAINING } from "@/core/constants";
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
import ExportNetworkGitHub    from "@/components/global-popups/export-network-git-hub.vue";
import ImportModel            from "@/components/global-popups/import-model-popup.vue";
import FilePickerPopup        from "@/components/global-popups/file-picker-popup.vue";
import GlobalTrainingSettings        from "@/components/global-popups/global-training-settings.vue";
import TheTesting             from "@/components/statistics/the-testing.vue";
import TheViewBox             from "@/components/statistics/the-view-box";
import StartTrainingSpinner   from '@/components/different/start-training-spinner.vue'
import TheMiniMap             from '@/components/different/the-mini-map.vue'
import TheToaster             from '@/components/different/the-toaster.vue'
import TheSidebar             from '@/components/the-sidebar.vue'
import Notebook               from '@/components/notebooks/notebook-container.vue';
import CodeWindow             from '@/components/workspace/code-window/workspace-code-window.vue';
import InformationPanel       from '@/components/workspace/information-panel/information-panel.vue';
import EmptyNavigation        from '@/components/empty-navigation/empty-navigation.vue';
import ResourceMonitor        from "@/components/charts/resource-monitor.vue";
import SelectModelModal       from '@/pages/projects/components/select-model-modal.vue';
import ViewBoxBtnList         from '@/components/statistics/view-box-btn-list.vue'
import ModelStatus            from '@/components/different/model-status.vue';
import MiniMapNavigation      from '@/components/workspace/mini-map-navigation.vue';
import ChartSpinner           from '@/components/charts/chart-spinner'

import { saveModelJson as fileserver_saveModelJson } from '@/core/apiFileserver';

export default {
  name: 'WorkspaceContent',
  mixins: [saveNet, scaleNet, spinnerNet, helpersNet],
  components: {
    WorkspaceToolbar, StatisticsToolbar,
    NetworkField, TextEditable,
    GeneralResult, SelectCoreSide,
    WorkspaceBeforeImport, WorkspaceSaveNetwork, WorkspaceLoadNetwork, ExportNetwork, ExportNetworkGitHub, ImportModel,
    TheTesting, TheViewBox, StartTrainingSpinner,
    TheToaster, TheMiniMap, FilePickerPopup, TheSidebar,
    CodeWindow, InformationPanel,
    Notebook, ResourceMonitor, SelectModelModal,
    ViewBoxBtnList, EmptyNavigation,
    ModelStatus,
    MiniMapNavigation,
    ChartSpinner,
    GlobalTrainingSettings
  },
  mounted() {
    window.addEventListener('resize', this.onResize);
    if(this.$refs.tabset) this.$refs.tabset.addEventListener('wheel', this.onTabScroll);

    this.checkTabWidths();
    this.$nextTick().then(x => {
      this.scrollActiveTabIntoView();
    });
    window.addEventListener('mousemove',  this.startCursorListener);
    window.addEventListener('contextmenu', this.preventEvent)
  },
  beforeDestroy() {
    if (this.isTraining) {
      this.setHeadless(true);
    }
    window.removeEventListener('contextmenu', e => e.preventDefault())

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
      isCreateModelModalOpen: false,
      debouncedCopyCursorPositionFn: null,
    }
  },
  created() {
    this.debouncedCopyCursorPositionFn = debounce(function(x, y) {
      this.set_cursorPosition({x, y});
    }, process.env.NODE_ENV === 'production' ? 60 : 4000)
  },
  computed: {
    ...mapGetters({
      currentSelectedEl:  'mod_workspace/GET_currentSelectedEl',
      currentElList:      'mod_workspace/GET_currentNetworkElementList',
      testIsOpen:         'mod_workspace/GET_testIsOpen',
      statusNetworkCore:  'mod_workspace/GET_networkCoreStatus',
      statisticsIsOpen:   'mod_workspace/GET_statisticsIsOpen',
      currentModelIndex:  'mod_workspace/GET_currentModelIndex',
      currentStatsIndex:  'mod_workspace/GET_currentStatsIndex',
      currentTestIndex:   'mod_workspace/GET_currentTestIndex',
      getViewType:        'mod_workspace/GET_viewType',

      isTutorialMode:     'mod_tutorials/getIsTutorialMode',
      getShowTutorialTips:'mod_tutorials/getShowTutorialTips',
      getCurrentStepCode: 'mod_tutorials/getCurrentStepCode',
      isNotebookMode:     'mod_notebook/getNotebookMode',
      emptyNavigationMode:'mod_empty-navigation/getEmptyScreenMode',
      isTraining:         'mod_workspace/GET_networkIsTraining',
      currentNetwork:     'mod_workspace/GET_currentNetwork',
      getIsWorkspaceDragEvent: 'mod_events/getIsWorkspaceDragEvent',
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
      showExportNetworkToGitHubPopup:     state => state.globalView.globalPopup.showExportNetworkToGitHubPopup,
      showImportNetworkfromGitHubOrLocalPopup:     state => state.globalView.globalPopup.showImportNetworkfromGitHubOrLocalPopup,
      isMiniMapNavigatorOpened:   state => state.globalView.isMiniMapNavigatorOpened,
      isGlobalTrainingSettingsPopupOpened: state => state.globalView.globalPopup.showGlobalTrainingSettingsPopup.isOpen,
      coreVersions:               state => state.mod_api.coreVersions || {}
    }),
    

    hasStatistics() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkStatistics;
    },
    isStatisticsOrTestOpened() {
      const currentItemNetwork = this.$store.getters['mod_workspace/GET_currentNetwork'];
      return currentItemNetwork.networkMeta.openStatistics === true || currentItemNetwork.networkMeta.openTest === true;
    },
    networkMode() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.netMode
    },
    coreStatus() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.coreStatus
    },
    statusLocalCore() {
      return this.$store.state.mod_api.statusLocalCore;
    },
    kernelLabel() {
      if(this.statusLocalCore !== "online") {
        return "Kenerl is not connected";
      } else {
        return "Kenerl is connected";
      }
    },
    // currentNet() {
    //   this.scale = this.$store.getters['mod_workspace/GET_currentNetworkZoom'];
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
    getNotificationWindowSelectedTab() {

      if (!this.workspace[this.indexCurrentNetwork]) {
        return '';
      }

      return this.$store.getters['mod_workspace-notifications/getNotificationWindowSelectedTab'](this.workspace[this.indexCurrentNetwork].networkID);
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
    isGridEnabled: {
      get() {
        return this.$store.state.globalView.isGridEnabled 
      },
      set(value) {
        this.setGridValue(value);
      }
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
        this.$store.dispatch('mod_tracker/EVENT_trainingCompleted', 'Finished training');

        const currentNetwork = this.$store.getters['mod_workspace/GET_currentNetwork'];
        this.$store.dispatch('mod_webstorage/saveNetwork', currentNetwork, {root: true});
        this.net_trainingDone();
        this.event_startDoRequest(false);
        this.setChecklistItemComplete({ itemId: 'finishTraining' });
      }
    },
    isTraining: {
      handler(newVal, oldVal) {
        
        // When the "autoupdate previews" task is done, this "if" needs to be expanded
        // with a check to include: this.getViewType === 'model'
        if (newVal && this.getViewType === 'statistic') {
          this.setHeadless(false);
          return;
        }

        this.setHeadless(true);
      },
      immediate: true
    },
    currentSelectedEl(newStatus) {
      if(newStatus.length > 0
        && this.isTutorialMode
        && this.tutorialActiveStep === 'training'
      ) {
        // add tutorial trigger here
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
    },
    getCurrentStepCode: {
      handler(newVal, oldVal) {
        if (!this.getShowTutorialTips) {
          this.deactivateCurrentStep();
          return;
        }
      },
      immediate: true
    }
  },
  methods: {
    ...mapMutations({
      set_showTrainingSpinner:  'mod_workspace/SET_showStartTrainingSpinner',
      set_cursorPosition:       'mod_workspace/SET_CopyCursorPosition',
      set_cursorInsideWorkspace:'mod_workspace/SET_cursorInsideWorkspace',
      set_currentModelIndex:    'mod_workspace/set_currentModelIndex',
      set_hideSidebar:          'globalView/SET_hideSidebar',
      GP_showCoreSideSettings:  'globalView/GP_showCoreSideSettings',
      setSelectedMetric:        'mod_statistics/setSelectedMetric',
      setLayerMetrics:          'mod_statistics/setLayerMetrics',
      setMiniMapNavigationMutation:   'globalView/setMiniMapNavigationMutation',
      setGridValue:             'globalView/setGridStateMutation',
    }),
    ...mapActions({
      popupConfirm:               'globalView/GP_confirmPopup',
      net_trainingDone:           'globalView/NET_trainingDone',
      saveNetwork:                'mod_webstorage/saveNetwork',
      delete_network:             'mod_workspace/DELETE_network',
      set_openStatistics:         'mod_workspace/SET_openStatistics',
      set_openTest:               'mod_workspace/SET_openTest',
      set_elementUnselect:        'mod_workspace/SET_elementUnselect',
      setNetworkNameAction:       'mod_workspace/SET_networkName',
      set_currentNetwork:         'mod_workspace/SET_currentNetwork',
      event_startDoRequest:       'mod_workspace/EVENT_startDoRequest',
      set_chartRequests:          'mod_workspace/SET_chartsRequestsIfNeeded',
      closeStatsTestViews:        'mod_workspace/SET_statisticsAndTestToClosed',
      activateCurrentStep:        'mod_tutorials/activateCurrentStep',
      deactivateCurrentStep:      'mod_tutorials/deactivateCurrentStep',
      setChecklistItemComplete:   'mod_tutorials/setChecklistItemComplete',
      pushSnapshotToHistory:      'mod_workspace-history/PUSH_newSnapshot',
      setNotificationWindowState: 'mod_workspace-notifications/setNotificationWindowState',
      popupNewModel:              'globalView/SET_newModelPopup',
      SET_emptyScreenMode:        'mod_empty-navigation/SET_emptyScreenMode',
    }),
    onCloseSelectModelModal() {
      this.popupNewModel(false);
    },
    startCursorListener (event) {
      const networkFieldRect = document.getElementsByClassName('network-field')[0].getBoundingClientRect();
      const workspaceRect = document.getElementById('networkWorkspace').getBoundingClientRect();

      const eventX = event.x - networkFieldRect.left;
      const eventY = event.y - networkFieldRect.top;
      const borderline = 15;
      const { x: oldX, y: oldY } = this.cursorPosition;
      const newX = eventX - (eventX % 10);
      const newY = eventY  - (eventY % 10);
      
      if((oldX !== newX) || (oldY !== newY)) {
        this.debouncedCopyCursorPositionFn(newX, newY);
      }

      if(event.x <= workspaceRect.left + borderline ||
          event.y <= workspaceRect.top + borderline ||
          event.y >= workspaceRect.bottom - borderline ||
          event.x >= workspaceRect.right - borderline)
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
    // resize(newRect, i) {s
    //   //console.log(newRect);
    //   //console.log(i);
    //   // this.network[i].meta.top = newRect.top;
    //   // this.network[i].meta.left = newRect.left;
    // },
    setTabNetwork(index) {
      this.set_showTrainingSpinner(false);
      this.set_currentNetwork(index);
      // this.set_openStatistics(false);
      // this.set_openTest(false);
      this.closeStatsTestViews({ networkId: this.workspace[index].networkID });
      this.set_elementUnselect();

      // request charts if the page has been refreshed, and
      // the requested tab not being the first
      this.set_chartRequests(this.workspace[index].networkID);

      this.notificationWindowStateHandlerNew(this.getNotificationWindowSelectedTab); 
      this.$store.commit('mod_workspace/set_currentModelIndex', index);

    },
    hideModelTab(index) {
      const networkID = this.workspace[index].networkID;
      let hasUnsavedChanges = this.hasUnsavedChanges(networkID);

      if (hasUnsavedChanges) {
        this.popupConfirm(
          {
            text: `${this.workspace[index].networkName} has unsaved changes`,
            cancel: () => { return; },
            ok: () => {
              this.updateUnsavedChanges({
                networkId: this.workspace[index].networkID, 
                value: false
              });

              hideProcess(this);
            }
          });
      } else {
        hideProcess(this);
      }

      function hideProcess(parent) {
        parent.$store.commit('mod_workspace/update_network_meta', {key: 'hideModel', networkID: networkID, value: true});
        // console.log('hiding', parent.currentModelIndex, index);

        parent.saveNetwork(parent.workspace[index]);
        fileserver_saveModelJson(parent.workspace[index]);

        if (parent.currentModelIndex===index) {
          const candidate = parent.workspace.findIndex(item => item.networkMeta.hideModel!=true);
  
          if (candidate > -1) {
            parent.setTabNetwork(candidate);
          } else {
            parent.SET_emptyScreenMode(1);
            parent.$store.commit('mod_workspace/set_currentModelIndex', -1);
            parent.$store.dispatch('mod_notebook/SET_notebookMode', false);
          }
        }
      }
    },
    hideStatsTab(index) {
      const networkID = this.workspace[index].networkID;
      this.$store.commit('mod_workspace/update_network_meta', {key: 'hideStatistics', networkID: networkID, value: true});

      if (this.currentStatsIndex===index) {
        const candidate = this.workspace.findIndex(item => typeof item.networkMeta.openStatistics === 'boolean' && item.networkMeta.hideStatistics!==true);

        if (candidate > -1) {
          this.$store.dispatch('mod_workspace/SET_currentNetwork', candidate);
          this.$store.commit('mod_workspace/set_currentStatsIndex', candidate);
          this.set_openStatistics(true);
        } else {
          this.SET_emptyScreenMode(2);
          this.$store.commit('mod_workspace/set_currentStatsIndex', -1);
        }
      }

    },
    hideTestTab(index) {
      const networkID = this.workspace[index].networkID;
      this.$store.commit('mod_workspace/update_network_meta', {key: 'hideTest', networkID: networkID, value: true});


      if (this.currentTestIndex===index) {
        const candidate = this.workspace.findIndex(item => typeof item.networkMeta.openTest === 'boolean' && item.networkMeta.hideTest!==true);

        if (candidate > -1) {
          this.$store.dispatch('mod_workspace/SET_currentNetwork', candidate);
          this.$store.commit('mod_workspace/set_currentTestIndex', candidate);
          this.set_openTest(true);
        } else {
          this.SET_emptyScreenMode(3);
          this.$store.commit('mod_workspace/set_currentTestIndex', -1);
        }
      }

    },
    deleteTabNetwork(index) {
      let hasUnsavedChanges = this.hasUnsavedChanges(this.workspace[index].networkID);
      if (hasUnsavedChanges) {
        this.popupConfirm(
          {
            text: `${this.workspace[index].networkName} has unsaved changes`,
            cancel: () => { return; },
            ok: () => {
              this.delete_network(index);
            }
          });
      } else {
        this.delete_network(index);
      }
    },
    notificationWindowStateHandlerNew(selectedTab){
      let state = true;
      if(selectedTab === this.getNotificationWindowSelectedTab) {
        state = false;
      }
      let tab =  !state ? '' : selectedTab;

      this.setNotificationWindowState({
        networkId: this.workspace[this.indexCurrentNetwork].networkID,
        value: state,
        selectedTab: tab,
      });
      
      this.$store.dispatch('mod_tracker/EVENT_consoleWindowToggle', { value: state, selectedTab: selectedTab });
    },
    openStatistics(i) {
      this.$store.dispatch('mod_workspace/setViewType', 'statistic');
      this.$store.dispatch('mod_workspace/SET_currentNetwork', i);
      this.$store.dispatch('mod_workspace/SET_currentStatsIndex', i);
      this.set_openStatistics(true);
    },
    openTest(i) {
      this.$store.dispatch('mod_workspace/setViewType', 'test');
      
      // --- MERGE CHANGES ---
      // this.setTabNetwork(i);
      // this.$nextTick(()=>{
      //   this.set_openTest(true);
      // })
      // --- MERGE CHANGES ---

      this.$store.dispatch('mod_workspace/SET_currentNetwork', i);
      this.$store.dispatch('mod_workspace/SET_currentTestIndex', i);
      this.set_openTest(true);
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
      this.$store.dispatch('mod_workspace-notifications/addError', { networkId, addToast: true });
    },
    addWarningNotification() {
      // used for test purposes 
      const networkId = this.workspace[this.indexCurrentNetwork].networkID;
      this.$store.dispatch('mod_workspace-notifications/addWarning', { networkId, addToast: true });
    },
    openTerminalConsole() {
      console.log('open terminal console')
    },
    setHeadless(isHeadless) {
      this.$store.dispatch('mod_api/API_setHeadless', isHeadless, {root: true})
    },
    preventEvent(e) {
      e.preventDefault();
    }
  }
}
