import html2canvas  from 'html2canvas';
import canvg        from 'canvg'
import { generateID }  from "@/core/helpers.js";

import { mapGetters, mapMutations, mapActions } from "vuex";
import cloneDeep from 'lodash.clonedeep';
import { doesDirExist as fileserver_doesDirExist } from '@/core/apiFileserver';
import { saveModelJson as fileserver_saveModelJson } from '@/core/apiFileserver';

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
    ...mapActions({
      infoPopup:            'globalView/GP_infoPopup',
      set_networkRootFolder:'mod_workspace/SET_networkRootFolder',
      checkTrainedNetwork:  'mod_api/API_checkTrainedNetwork',
      saveTrainedNetwork:   'mod_api/API_saveTrainedNetwork',
      trackerModelSave:     'mod_tracker/EVENT_modelSave',
      saveLocalUserInfo:    'mod_user/UPDATE_LOCAL_userInfo',
      updateUnsavedChanges: 'mod_workspace-changes/updateUnsavedChanges',
    }),
    refreshSavePopup() {
      this.saveNetworkPopup = {...this.saveNetworkPopupDefault}
    },
    eventSaveNetwork() {
      // const projectsList = this.getLocalUserInfo.projectsList;
      const network = this.currentNetwork;

      const settings = {
        isSaveTrainedModel: false,
        networkName: network.networkName,
        networkPath: network.apiMeta.location
      };
      this.doSaveNetwork(settings, network.networkID);

//       this.checkTrainedNetwork()
//         .then((isTrained)=> {
// //          if(!projectsList.length || findIndexId(projectsList, network) < 0) {
//           // if(!network.networkRootFolder) {
//           //   this.saveNetworkPopup.isSyncName = true;
//           //   this.eventSaveNetworkAs(network.networkID, true)
//           //   return
//           // }

//           if(isTrained) {
//             this.saveNetworkPopup.isFreezeInfo = true;
//             this.eventSaveNetworkAs(network.networkID)
//           }
//           else {
//             const settings = {
//               isSaveTrainedModel: false,
//               networkName: network.networkName,
//               networkPath: network.apiMeta.location
//             };
//             this.doSaveNetwork(settings, network.networkID)
//           }
//         })

//       function findIndexId(list, currentNet) {
//         return list.findIndex((proj) => proj.id === currentNet.networkID)
//       }
    },
    eventSaveNetworkAs(netId, isSaveProjectPath) {
      this.$store.dispatch('globalView/SET_saveNetworkPopup', true);
      this.askSaveFilePopup()
        .then(async (answer)=> {
          if(answer) {
            const isFolderAlreadyExist = await fileserver_doesDirExist(answer.networkPath);
            
            if(isFolderAlreadyExist) {
              this.$store.dispatch('globalView/GP_confirmPopup', {
                text: `That folder already exists. Are you sure <br/> you want to overwrite it?`,
                ok: () => {
                  this.doSaveNetwork(answer, netId, isSaveProjectPath);
                }
              })
            } else {
              this.doSaveNetwork(answer, netId, isSaveProjectPath);
            }
          }
        })
        .catch((err)=> console.log(err))
    },
    askSaveFilePopup() {
      this.$store.dispatch('globalView/SET_saveNetworkPopup', true);
      return this.$nextTick()
        .then(()=>     this.$refs.saveNetworkPopup.openPopup())
        .catch((err)=> this.infoPopup('Model not saved'))
        .finally(()=> {
          this.refreshSavePopup();
          this.$store.dispatch('globalView/SET_saveNetworkPopup', false);
        });
    },
    doSaveNetwork(netInfo, netId, saveProjectPath) {
      const networkField = this.$refs.networkField[0].$refs.network;
      networkField.style.filter = 'blur(5px)';

      const currentNet = this.currentNetwork;
      const newProjectId = netId || generateID();

      const pathSaveProject = netInfo.networkPath;

      let prepareNet = cloneNet(cloneDeep(currentNet), newProjectId, netInfo);
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
            }).catch(() => Promise.reject())
          }
          else {
            /*app save*/
            const payload = {
              path: prepareNet.toLocal.pathProject
            };
            const networkJson = cloneDeep(this.currentNetwork)
            const healthNetworkElementList = {};
            Object.keys(networkJson.networkElementList).map(key => {
              const el = networkJson.networkElementList[key];
              healthNetworkElementList[key] = {
                ...el,
                chartData: {}
              }
            })
            const healthNetworkJson = {
              ...networkJson,
              networkElementList: healthNetworkElementList
            }
            return fileserver_saveModelJson(healthNetworkJson)
              .catch((e) => {
                console.log(e)
                Promise.reject(e)
              });

          }
        })
        .then(()=> {
          // Update the model in the webstorage too.
          //try to update date first
          const savedTime = new Date();

          currentNet.apiMeta.updated = savedTime;
          this.$store.dispatch('mod_webstorage/saveNetwork', currentNet, {root: true});
          // update model updated in rygg
          this.$store.dispatch('mod_project/patchModel', { model_id: currentNet.apiMeta.model_id, updated: savedTime});

          /*save project to project page*/
          if(prepareNet.toFile.apiMeta.location !== prepareNet.toLocal.pathProject || 
            prepareNet.toFile.apiMeta.name !== prepareNet.toLocal.name) {
            this.$store.dispatch('mod_workspace/SET_networkLocation', prepareNet.toLocal.pathProject); // change new location in vuex
            this.$store.dispatch('mod_workspace/SET_networkName', prepareNet.toLocal.name); // change new location in vuex
          }
          if(saveProjectPath) this.set_networkRootFolder(pathSaveProject);
          this.trackerModelSave(prepareNet.toFile);
          this.updateUnsavedChanges({
            networkId: netId, 
            value: false
          });
          saveProjectToLocalStore(prepareNet.toLocal, this);
        })
        .catch((error) => {
          console.log(error)
          this.$store.dispatch('globalView/GP_errorPopup',"Couldn't save model")
        })
        .finally(()=> {
          networkField.style.filter = '';
        });

      function doScreenShot(networkFieldEl) {
        return new Promise((resolve, reject)=> {
          try {
            const svg = document.querySelector('.svg-arrow');
            const arrowsCanvas = document.createElement('canvas');
            arrowsCanvas.style.position = 'absolute';
            arrowsCanvas.style.zIndex = '0';
            networkFieldEl.appendChild(arrowsCanvas);
//            canvg(arrowsCanvas, svg.outerHTML, {});
            svg.style.display = 'none';
  
            const options = {
              scale: 1,
              backgroundColor: 'null',
            };
            return html2canvas(networkFieldEl, options)
              .then((canvas)=> {
                resolve(canvas.toDataURL());
              })
              .catch(error => { resolve() })
              .finally(()=> {
                svg.style.display = '';
                arrowsCanvas.remove();
              })
          } catch(e) {
          }
          

        })
      }

      function saveProjectToLocalStore(project, ctx) {
        let projectsLocalList = cloneDeep(ctx.getLocalUserInfo.projectsList);

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

        /********************************************************************
           
          The following logic is added due to:
            story 903 (decoupling of workspace - stats/test view)
          
          Before deciding between:
            - Alt 1 (Save everything as the same “model”) and
            - Alt 2 (Save as model and experiments)
          we'll export the snapshot (stored in prepareNet.toFile.networkSnapshots[0]).
          
        *********************************************************************/
        
        if (newNetInfo.isSaveTrainedModel &&
            net.networkSnapshots &&
            net.networkSnapshots.length > 0) {

          net.networkElementList = net.networkSnapshots[0];
          delete net.consoleLogs;
        }
        delete net.networkSnapshots;

        //clone network
        let toFile = {};
        for (var key in net) {
          if(key === 'networkElementList') toFile[key] = JSON.parse(cloneEl(net[key]));
          else toFile[key] = net[key];
        }

        if(idProject) toFile.networkID = idProject;
        toFile.networkName = newNetInfo.networkName;
        toFile.networkMeta = {};
        toFile.networkRootFolder = newNetInfo.networkPath;
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
          name: newNetInfo.networkName,
          id: idProject,
          pathProject: newNetInfo.networkPath,
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
