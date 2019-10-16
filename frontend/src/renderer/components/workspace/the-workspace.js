import html2canvas  from 'html2canvas';
import canvg        from 'canvg'
import {mapActions, mapGetters, mapMutations, mapState} from 'vuex';

import { projectPCSave, generateID, loadPathFolder, deepCopy }  from "@/core/helpers.js";
import { pathSlash }  from "@/core/constants.js";

import TextEditable           from '@/components/base/text-editable.vue'
import NetworkField           from '@/components/network-field/network-field.vue'
import GeneralSettings        from "@/components/global-popups/workspace-general-settings.vue";
import GeneralResult          from "@/components/global-popups/workspace-result";
import SelectCoreSide         from "@/components/global-popups/workspace-core-side";
import WorkspaceBeforeImport  from "@/components/global-popups/workspace-before-import";
import WorkspaceSaveNetwork   from "@/components/global-popups/workspace-save-network.vue";
import TheStatistics          from "@/components/statistics/the-statistics.vue";
import TheTesting             from "@/components/statistics/the-testing.vue";
import TheViewBox             from "@/components/statistics/the-view-box";
import StartTrainingSpinner   from '@/components/different/start-training-spinner.vue'
var unwatch;
export default {
  name: 'WorkspaceContent',
  components: {
    NetworkField, TextEditable,
    GeneralSettings, GeneralResult, SelectCoreSide,
    WorkspaceBeforeImport, WorkspaceSaveNetwork,
    TheStatistics, TheTesting, TheViewBox, StartTrainingSpinner
  },
  created() {


  },
  data() {
    return {
      trainingWasPaused: false,
      counterHideSpinner: 0,
      saveNetworkPopup: {
        show: false,
        existTrained: false,
        freezeInfo: false
      }
      //unwatch: null
    }
  },
  computed: {
    ...mapGetters({
      currentNetwork:     'mod_workspace/GET_currentNetwork',
      currentSelectedEl:  'mod_workspace/GET_currentSelectedEl',
      testIsOpen:         'mod_workspace/GET_testIsOpen',
      statusNetworkCore:  'mod_workspace/GET_networkCoreStatus',
      doShowCharts:       'mod_workspace/GET_networkShowCharts',
      statisticsIsOpen:   'mod_workspace/GET_statisticsIsOpen',
      showTrainingSpinner:'mod_workspace/GET_showStartTrainingSpinner',

      isTutorialMode:     'mod_tutorials/getIstutorialMode',
      tutorialActiveStep: 'mod_tutorials/getActiveStep',

      getLocalUserInfo:   'mod_user/GET_LOCAL_userInfo',
    }),
    ...mapState({
      workspace:                  state => state.mod_workspace.workspaceContent,
      indexCurrentNetwork:        state => state.mod_workspace.currentNetwork,
      statisticsElSelected:       state => state.mod_statistics.selectedElArr,
      hideSidebar:                state => state.globalView.hideSidebar,
      showGlobalSet:              state => state.globalView.globalPopup.showNetSettings,
      showGlobalResult:           state => state.globalView.globalPopup.showNetResult,
      showWorkspaceBeforeImport:  state => state.globalView.globalPopup.showWorkspaceBeforeImport,
      showCoreSide:               state => state.globalView.globalPopup.showCoreSideSettings,
    }),
    scaleNet: {
      get: function () {
        let zoom = this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom * 100;
        return Math.round(zoom);
      },
      set: function (newValue) {
        this.set_statusNetworkZoom(newValue/100);
      }
    },
    hasStatistics() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkStatistics;
    },
    networkMode() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.netMode
    },
    coreStatus() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.coreStatus
    },
    currentNet() {
      this.scale = this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.zoom;
      return this.$store.getters['mod_workspace/GET_currentNetworkElementList']
    },
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
      if(newStatus === 'Finished'
        && this.testIsOpen === null
      ) {
        this.net_trainingDone();
        this.event_startDoRequest(false);
      }
    },
    showTrainingSpinner(newVal) {
      //console.log('showTrainingSpinner', newVal);
      if(newVal) unwatch = this.$watch('doShowCharts', this.watch_doShowCharts);
      else unwatch();
    },
    // doShowCharts() {
    //   console.log('doShowCharts', this.counterHideSpinner);
    //   if(this.showTrainingSpinner) {
    //     if (this.counterHideSpinner === 2) {
    //       this.set_showTrainingSpinner(false);
    //       this.counterHideSpinner = 0
    //     } else ++this.counterHideSpinner;
    //   }
    // },
    // coreStatus(newStatus, oldStatus) {
    //   console.log('coreStatus', newStatus.Status, oldStatus.Status, this.showTrainingSpinner);
    //   if(newStatus.Status === 'Training'
    //     //&& oldStatus.Status === 'Training'
    //     && this.showTrainingSpinner
    //   ) {
    //     this.set_showTrainingSpinner(false);
    //   }
    //   else if(this.isTutorialMode
    //     && newStatus.Status === 'Training'
    //     //&& oldStatus.Status === 'Training'
    //     && !this.trainingWasPaused
    //   ) {
    //
    //   }
    //
    // },
    '$store.state.mod_events.saveNetwork': {
      handler() {
        this.eventSaveNetwork();
      }
    },
    '$store.state.mod_events.saveNetworkAs': {
      handler() {
        this.eventSaveNetworkAs();
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
      delete_network:           'mod_workspace/DELETE_network',
      set_currentNetwork:       'mod_workspace/SET_currentNetwork',
      set_hideSidebar:          'globalView/SET_hideSidebar',
    }),
    ...mapActions({
      infoPopup:            'globalView/GP_infoPopup',
      net_trainingDone:     'globalView/NET_trainingDone',

      pauseTraining:        'mod_api/API_pauseTraining',
      checkTrainedNetwork:  'mod_api/API_checkTrainedNetwork',
      saveTrainedNetwork:   'mod_api/API_saveTrainedNetwork',

      set_openStatistics:   'mod_workspace/SET_openStatistics',
      set_openTest:         'mod_workspace/SET_openTest',
      set_elementUnselect:  'mod_workspace/SET_elementUnselect',
      set_networkName:      'mod_workspace/SET_networkName',
      event_startDoRequest: 'mod_workspace/EVENT_startDoRequest',
      set_statusNetworkZoom:'mod_workspace/SET_statusNetworkZoom',

      tutorialPointActivate:'mod_tutorials/pointActivate',

      saveLocalUserInfo:    'mod_user/UPDATE_LOCAL_userInfo',
      trackerModelSave:     'mod_tracker/EVENT_modelSave',
      //enableLogHistory:     'mod_workspace-history/SET_isEnableHistory'
    }),
    watch_doShowCharts() {
      if (this.counterHideSpinner > 1) {
        this.set_showTrainingSpinner(false);
        this.counterHideSpinner = 0
      } else ++this.counterHideSpinner;
      //TODO need paused in tutorial
      //this.set_showTrainingSpinner(false);
      //     this.pauseTraining();
      //     this.trainingWasPaused = true;
    },
    calcScaleMap() {
      this.$nextTick(()=> {
        const net = this.$refs.networkField[0].$refs.network;
        const scaleH = net.offsetHeight/net.scrollHeight;
        const scaleW = net.offsetWidth/net.scrollWidth;
        const maxScale = scaleH < scaleW ? scaleH : scaleW;
        this.scaleNet = +maxScale.toFixed(1) * 100
      })
    },
    scaleScroll(e) {
      e.wheelDelta > 0
        ? this.incScale()
        : this.decScale();
    },
    deleteTabNetwork(index) {
      this.delete_network(index)
    },
    setTabNetwork(index) {
      //this.enableLogHistory(false);
      this.set_showTrainingSpinner(false);
      if(this.statisticsIsOpen !== null) this.set_openStatistics(false);
      if(this.testIsOpen !== null) this.set_openTest(false);
      //if(this.isTutorialMode) return;
      this.set_currentNetwork(index);
      this.set_elementUnselect();
      //this.$nextTick(()=> { this.enableLogHistory(true) })
    },
    toggleSidebar() {
      this.set_hideSidebar(!this.hideSidebar)
    },
    decScale() {
      if (this.scaleNet <= 30) this.scaleNet = 30;
      else this.scaleNet = this.scaleNet - 5
    },
    incScale () {
      if (this.scaleNet > 95) this.scaleNet = 100;
      else this.scaleNet = this.scaleNet + 5
    },
    // resize(newRect, i) {
    //   //console.log(newRect);
    //   //console.log(i);
    //   // this.network[i].meta.top = newRect.top;
    //   // this.network[i].meta.left = newRect.left;
    // },
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

    eventSaveNetwork() {
      //this.askSaveFilePopup();
      const projectsList = this.getLocalUserInfo.projectsList;
      const network = this.currentNetwork;
      this.checkTrainedNetwork()
        .then((isTrained)=> {
          console.log('isTrained', isTrained);
          this.saveNetworkPopup.existTrained = !!isTrained;
          if(!projectsList.length || findIndexId(projectsList, network) < 0) {
            console.log('save new net');
            this.eventSaveNetworkAs();
            return
          }
          if(isTrained) {
            console.log('save current trained net');
            this.eventSaveNetworkAs(network.networkID);
          }
          else {
            console.log('save current not trained net');
            const settings = {
              isSaveTrainedModel: false,
              projectName: network.networkName,
              projectPath: network.networkRootFolder
            };
            this.saveNetwork(settings, network.networkID)
          }
        })
    },
    eventSaveNetworkAs(netId) {
      console.log('eventSaveNetworkAs', netId);
      this.askSaveFilePopup(netId)
        .then((settings)=> {
          console.log('eventSaveNetworkAs answer', settings);
          this.saveNetwork(settings, netId);
        })
        .catch((err)=> {
          console.log('eventSaveNetworkAs err');
        })
    },
    askSaveFilePopup(isFreeze) {
      this.saveNetworkPopup.show = true;
      this.saveNetworkPopup.freezeInfo = !!isFreeze;
      return this.$nextTick()
        .then(()=>    this.$refs.saveNetworkPopup[0].openPopup())
        .catch(()=>   this.infoPopup('Project not saved'))
        .finally(()=> this.saveNetworkPopup.show = false)
    },
    saveNetwork(netInfo, netId) {
      // isSaveTrainedModel: true
      // projectName: "New_Network"
      // projectPath:
      console.log('saveNetwork netInfo', netInfo);
      const networkField = this.$refs.networkField[0].$refs.network;
      networkField.style.filter = 'blur(5px)';

      const currentNet = this.currentNetwork;
      const newProjectId = netId || generateID();
      //const rootProjectPath = netInfo.projectPath;
      //const projectId = newId || currentNet.networkID;
      const pathSaveProject = netInfo.projectPath + pathSlash + netInfo.projectName;
      let prepareNet = cloneNet(currentNet, newProjectId, pathSaveProject);
      console.log(prepareNet);
      /*check Is Trained Net + do ScreenShot*/
      doScreenShot(networkField)
        .then((img)=> {
          prepareNet.toLocal.image = img;
          console.log('сохранить через кор', netInfo.isSaveTrainedModel);
          if(netInfo.isSaveTrainedModel) {
            prepareNet.toLocal.isTrained = true;
            return this.saveTrainedNetwork({
              'Location': [pathSaveProject],
              'frontendNetwork': prepareNet.toFile
            })
          }
          else {
            console.log('doScreenShot else');
            return projectPCSave(prepareNet.toFile)
          }
        })
        .then(()=> {
          /*save project to project page*/
          saveProjectToLocalStore(prepareNet.toLocal, this);
          this.infoPopup('The file has been successfully saved');
          this.trackerModelSave(prepareNet.toFile);
        })
        .catch((error) => {})
        .finally(()=> {
          networkField.style.filter = '';
        });
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
  }
}

function doScreenShot(networkFieldEl) {
  return new Promise((resolve, reject)=> {
    const svg = document.querySelector('.svg-arrow');
    const arrowsCanvas = document.createElement('canvas');
    arrowsCanvas.style.position = 'absolute';
    arrowsCanvas.style.zIndex = '0';
    networkFieldEl.appendChild(arrowsCanvas);
    canvg(arrowsCanvas, svg.outerHTML, {});
    svg.style.display = 'none';

    const options = {
      scale: 1,
      backgroundColor: 'null',
    };
    return html2canvas(networkFieldEl, options)
      .then((canvas)=> {
        resolve(canvas.toDataURL());
      })
      .finally(()=> {
        svg.style.display = '';
        arrowsCanvas.remove();
      })

  })
}

function saveProjectToLocalStore(project, ctx) {
  let projectsLocalList = deepCopy(ctx.getLocalUserInfo.projectsList);

  if(projectsLocalList.length) {
    const idIndex = projectsLocalList.findIndex((proj)=> proj.id === project.id);
    const pathIndex = projectsLocalList.findIndex((proj)=> proj.pathModel === project.pathModel);
    const idExist = idIndex >= 0;
    const pathExist = pathIndex >= 0;

    if(idExist && pathExist && idIndex === pathIndex) projectsLocalList[idIndex] = project; //to him self
    else projectsLocalList.push(project) //create new
  }
  else {
    projectsLocalList.push(project)
  }
  ctx.saveLocalUserInfo({key: 'projectsList', data: projectsLocalList });
}

function cloneNet(net, idProject, pathProject) {
  //clone network
  let toFile = {};
  for (var key in net) {
    if(key === 'networkElementList') toFile[key] = JSON.parse(cloneEl(net[key]));
    else toFile[key] = net[key];
  }
  if(idProject) toFile.networkID = idProject;
  toFile.networkMeta = {};
  toFile.networkRootFolder = pathProject;
  //create project
  const time = new Date();
  const timeOptions = {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    timezone: 'UTC',
    hour: 'numeric',
    minute: 'numeric',
  };
  const toLocal = {
    time: time.toLocaleString("ru", timeOptions),
    image: null,
    name: toFile.networkName,
    id: idProject,
    //networkRootFolder: pathProject,
    pathProject: pathProject,
    isTrained: false,
    isCloud: false,
  };
  return {
    toFile,
    toLocal
  }
}
function cloneEl(el) {
  return JSON.stringify(
    el,
    (key, val)=> {
      if (key === 'calcAnchor') return undefined;
      else if(key === 'isSelected') return false;
      else return val;
    },
    ' ');
}
function findIndexId(list, currentNet) {
  return list.findIndex((proj) => proj.id === currentNet.networkID)
}
