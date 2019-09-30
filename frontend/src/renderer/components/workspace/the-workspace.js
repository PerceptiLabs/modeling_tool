import html2canvas  from 'html2canvas';
import canvg        from 'canvg'
import {mapActions, mapGetters, mapMutations, mapState} from 'vuex';

import { projectPCSave, generateID, loadPathFolder, deepCopy }  from "@/core/helpers.js";

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

export default {
  name: 'WorkspaceContent',
  components: {
    NetworkField, TextEditable,
    GeneralSettings, GeneralResult, SelectCoreSide, WorkspaceBeforeImport, WorkspaceSaveNetwork,
    TheStatistics, TheTesting, TheViewBox, StartTrainingSpinner
  },
  data() {
    return {
      trainingWasPaused: false
    }
  },
  computed: {
    ...mapGetters({
      currentNetwork:     'mod_workspace/GET_currentNetwork',
      currentSelectedEl:  'mod_workspace/GET_currentSelectedEl',
      isTutorialMode:     'mod_tutorials/getIstutorialMode',
      tutorialActiveStep: 'mod_tutorials/getActiveStep',
      testIsOpen:         'mod_workspace/GET_testIsOpen',
      statusNetworkCore:  'mod_workspace/GET_networkCoreStatus',
      statisticsIsOpen:   'mod_workspace/GET_statisticsIsOpen',
      showTrainingSpinner:'mod_workspace/GET_showStartTrainingSpinner',
      getLocalUserInfo:   'mod_user/GET_LOCAL_userInfo',
      //userId:             'mod_user/GET_userID',
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
        this.$store.dispatch('mod_workspace/SET_statusNetworkZoom', newValue/100);
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
        this.$store.dispatch('globalView/NET_trainingDone');
        this.$store.dispatch('mod_workspace/EVENT_startDoRequest', false);
      }
    },
    coreStatus(newStatus, oldStatus) {
      if(newStatus.Status === 'Training'
        && oldStatus.Status === 'Training'
        && this.showTrainingSpinner
      ) {
        this.set_showTrainingSpinner(false);
      }
      else if(this.isTutorialMode
        && newStatus.Status === 'Training'
        && oldStatus.Status === 'Training'
        && !this.trainingWasPaused
      ) {
        this.set_showTrainingSpinner(false);
        this.pauseTraining();
        this.trainingWasPaused = true;
      }

    },
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
        this.$store.dispatch('mod_tutorials/pointActivate', {
          way: 'next',
          validation: newStatus[0].layerMeta.tutorialId
        });
      } 
    }
  },
  methods: {
    ...mapMutations({
      set_showTrainingSpinner:  'mod_workspace/SET_showStartTrainingSpinner'
    }),
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
      infoPopup:                'globalView/GP_infoPopup',
      pauseTraining:            'mod_api/API_pauseTraining',
      checkTrainedNetwork:      'mod_api/API_checkTrainedNetwork',
      saveTrainedNetwork:       'mod_api/API_saveTrainedNetwork',
      saveLocalUserInfo:        'mod_user/UPDATE_LOCAL_userInfo',
      trackerModelSave:         'mod_tracker/EVENT_modelSave',
    }),
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
      this.$store.commit('mod_workspace/DELETE_network', index)
    },
    setTabNetwork(index) {
      this.set_showTrainingSpinner(false);
      if(this.statisticsIsOpen !== null) this.$store.dispatch('mod_workspace/SET_openStatistics', false);
      if(this.testIsOpen !== null) this.$store.dispatch('mod_workspace/SET_openTest', false);
      //if(this.isTutorialMode) return;
      this.$store.commit('mod_workspace/SET_currentNetwork', index);
      this.$store.dispatch('mod_workspace/SET_elementUnselect');
    },
    toggleSidebar() {
      this.$store.commit('globalView/SET_hideSidebar', !this.hideSidebar)
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
    editNetName(newName) {
      this.$store.dispatch('mod_workspace/SET_networkName', newName);
    },
    openStatistics(i) {
      this.setTabNetwork(i);
      this.$nextTick(()=>{
        this.$store.dispatch('mod_workspace/SET_openStatistics', true);
      })
    },
    openTest(i) {
      this.setTabNetwork(i);
      this.$nextTick(()=>{
        this.$store.dispatch('mod_workspace/SET_openTest', true);
      })
    },

    eventSaveNetwork() {
      const projectsList = this.getLocalUserInfo.projectsList;
      const network = this.currentNetwork;
      if(!projectsList.length || findIndexId(projectsList, network) < 0) {
        this.eventSaveNetworkAs();
        return
      }
      let idIndex = findIndexId(projectsList, network);
      const currentPath = projectsList[idIndex].pathProject[0];
      const currentPathFolder = currentPath.slice(0, -(network.networkID.length + 1));
      this.saveNetwork([currentPathFolder]);
    },
    eventSaveNetworkAs() {
      const projectsList = this.getLocalUserInfo.projectsList;
      const network = this.currentNetwork;
      let newProjId;
      if(findIndexId(projectsList, network) >= 0) {
        newProjId = generateID();
      }
      const option = {
        title: "Select folder",
        buttonLabel: "Select folder"
      };
      loadPathFolder(option)
        .then((path)=> {
          this.saveNetwork(path, newProjId)
        })
    },

    saveNetwork(savePath, newId) {
      const networkField = this.$refs.networkField[0].$refs.network;
      networkField.style.filter = 'blur(5px)';

      const currentNet = this.currentNetwork;
      const projectId = newId || currentNet.networkID;
      const pathSaveProject = [`${savePath[0]}\\${projectId}`];
      let prepareNet = cloneNet(currentNet, projectId, pathSaveProject);
      /*check Is Trained Net + do ScreenShot*/
      Promise.all([
        this.checkTrainedNetwork(),
        doScreenShot(networkField)
      ])
        .then((result)=> {
          /*prepare Net + ask what the file save*/
          const isTrainingNet = result[0];
          prepareNet.toLocal.image = result[1];
          if(isTrainingNet) return this.askSaveFilePopup();
          else return false;
        })
        .then((isSaveTrainedModel)=> {
          /*save files the core or front*/
          if(isSaveTrainedModel) {
            prepareNet.toLocal.isTrained = true;
            return this.saveTrainedNetwork({
              'Location': savePath,
              'frontendNetwork': prepareNet.toFile
            })
          }
          else {
            return projectPCSave(pathSaveProject, prepareNet.toFile)
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
    askSaveFilePopup() {
      return this.$refs.saveNetworkPopup[0].openPopup()
        .then((answer)=> answer)
        .catch((err)=> {

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
    pathProject: pathProject,
    pathModel: `${pathProject[0]}\\${idProject}.json`,
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
