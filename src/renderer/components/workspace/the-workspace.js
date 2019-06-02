import html2canvas  from 'html2canvas';
import canvg        from 'canvg'
import {remote}     from 'electron'
import fs           from 'fs';
import {mapActions, mapGetters} from 'vuex';

import { generateID }  from "@/core/helpers.js";

import TextEditable     from '@/components/base/text-editable.vue'
import NetworkField     from '@/components/network-field/network-field.vue'
import GeneralSettings  from "@/components/global-popups/workspace-general-settings.vue";
import GeneralResult    from "@/components/global-popups/workspace-result";
import SelectCoreSide   from "@/components/global-popups/workspace-core-side";
import TheStatistics    from "@/components/statistics/the-statistics.vue";
import TheTesting       from "@/components/statistics/the-testing.vue";
import TheViewBox       from "@/components/statistics/the-view-box";

export default {
  name: 'WorkspaceContent',
  components: {
    NetworkField, TextEditable,
    GeneralSettings, GeneralResult,
    SelectCoreSide,
    TheStatistics, TheTesting, TheViewBox,
  },
  data() {
    return {
      showTestingTab: false,
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
    networkMode() {
      return this.$store.getters['mod_workspace/GET_currentNetwork'].networkMeta.netMode
    },
    statisticsElSelected() {
      return this.$store.state.mod_statistics.selectedElArr
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
    }
  },
  watch: {
    statusNetworkCore(newStatus) {
      if(newStatus === 'Finished' && this.showTestingTab === false) {
        this.$store.dispatch('globalView/NET_trainingDone');
        this.$store.dispatch('mod_workspace/EVENT_startDoRequest', false);
        this.showTestingTab = true;
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
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
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
      this.$store.commit('mod_workspace/SET_currentNetwork', index);
      this.$store.dispatch('mod_workspace/SET_elementUnselect');
      if(this.statisticsIsOpen !== null) this.$store.dispatch('mod_workspace/SET_openStatistics', false);
      if(this.testIsOpen !== null) this.$store.dispatch('mod_workspace/SET_openTest', false);
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
      this.$store.dispatch('mod_workspace/SET_openStatistics', true);
    },
    openTest(i) {
      this.setTabNetwork(i);
      this.$store.dispatch('mod_workspace/SET_openTest', true);
    },
    saveNetwork(){
      let projectsList = JSON.parse(localStorage.getItem('projectsList'));
      if(projectsList) {
        let idIndex = projectsList.findIndex((proj) => proj.id === this.currentNetwork.networkID);
        let idExist = idIndex >= 0 ? true : false;
        if(idExist) {
          const network = this.currentNetwork;
          doScreenShot(this)
            .then((img)=> {
              const currentPath = projectsList[idIndex].path[0];
              const stringNet = cloneNet(network, img, currentPath);
              projectsList[idIndex] = JSON.parse(stringNet).project  ;
              saveFileToDisk(currentPath, stringNet, this, setLocalProjectsList(projectsList))
            })
            .catch((err)=> {console.log(err)});
        }
        else this.saveNetworkAs();
      }
      else this.saveNetworkAs();
    },
    saveNetworkAs() {
      const dialog = remote.dialog;
      const network = this.currentNetwork;
      doScreenShot(this)
        .then((img)=> {
          const stringNet = cloneNet(network, img);
          openSaveDialog(stringNet, dialog, network, this)
        })
        .catch((err)=> {console.log(err)});
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
function openSaveDialog(jsonNet, dialogWin, network, ctx) {
  const option = {
    title:"Save Network",
    defaultPath: `*/${network.networkName}`,
    filters: [
      {name: 'Text', extensions: ['json']},
    ]
  };

  dialogWin.showSaveDialog(null, option, (fileName) => {
    if (fileName === undefined){
      ctx.$store.dispatch('globalView/GP_infoPopup', "You didn't save the file");
      return;
    }
    saveFileToDisk(fileName, jsonNet, ctx, savePathToLocal(JSON.parse(jsonNet).project, fileName))
  });
}
function saveFileToDisk(fileName, jsonNet, ctx, successCallBack) {
  fs.writeFile(fileName, jsonNet, (err) => {
    if(err){
      ctx.$store.dispatch('globalView/GP_infoPopup', "An error occurred creating the file "+ err.message)
    }

    ctx.$store.dispatch('globalView/GP_infoPopup', "The file has been successfully saved");
    successCallBack;
  });
}
function doScreenShot(ctx) {
  return new Promise((resolve, reject)=> {
    const workspace = ctx.$refs.workspaceNet;
    const svg = workspace.querySelector('.svg-arrow');
    const arrowsCanvas = document.createElement('canvas');
    arrowsCanvas.style.position = 'absolute';
    arrowsCanvas.style.zIndex = '0';
    ctx.$refs.infoSectionName[0].appendChild(arrowsCanvas);
    canvg(arrowsCanvas, svg.outerHTML, {});
    svg.style.display = 'none';
    workspace.style.background = 'none';
    const options = {
      scale: 1,
      backgroundColor: null,
    };
    return html2canvas(workspace, options)
      .then((canvas)=> {
        resolve(canvas.toDataURL());
        svg.style.display = '';
        workspace.style.background = '';
        arrowsCanvas.remove();
      });
  })
}
function savePathToLocal(project, path) {
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