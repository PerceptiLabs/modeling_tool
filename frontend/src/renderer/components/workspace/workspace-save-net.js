import html2canvas  from 'html2canvas';
import { generateID }  from "@/core/helpers.js";

import { mapGetters, mapMutations, mapActions } from "vuex";
import cloneDeep from 'lodash.clonedeep';
import { doesDirExist as rygg_doesDirExist } from '@/core/apiRygg';
import { saveModelJson as rygg_saveModelJson } from '@/core/apiRygg';
import { disassembleModel } from "@/core/helpers/model-helper";

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
      updateUnsavedChanges: 'mod_workspace-changes/updateUnsavedChanges',
    }),
    refreshSavePopup() {
      this.saveNetworkPopup = {...this.saveNetworkPopupDefault}
    },
    eventSaveNetwork() {
      const network = this.currentNetwork;

      const settings = {
        isSaveTrainedModel: false,
        networkName: network.networkName,
        networkPath: network.apiMeta.location
      };
      this.doSaveNetwork(settings, network.networkID);
    },
    eventSaveNetworkAs(netId, isSaveProjectPath) {
      this.$store.dispatch('globalView/SET_saveNetworkPopup', true);
      this.askSaveFilePopup()
        .then(async (answer)=> {
          if(answer) {
            const isFolderAlreadyExist = await rygg_doesDirExist(answer.networkPath);
            
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

          if(prepareNet.toFile.apiMeta.location !== prepareNet.toLocal.pathProject || 
            prepareNet.toFile.apiMeta.name !== prepareNet.toLocal.name) {
            this.$store.dispatch('mod_workspace/SET_networkLocation', prepareNet.toLocal.pathProject); // change new location in vuex
            this.$store.dispatch('mod_workspace/SET_networkName', prepareNet.toLocal.name); // change new location in vuex
          }
          const healthNetworkJson = disassembleModel(this.currentNetwork);      
          return rygg_saveModelJson(healthNetworkJson)
            .catch((e) => {
              console.log(e)
              Promise.reject(e)
            });
        })
        .then(()=> {
          // Why is the model saved twice?
          const healthNetworkJson = disassembleModel(this.currentNetwork);                
          rygg_saveModelJson(healthNetworkJson)
            .catch((e) => {
              console.log(e)
            });

          // Update the model in the webstorage too.
          //try to update date first
          const savedTime = new Date();

          currentNet.apiMeta.updated = savedTime;
          // update model updated in rygg
          this.$store.dispatch('mod_project/patchModel', { model_id: currentNet.apiMeta.model_id, updated: savedTime});

          /*save project to project page*/
          if(saveProjectPath) this.set_networkRootFolder(pathSaveProject);
          this.trackerModelSave(prepareNet.toFile);
          this.updateUnsavedChanges({
            networkId: netId, 
            value: false
          });
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
