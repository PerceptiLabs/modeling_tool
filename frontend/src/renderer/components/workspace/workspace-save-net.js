import html2canvas  from 'html2canvas';
import canvg        from 'canvg'
import { projectPCSave, generateID, loadPathFolder, deepCopy }  from "@/core/helpers.js";
import { pathSlash }  from "@/core/constants.js";
import { mapGetters, mapMutations, mapActions } from "vuex";

const workspaceSaveNet = {
  created() {
    this.refreshSavePopup();
  },
  data() {
    return {
      saveNetworkPopupDefault: {
        show: false,
        isFreezeInfo: false,
        isSyncName: false
      },
      saveNetworkPopup: null
    }
  },
  computed: {
    ...mapGetters({
      currentNetwork: 'mod_workspace/GET_currentNetwork',
      getLocalUserInfo:   'mod_user/GET_LOCAL_userInfo',
    })
  },
  watch: {
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
  },
  methods: {
    ...mapMutations({
      setUnsavedChanges:    'mod_workspace-changes/set_hasUnsavedChanges',
    }),
    ...mapActions({
      infoPopup:            'globalView/GP_infoPopup',
      set_networkRootFolder:'mod_workspace/SET_networkRootFolder',
      checkTrainedNetwork:  'mod_api/API_checkTrainedNetwork',
      saveTrainedNetwork:   'mod_api/API_saveTrainedNetwork',
      trackerModelSave:     'mod_tracker/EVENT_modelSave',
      saveLocalUserInfo:    'mod_user/UPDATE_LOCAL_userInfo',
    }),
    refreshSavePopup() {
      this.saveNetworkPopup = {...this.saveNetworkPopupDefault}
    },
    eventSaveNetwork() {
      // const projectsList = this.getLocalUserInfo.projectsList;
      const network = this.currentNetwork;

      this.checkTrainedNetwork()
        .then((isTrained)=> {
//          if(!projectsList.length || findIndexId(projectsList, network) < 0) {
          // if(!network.networkRootFolder) {
          //   this.saveNetworkPopup.isSyncName = true;
          //   this.eventSaveNetworkAs(network.networkID, true)
          //   return
          // }

          if(isTrained) {
            this.saveNetworkPopup.isFreezeInfo = true;
            this.eventSaveNetworkAs(network.networkID)
          }
          else {
            const settings = {
              isSaveTrainedModel: false,
              projectName: network.networkName,
              projectPath: network.apiMeta.location
            };
            this.saveNetwork(settings, network.networkID)
          }
        })

      function findIndexId(list, currentNet) {
        return list.findIndex((proj) => proj.id === currentNet.networkID)
      }
    },
    eventSaveNetworkAs(netId, isSaveProjectPath) {
      this.saveNetworkPopup.show = true;
      this.askSaveFilePopup()
        .then((answer)=> {
          if(answer) {
            this.saveNetwork(answer, netId, isSaveProjectPath);
          }
        })
        .catch((err)=> console.log(err))
    },
    askSaveFilePopup() {
      this.saveNetworkPopup.show = true;
      return this.$nextTick()
        .then(()=>     this.$refs.saveNetworkPopup[0].openPopup())
        .catch((err)=> this.infoPopup('Project not saved'))
        .finally(()=>  this.refreshSavePopup())
    },
    saveNetwork(netInfo, netId, saveProjectPath) {
      const networkField = this.$refs.networkField[0].$refs.network;
      networkField.style.filter = 'blur(5px)';

      const currentNet = this.currentNetwork;
      const newProjectId = netId || generateID();
      // debugger;
      const pathSaveProject = netInfo.projectPath;

      let prepareNet = cloneNet(currentNet, newProjectId, netInfo);
      /*check Is Trained Net + do ScreenShot*/
      doScreenShot(networkField)
        .then((img)=> {
          prepareNet.toLocal.image = img;
          if(netInfo.isSaveTrainedModel) {
            /*core save*/
            prepareNet.toLocal.isTrained = true;
            return this.saveTrainedNetwork({
              'Location': [pathSaveProject],
              'frontendNetwork': prepareNet.toFile,
              'networkName': this.currentNetwork.networkName
            })
          }
          else {
            // /*app save*/
            // return projectPCSave(prepareNet.toFile)

            const payload = {
              path: prepareNet.toLocal.pathProject
            };
            return this.$store.dispatch('mod_api/API_saveJsonModel', payload);
            
          }
        })
        .then(()=> {
          /*save project to project page*/
          if(prepareNet.toFile.apiMeta.location !== prepareNet.toLocal.pathProject) {
            let newModelPath = prepareNet.toLocal.pathProject;
            const modelUdateBody = {
              modelId: prepareNet.toFile.apiMeta.model_id,
              project: prepareNet.toFile.apiMeta.project,
              name: prepareNet.toLocal.name,
              location: newModelPath,
            };
            this.$store.dispatch('mod_workspace/SET_networkLocation', newModelPath); // change new location in vuex
            this.$store.dispatch('mod_project/updateModel', modelUdateBody); // change new location in api
          }
          

          saveProjectToLocalStore(prepareNet.toLocal, this);
          if(saveProjectPath) this.set_networkRootFolder(pathSaveProject);
          this.infoPopup('The file has been successfully saved');
          this.trackerModelSave(prepareNet.toFile);
          this.setUnsavedChanges({
            networkId: netId, 
            value: false
          });
        })
        .catch((error) => {})
        .finally(()=> {
          networkField.style.filter = '';
        });

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
          //const pathIndex = projectsLocalList.findIndex((proj)=> proj.pathModel === project.pathModel);
          const idExist = idIndex >= 0;
          //const pathExist = pathIndex >= 0;
          //console.log(idIndex, pathIndex);
          //if(idExist && pathExist && idIndex === pathIndex) projectsLocalList[idIndex] = project; //to him self
          if(idExist) projectsLocalList[idIndex] = project; //to him self
          else projectsLocalList.push(project) //create new
        }
        else {
          projectsLocalList.push(project)
        }
        ctx.saveLocalUserInfo({key: 'projectsList', data: projectsLocalList });
      }

      function cloneNet(net, idProject, newNetInfo) {
        //clone network
        let toFile = {};
        for (var key in net) {
          if(key === 'networkElementList') toFile[key] = JSON.parse(cloneEl(net[key]));
          else toFile[key] = net[key];
        }

        // console.log('toFile.networkMeta', toFile.networkMeta);

        if(idProject) toFile.networkID = idProject;
        toFile.networkName = newNetInfo.projectName;
        toFile.networkMeta = {};
        toFile.networkRootFolder = newNetInfo.projectPath;
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
          name: newNetInfo.projectName,
          id: idProject,
          pathProject: newNetInfo.projectPath,
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
    },
  }

};

export default workspaceSaveNet
