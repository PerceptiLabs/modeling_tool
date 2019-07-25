import html2canvas  from 'html2canvas';
import canvg        from 'canvg'
//const {dialog, } =   require('electron').remote;
//import fs           from 'fs';
import {mapActions, mapGetters, mapMutations, mapState} from 'vuex';

import { openSaveDialog, fileLocalSave, generateID }  from "@/core/helpers.js";

import TextEditable           from '@/components/base/text-editable.vue'
import NetworkField           from '@/components/network-field/network-field.vue'
import GeneralSettings        from "@/components/global-popups/workspace-general-settings.vue";
import GeneralResult          from "@/components/global-popups/workspace-result";
import SelectCoreSide         from "@/components/global-popups/workspace-core-side";
import WorkspaceBeforeImport  from "@/components/global-popups/workspace-before-import";
import TheStatistics          from "@/components/statistics/the-statistics.vue";
import TheTesting             from "@/components/statistics/the-testing.vue";
import TheViewBox             from "@/components/statistics/the-view-box";
import StartTrainingSpinner   from '@/components/different/start-training-spinner.vue'

export default {
  name: 'WorkspaceContent',
  components: {
    NetworkField, TextEditable,
    GeneralSettings, GeneralResult, SelectCoreSide, WorkspaceBeforeImport,
    TheStatistics, TheTesting, TheViewBox, StartTrainingSpinner
  },
  data() {
    return {
      trainingWasPaused: false
      //showTestingTab: false
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
      showTrainingSpinner:'mod_workspace/GET_showStartTrainingSpinner'
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
      if(newStatus === 'Finished' && this.testIsOpen === null) {
        this.$store.dispatch('globalView/NET_trainingDone');
        this.$store.dispatch('mod_workspace/EVENT_startDoRequest', false);
        //this.showTestingTab = true;
      }
    },
    coreStatus(newStatus, oldStatus) {
      if(newStatus.Status === 'Training' && oldStatus.Status === 'Training' && this.showTrainingSpinner)  {
        this.set_showTrainingSpinner(false);
      }
      else if(this.isTutorialMode && newStatus.Status === 'Training' && oldStatus.Status === 'Training' && !this.trainingWasPaused) {
        this.set_showTrainingSpinner(false);
        this.pauseTraining();
        this.trainingWasPaused = true;
      }

    },
    '$store.state.mod_events.saveNetwork': {
      handler() {
        this.saveNetwork();
      }
    },
    '$store.state.mod_events.saveNetworkAs': {
      handler() {
        this.saveNetworkAs();
      }
    },
    currentSelectedEl(newStatus) {
      if(newStatus.length > 0 && this.isTutorialMode && this.tutorialActiveStep === 'training') {
        this.$store.dispatch('mod_tutorials/pointActivate', {way: 'next', validation: newStatus[0].layerMeta.tutorialId});
      } 
    }
  },
  methods: {
    ...mapMutations({
      set_showTrainingSpinner:    'mod_workspace/SET_showStartTrainingSpinner'
    }),
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
      infoPopup:                'globalView/GP_infoPopup',
      pauseTraining:            'mod_api/API_pauseTraining'
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
    // onActivated(e) {
    //   //console.log(e)
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
    saveNetwork() {
      let projectsList = JSON.parse(localStorage.getItem('projectsList'));
      if(!projectsList) {
        this.saveNetworkAs();
        return
      }
      let idIndex = projectsList.findIndex((proj) => proj.id === this.currentNetwork.networkID);
      if(idIndex < 0) {
        this.saveNetworkAs();
        return
      }

      const network = this.currentNetwork;
      doScreenShot(this)
        .then((img)=> {
          const currentPath = projectsList[idIndex].path[0];
          const stringNet = cloneNet(network, img, currentPath);
          projectsList[idIndex] = JSON.parse(stringNet).project  ;
          fileLocalSave(currentPath, stringNet)
        })
        .then(()=> {
          this.$refs.networkField[0].$refs.network.style.filter = '';
          setLocalProjectsList(projectsList)
        })
        .catch((err)=> {console.log(err)});
    },
    saveNetworkAs() {
      const network = this.currentNetwork;
      let stringNetwork;
      doScreenShot(this)
        .then((img)=> {
          stringNetwork = cloneNet(network, img);
          const option = {
            title:"Save Network",
            defaultPath: `*/${network.networkName}`,
            filters: [
              {name: 'Text', extensions: ['json']},
            ]
          };
          return openSaveDialog(option);
        })
        .then((path)=> {
          return fileLocalSave(path, stringNetwork)
        })
        .then((t)=> {
          console.log(t);
          savePathToLocalStorage(JSON.parse(stringNetwork).project)
        })
        .catch((err)=> {
          console.log(err)
        })
        .finally(()=>{
          this.$refs.networkField[0].$refs.network.style.filter = '';
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
    }
  }
}

//SAVE NETWORK
// function openSaveDialog(jsonNet, dialogWin, network, ctx) {
//   const option = {
//     title:"Save Network",
//     defaultPath: `*/${network.networkName}`,
//     filters: [
//       {name: 'Text', extensions: ['json']},
//     ]
//   };
//
//   const fileName = dialogWin.showSaveDialog(null, option);
//
//   if (fileName === undefined){
//     ctx.infoPopup("You didn't save the file");
//     return;
//   }
//   saveFileToDisk(fileName, jsonNet, ctx, savePathToLocalStorage(JSON.parse(jsonNet).project))
// }
// function saveFileToDisk(fileName, jsonNet, ctx, successCallBack) {
//   fs.writeFile(fileName, jsonNet, (err) => {
//     if(err){
//       ctx.infoPopup(`An error occurred creating the file ${err.message}`);
//     }
//     ctx.infoPopup("The file has been successfully saved");
//     successCallBack;
//   });
//
// }
function doScreenShot(ctx) {
  return new Promise((resolve, reject)=> {
    const networkField = ctx.$refs.networkField[0].$refs.network;
    const svg = document.querySelector('.svg-arrow');
    const arrowsCanvas = document.createElement('canvas');
    arrowsCanvas.style.position = 'absolute';
    arrowsCanvas.style.zIndex = '0';
    networkField.appendChild(arrowsCanvas);
    canvg(arrowsCanvas, svg.outerHTML, {});
    svg.style.display = 'none';
    networkField.style.filter = 'blur(5px)';
    const options = {
      scale: 1,
      backgroundColor: 'null',
    };
    return html2canvas(networkField, options)
      .then((canvas)=> {
        resolve(canvas.toDataURL());
        svg.style.display = '';
        arrowsCanvas.remove();
      });
  })
}
function savePathToLocalStorage(project, path) {
  let projectsList = JSON.parse(localStorage.getItem('projectsList'));
  project.path.push(path);
  if(projectsList) {
    let idIndex = projectsList.findIndex((proj)=> proj.id === project.id);
    let pathIndex = projectsList.findIndex((proj)=> proj.path[0] === path);
    let idExist = idIndex >= 0 ? true : false;
    let pathExist = pathIndex >= 0 ? true : false;
    //to him self
    if(idExist && pathExist && idIndex === pathIndex) {
      projectsList[idIndex] = project
    }
    // затираем существующий
    if(pathExist && idIndex !== pathIndex) {
      project.id = generateID();
      projectsList[pathIndex] = project
    }
    //to add new
    if(!pathExist) {
      project.id = generateID();
      projectsList.push(project);
    }
  }
  else {
    projectsList = [];
    projectsList.push(project)
  }
  setLocalProjectsList(projectsList);
}
function setLocalProjectsList(list) {
  localStorage.setItem('projectsList', JSON.stringify(list))
}
function cloneNet(net, imgPath, filePath) {
  //clone network
  var outNet = {};
  for (var key in net) {
    if(key === 'networkElementList') {
      outNet[key] = JSON.parse(cloneEl(net[key]))
    }
    else {
      outNet[key] = net[key];
    }
  }

  //create project
  let time = new Date();
  var timeOptions = {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    timezone: 'UTC',
    hour: 'numeric',
    minute: 'numeric',
  };
  let toJson = {
    project: {
      time: time.toLocaleString("ru", timeOptions),
      image: imgPath,
      name: outNet.networkName,
      id: outNet.networkID,
      path: [],
      trainedPath: '',
      isCloud: false,
      isChecked: false,
      notExist: false
    },
    network: outNet
  };
  toJson.network.networkMeta = {};
  toJson.network.networkID = '';
  if(filePath) {
    toJson.project.path.push(filePath);
  }
  return JSON.stringify(toJson, null, ' ');
}
function cloneEl(el) {
  return JSON.stringify(el, (key, val)=> {
    if (key === 'calcAnchor') {
      return undefined;
    }
    return val;
  }, ' ');
}