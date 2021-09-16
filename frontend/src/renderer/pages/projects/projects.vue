<template lang="pug">
  div
    import-model(v-if="showImportNetworkfromGitHubOrLocalPopup")
    .modelContext(v-if="isContextOpened" :style="modelContextStyles")
      button(@click="handleContextOpenModel()") Open
      button(@click="handleContextRenameModel()") Rename
      button(@click="handleContextRemoveModel()") Delete
    div(v-show="!showNewModelPopup").project-wrapper
      //- h1.project-name Project_Name
      div.header-controls
        div.left-side
          base-button(
            @click.native="handleLoadDataClick"
          )
            svg(width="18" height="19" viewBox="0 0 18 19" fill="none" xmlns="http://www.w3.org/2000/svg")
              path(d="M0.5625 11.6367C0.711684 11.6367 0.854758 11.696 0.960248 11.8015C1.06574 11.907 1.125 12.05 1.125 12.1992V15.0117C1.125 15.3101 1.24353 15.5962 1.4545 15.8072C1.66548 16.0182 1.95163 16.1367 2.25 16.1367H15.75C16.0484 16.1367 16.3345 16.0182 16.5455 15.8072C16.7565 15.5962 16.875 15.3101 16.875 15.0117V12.1992C16.875 12.05 16.9343 11.907 17.0398 11.8015C17.1452 11.696 17.2883 11.6367 17.4375 11.6367C17.5867 11.6367 17.7298 11.696 17.8352 11.8015C17.9407 11.907 18 12.05 18 12.1992V15.0117C18 15.6085 17.7629 16.1808 17.341 16.6027C16.919 17.0247 16.3467 17.2617 15.75 17.2617H2.25C1.65326 17.2617 1.08097 17.0247 0.65901 16.6027C0.237053 16.1808 0 15.6085 0 15.0117V12.1992C0 12.05 0.0592632 11.907 0.164752 11.8015C0.270242 11.696 0.413316 11.6367 0.5625 11.6367Z" fill="white")
              path(d="M8.60246 1.79026C8.65471 1.73787 8.71678 1.69631 8.78512 1.66795C8.85346 1.6396 8.92672 1.625 9.00071 1.625C9.0747 1.625 9.14796 1.6396 9.2163 1.66795C9.28464 1.69631 9.34671 1.73787 9.39896 1.79026L12.774 5.16526C12.8796 5.27088 12.9389 5.41413 12.9389 5.56351C12.9389 5.71288 12.8796 5.85613 12.774 5.96176C12.6683 6.06738 12.5251 6.12672 12.3757 6.12672C12.2263 6.12672 12.0831 6.06738 11.9775 5.96176L9.56321 3.54638V13.4385C9.56321 13.5877 9.50395 13.7308 9.39846 13.8363C9.29297 13.9417 9.1499 14.001 9.00071 14.001C8.85153 14.001 8.70845 13.9417 8.60296 13.8363C8.49747 13.7308 8.43821 13.5877 8.43821 13.4385V3.54638L6.02396 5.96176C5.97166 6.01405 5.90957 6.05554 5.84124 6.08384C5.77291 6.11215 5.69967 6.12672 5.62571 6.12672C5.55175 6.12672 5.47851 6.11215 5.41018 6.08384C5.34185 6.05554 5.27976 6.01405 5.22746 5.96176C5.17516 5.90946 5.13368 5.84737 5.10537 5.77904C5.07707 5.71071 5.0625 5.63747 5.0625 5.56351C5.0625 5.48954 5.07707 5.41631 5.10537 5.34797C5.13368 5.27964 5.17516 5.21755 5.22746 5.16526L8.60246 1.79026Z" fill="white")
            | Upload data
      //-- MODELS RENDERING --//
      div.models-list
        //-- MODELS HEADER --//
        div.models-list-row.model-list-header
          div.column-1 
            span.btn-round-icon.check-model-button(@click="toggleSelectedItems()" v-tooltip:bottom="'Select All'")
              img(v-if="isAllItemsSelected()" src="../../../../static/img/project-page/checked.svg")
            | All datasets
          div.column-2
          div.column-3
          div.column-4 Status
          div.column-5 Duration
          div.column-6 Modified
          div.column-7
            div.d-flex.flex-row-reverse.align-items-center
              .button-container(v-tooltip:bottom="'Delete'")
                span.img-button.pt-4(:class="{ 'disabledIconButton': !isAtLeastOneItemSelected() }" @click="removeItems()")
                  img(src="../../../../static/img/project-page/remove.svg")
              base-button(
                @click="openItems"
                type="transparent"
                :disabled="!isAtLeastOneItemSelected()"
              ) Open
        //-- MODELS BODY --//
        perfect-scrollbar.model-list-scrollbar
          div(v-for="dataset in allDatasets" :key="dataset.dataset_id")
            //-- DATASET ROW --//
            div.models-list-row.model-list-item.model-list-item-dataset
              div.column-1
                span(
                  @click="toggleDataSetAllModels(dataset.dataset_id)"
                ).btn-round-icon.check-model-button
                  img(v-if="areAllDataSetItemsChecked(dataset.dataset_id)"  src="../../../../static/img/project-page/checked.svg")
  
                .editable-field.model-name-wrapper.text-rtl
                  span.model-name(
                  )
                  img.dataset-chevron(v-if="isDatasetOpened(dataset.dataset_id)" @click="toggleDataSetModels(dataset.dataset_id)" src="../../../../static/img/chevron-down.svg" alt="chevron-down")
                  img.dataset-chevron(v-else @click="toggleDataSetModels(dataset.dataset_id)" src="../../../../static/img/chevron-right.svg" alt="chevron-right")
                  bdi {{dataset.name}}
              div.column-2
              div.column-4
              div.column-7
              div.column-3
              div.column-6
              div.column-7
                div.d-flex.flex-row-reverse(
                  @click="createModelWithCurrentDataSetPath(dataset.dataset_id)"
                )
                  | + New Model
            //-- MODELS BELONG TO DATASET --//
            template(v-if="isDatasetOpened(dataset.dataset_id)")  
              div.models-list-row.model-list-item.model-list-item-child(
                v-for="(model, index) in getModelsByDataSetId(dataset.dataset_id)"
                @click="toggleItemSelection(model.networkID)"
                @contextmenu.stop.prevent="openContext($event, index)"
                :key="'Valid_' + model.networkID"
                :class="{'is-selected': isItemSelected(model.networkID)}")
                div.column-1
                  span.btn-round-icon.check-model-button
                    img(v-if="isItemSelected(model.networkID)" src="../../../../static/img/project-page/checked.svg")
    
                  .editable-field.model-name-wrapper
                    span.model-name(
                      title="model.networkName}"
                      v-if="!isRenamingItem(index)" 
                      v-tooltip:bottom="'Click to open Model'" 
                      @click.stop="goToNetworkView(model.networkID)"
                    ) {{model.networkName}}
                    input.rename-control(
                      v-else 
                      v-model="renameValue" 
                      @blur="renameModel"
                      @keyup.enter="renameModel"
                      ref="titleInput"
                    )
    
                  div.model-unsaved_changes_indicator(v-if="hasUnsavedChanges(model.networkID)")
                    span Unsaved
                    .indicator-circle
    
                div.column-2
                  |
                div.column-3
                  |
                div.column-4
                  model-status(
                    :statusData="model.networkMeta.coreStatus"
                    :coreError="model.networkMeta.coreError"
                  )
                div.column-5
                  span(@click.stop="") {{ model && model.networkMeta && model.networkMeta.coreStatus && model.networkMeta.coreStatus.Training_Duration ? model.networkMeta.coreStatus.Training_Duration.toFixed(2) + 's' : '-' }}
                div.column-6
                  | {{ (model && model.apiMeta && model.apiMeta.updated) ? formatDate(model.apiMeta.updated)  : ''}}
                div.column-7(@click.stop="")
          //-- DELETED MODELS --//
          div.models-list-row.model-list-item(
            v-for="(model, index) in unparsedModels"
            :key="'Unparsed_' + model.id"
            :class="{'is-selected': isItemSelected(model.networkID)}"
            @click="onClickDeletedModel(model, index)"
            )
            div.column-1
              span.model-name {{model.name}}

            div.column-2 Deleted
            
            div.column-4
              span(@click.stop="") -
            div.column-7 Deleted
            div.column-3
              span(@click.stop="") -
            div.column-6(@click.stop="")
              collaborator-avatar(
                  :list="[{id: 1, name: user && user.firstName || '', img: null,}]"
                )
              | {{ (model && model && model.updated) ? formatDate(model.updated) : ''}}
    select-model-modal(
      v-if="showNewModelPopup"
      @close="onCloseSelectModelModal"
      @onChose="onTemplateChoseSelectModelModal"
      )
    workspace-load-network(
      v-if="showLoadSettingPopup"
    )
</template>

<script>
  import SortByButton from '@/pages/projects/components/sort-by-button.vue';
  import CollaboratorAvatar from '@/pages/projects/components/collaborator-avatar.vue'
  import SelectModelModal from '@/pages/projects/components/select-model-modal.vue';
  import ModelStatus from '@/components/different/model-status.vue';
  import WorkspaceLoadNetwork   from "@/components/global-popups/workspace-load-network.vue";
  import ImportModel    from "@/components/global-popups/import-model-popup.vue";

  import { mapActions, mapState, mapGetters } from 'vuex';
  import { arrayIncludeOrOmit } from "@/core/helpers";
  import {
    getModelJson as rygg_getModelJson,
  } from '@/core/apiRygg';
  import { LOCAL_STORAGE_HIDE_DELETE_MODAL } from '@/core/constants.js'

  export default {
    name: "pageProjects",
    components: {
      SortByButton,
      CollaboratorAvatar,
      SelectModelModal,
      ModelStatus,
      WorkspaceLoadNetwork,
      ImportModel,
    },
    data: function () {
      return {
        isNewUser: false,
        selectedListIds: [],
        isImportModelsOpen: false,
        contextModelIndex: null,
        isContextOpened: false,
        modelContextStyles: {},
        // for renaming models
        renameIndex: null,
        renameValue: null,
        showUser: !process.env.NO_KC,
        dataSetIsOpenedStateArray: [],
      }
    },
    computed: {
      ...mapGetters({
        user:                 'mod_user/GET_userProfile',
        currentProject:       'mod_project/GET_project',
        getCurrentStepCode:   'mod_tutorials/getCurrentStepCode',
        allDatasets: 'mod_datasets/GET_datasets',
      }),
      ...mapState({
        currentProjectId:     state => state.mod_project.currentProject,
        showFilePickerPopup:  state => state.globalView.globalPopup.showFilePickerPopup,
        showNewModelPopup:    state => state.globalView.globalPopup.showNewModelPopup,
        hotKeyPressDelete:    state => state.mod_events.globalPressKey.del,
        showLoadSettingPopup: state => state.globalView.globalPopup.showLoadSettingPopup,
        workspaceContent:     state => state.mod_workspace.workspaceContent,
        unparsedModels:       state => state.mod_workspace.unparsedModels,
        showImportNetworkfromGitHubOrLocalPopup:     state => state.globalView.globalPopup.showImportNetworkfromGitHubOrLocalPopup,
      }),
      statusLocalCore() {
        return this.$store.state.mod_api.statusLocalCore;
      },
      isCoreOffline() {
        return this.$store.state.mod_api.statusLocalCore !== 'online';
      },
    },
    watch: {
      hotKeyPressDelete() {
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'hotKeyPressDelete'");
          return;
        }

        if (!this.projects) { return; }

        const indexCheckedProj = this.projects.findIndex((el)=> el.isChecked === true);
        if(indexCheckedProj < 0) return;

        const selectedProject = this.projects[indexCheckedProj];
        const pathDelete = selectedProject.pathProject;

        const newProjectsList = deepCopy(this.localUserInfo.projectsList);
        newProjectsList.splice(indexCheckedProj, 1);
        this.saveLocalUserInfo({key: 'projectsList', data: newProjectsList });
      },
      getCurrentStepCode: {
        handler(newVal, oldVal) {
          if (!this.isTutorialMode) { return; }
          if (newVal !== 'tutorial-model-hub-new-button') { return; }
          
          this.activateCurrentStep();
        },
        immediate: true
      },
      'allDatasets.length': {
        handler(newVal, oldVal) {
          if((newVal !== 0) && (newVal !== oldVal)) {
            this.expandDatasetsModels();
          }
        }
      }
    },
    methods: {
      ...mapActions({
        popupConfirm:        'globalView/GP_confirmPopup',
        popupDeleteConfirm:  'globalView/GP_deleteConfirmPopup',
        popupNewModel:       'globalView/SET_newModelPopup',
        showInfoPopup:       'globalView/GP_infoPopup',
        set_currentNetwork:  'mod_workspace/SET_currentNetwork',
        set_currentModelIndex: 'mod_workspace/SET_currentModelIndex',
        createProjectModel:  'mod_project/createProjectModel',
        setActivePageAction: 'modal_pages/setActivePageAction',
        delete_network :     'mod_workspace/DELETE_network',
        delete_networkById:  'mod_workspace/DELETE_networkById',        
        UPDATE_MODE_ACTION : 'mod_workspace/UPDATE_MODE_ACTION',
        closeStatsTestViews:  'mod_workspace/SET_statisticsAndTestToClosed',
        setCurrentView:       'mod_tutorials/setCurrentView',
        setNextStep:          'mod_tutorials/setNextStep',
        SET_openStatistics:   'mod_workspace/SET_openStatistics',
        SET_openTest:         'mod_workspace/SET_openTest',
        setNetworkNameAction: 'mod_workspace/SET_networkName',
        updateWorkspaces:     'mod_webstorage/updateWorkspaces',
        deleteAllIds:         'mod_webstorage/deleteAllIds',        
      }),
      goToNetworkView(networkID) {
        // maybe should receive a id and search index by it
        this.$store.commit('mod_workspace/update_network_meta', {key: 'hideModel', networkID: networkID, value: false});

        const index = this.workspaceContent.findIndex(wc => wc.networkID == networkID);
        this.set_currentNetwork(index > 0 ? index : 0);

        this.closeStatsTestViews({ networkId: networkID });

        this.set_currentModelIndex(index > 0 ? index : 0);
        this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);
        
        if(index !== -1) {
          this.$store.dispatch("mod_workspace/setViewType", 'model');
          // this.SET_openStatistics(false);
          // this.SET_openTest(false);
          this.$router.push({name: 'app'});

          this.$nextTick(() => {
            this.setCurrentView('tutorial-workspace-view');
          });
        }
      },
      loadFolderPath() {
        this.$store.commit("globalView/set_filePickerPopup", true);
      },
      openTemplate(path) {
        rygg_getModelJson(path)
      },
      isItemSelected(itemId) {
        itemId = parseInt(itemId);
        return this.selectedListIds.indexOf(itemId) !== -1;
      },
      toggleItemSelection(modelId) {
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'toggleItemSelection'");
          return;
        }

        modelId = parseInt(modelId);
        let itmPosition = this.selectedListIds.indexOf(modelId);
        if (itmPosition === -1) {
          this.selectedListIds = [...this.selectedListIds, modelId];
        } else {
          this.selectedListIds = [...this.selectedListIds.slice(0, itmPosition), ...this.selectedListIds.slice(itmPosition + 1)]
        }
      },
      isAtLeastOneItemSelected() {
        return this.selectedListIds.length >= 1;
      },
      isOneItemSelected() {
        return this.selectedListIds.length === 1;
      },
      openItems() {
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'openItems'");
          return;
        }
        if(!this.isAtLeastOneItemSelected()) {
          return;
        }
        this.selectedListIds.forEach(id => {
          this.$store.commit('mod_workspace/update_network_meta', {key: 'hideModel', networkID: id, value: false});
          const index = this.workspaceContent.findIndex(wc => wc.networkID == id);
          this.set_currentNetwork(index > 0 ? index : 0);
          this.set_currentModelIndex(index > 0 ? index : 0);
        });

        this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);
        this.$router.push({name: 'app'});
      },
      async removeItems() {
        if(!this.selectedListIds.length) return; // prevent removing modal when no item are selected
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'removeItems'");
          return;
        }

        if(localStorage.getItem(LOCAL_STORAGE_HIDE_DELETE_MODAL)) {
          for (const networkId of this.selectedListIds) {
            this.$store.dispatch('mod_tracker/EVENT_modelDeletion');
            await this.delete_networkById(networkId);
          }
          this.selectedListIds = [];
          this.updateWorkspaces();
        } else {
          this.popupDeleteConfirm({
            ok: async () => {
              const promises = [];

              for (const networkId of this.selectedListIds) {
                // promises.push(this.delete_networkById(networkId));
                this.$store.dispatch('mod_tracker/EVENT_modelDeletion');

                await this.delete_networkById(networkId);
              }
              
              this.selectedListIds = [];

              this.updateWorkspaces();
            }
          });
        }
      },
      isAllItemsSelected() {
        return this.selectedListIds.length === this.workspaceContent.length && this.workspaceContent.length !== 0;
      },
      toggleSelectedItems() {
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'toggleSelectedItems'");
          return;
        }

        const soemItemsAreSelected = this.selectedListIds.length !== this.workspaceContent.length;
        if(this.isAllItemsSelected()) {
          this.selectedListIds = [];
        } else {
          let newWorkspaceContent = [...this.workspaceContent];
          this.selectedListIds = newWorkspaceContent.map(networkItem => parseInt(networkItem.networkID, 10));
        }
      },
      handleAddNetworkModal() {
        this.setNextStep({
          currentStep:'tutorial-model-hub-new-button',
          activateNextStep: false // or extra notification will appear
        });

        // open modal
        this.popupNewModel(true);
      },
      onCloseSelectModelModal() {
        this.popupNewModel(false);
      },
      onTemplateChoseSelectModelModal() {

      },
      confirmFilePickerSelection(selectedItems) {
        this.clearPath();
      },
      clearPath(x){
        this.isImportModelsOpen = false;
      },
      openLoadModelPopup() {
        // this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.onLoadNetworkConfirmed});
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'openLoadModelPopup'");
          return;
        }
        this.$store.dispatch('globalView/SET_showImportNetworkfromGitHubOrLocalPopup', true);
      },
      onLoadNetworkConfirmed(path) {
        if (!path || path.length === 0) { return; }
        this.$store.dispatch('globalView/SET_filePickerPopup', false);

        this.$store.dispatch('mod_events/EVENT_loadNetwork', path[0]);
      },
      confirmCallback(el) {
        this.openTemplate(el[0]);
        this.$store.commit("globalView/HIDE_allGlobalPopups");
      },
      handleStatisticClick(index, e, model) {
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'handleStatisticClick'");
          return;
        }

        const { networkMeta: { openStatistics } } = model;


        if (typeof openStatistics === 'boolean') {
          this.$store.dispatch("mod_workspace/setViewType", 'statistic');

          this.$router.push({name: 'app'}) 
            .then(() => {
              this.set_currentNetwork(index);
              this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);
              
              this.$store.dispatch("mod_workspace/SET_currentStatsIndex", index);
              this.$store.commit('mod_workspace/update_network_meta', {key: 'hideStatistics', networkID: model.networkID, value: false});
              this.SET_openStatistics(true);
              this.SET_openTest(false);
            });
        } else {
          this.showInfoPopup("The model does not have any statistics. Run this model to generate statistics.");
        }
      },
      openContext(e, modelIndex) {
        const { pageX, pageY } = e;
        this.modelContextStyles = {
          top: pageY + 'px',
          left: pageX + 'px',
        };
        this.isContextOpened = true;
        this.contextModelIndex = modelIndex;
        document.addEventListener('click', this.closeContext);
      },
      closeContext() {
        document.removeEventListener('click', this.closeContext);
        this.contextModelIndex = null;
        this.isContextOpened = false
      },
      handleContextOpenModel() {
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'handleContetOpenModel'");
          return;
        }

        this.goToNetworkView(this.workspaceContent[this.contextModelIndex].networkID);
        this.closeContext();
      },
      async handleContextRemoveModel() {
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'handleContextRemoveModel'");
          return;
        }

        const modelIndex = this.contextModelIndex;

        if(localStorage.getItem(LOCAL_STORAGE_HIDE_DELETE_MODAL)) {
          this.$store.dispatch('mod_tracker/EVENT_modelDeletion');
          await this.delete_network(modelIndex);
        } else {
          this.popupDeleteConfirm({
            ok: async () => {
              this.$store.dispatch('mod_tracker/EVENT_modelDeletion');
              await this.delete_network(modelIndex);
            }
          });
        }
        
        this.closeContext();
      },
      onClickDeletedModel(model, index) {
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'onClickDeletedModel'");
          return;
        }

        this.popupConfirm({
            text: `Are you sure you want to remove ${model.name} from Model Hub since it is no longer connected to the Project?`,
            ok: () => {
              this.$store.dispatch('mod_tracker/EVENT_modelDeletion', 'Unparsed');
              this.$store.dispatch('mod_project/deleteModel', model)
                .then((serverResponse) => {
                  this.unparsedModels.splice(index, 1);
              })
            }
          })
      },
      handleContextRenameModel() {
        if(this.isCoreOffline) {
          this.showInfoPopup("Kernel is offline when calling 'handleContextRenameModel'");
          return;
        }

        this.renameIndex = this.contextModelIndex;
        this.renameValue = this.workspaceContent[this.renameIndex].networkName;
      },
      isRenamingItem(index) {
        return this.renameIndex === index;
      },
      renameModel() {
        // this.setNetworkNameAction(text);
        if (this.renameIndex !== null) {
          this.set_currentNetwork(this.renameIndex);
          this.setNetworkNameAction(this.renameValue);
          this.updateWorkspaces();
        }
        this.renameIndex = null;
        this.renameValue = null;
      },
      formatDate (dateString) {
        if(!dateString) { return ''; }
        let date = new Date(dateString);
        return `${date.toLocaleDateString(navigator.language)}`;
      },
      hasUnsavedChanges(networkId) {
        return this.$store.getters['mod_workspace-changes/get_hasUnsavedChanges'](networkId);
      },
      openExportToGithubModal() {
        if(!this.isOneItemSelected()) {
          return;
        }
        const modelId = this.selectedListIds[0];
        this.goToNetworkView(modelId);
        this.$store.dispatch('globalView/SET_exportNetworkToGithubPopup', true);
      },
      
      handleLoadDataClick() {
        this.handleAddNetworkModal()
      },
      getModelsByDataSetId(dataSetId) {
        let matchedModels = [];
        const models = this.workspaceContent;
        models.forEach(model => {
          if(model.apiMeta.datasets && model.apiMeta.datasets.includes(dataSetId)) {
            matchedModels.push(model);
          }
        })
        return matchedModels;
      },
      isDatasetOpened(dataSetId) {
        const isOpened = this.dataSetIsOpenedStateArray.includes(dataSetId);
        return isOpened
      },
      toggleDataSetModels(dataSetId) {
        this.$nextTick(() => {
          this.dataSetIsOpenedStateArray = arrayIncludeOrOmit(this.dataSetIsOpenedStateArray, dataSetId);
        });
      },
      getDataSetModelsIds(dataSetId) {
        return this.getModelsByDataSetId(dataSetId).map(d => d.networkID);
      },
      areAllDataSetItemsChecked(dataSetId) {
        const dataSetIds = this.getDataSetModelsIds(dataSetId);
        return dataSetIds.length !== 0 && dataSetIds.every( ai => this.selectedListIds.includes(ai));
      },
      selectModelById(modelId) {
        if(this.selectedListIds.indexOf(modelId) === -1) {
          this.selectedListIds.push(modelId);
        }
      },
      unSelectModelById(modelId) {
        const idIndex = this.selectedListIds.indexOf(modelId);
        if(idIndex === -1) {
          return
        }
        this.selectedListIds = [...this.selectedListIds.slice(0, idIndex), ...this.selectedListIds.slice(idIndex + 1)]
      },
      createModelWithCurrentDataSetPath(datasetId) {
        this.popupNewModel({datasetId});
      },
      toggleDataSetAllModels(dataSet) {
        const dataSetModelsIds = this.getDataSetModelsIds(dataSet);
        if (this.areAllDataSetItemsChecked(dataSet)) {
          dataSetModelsIds.map(modelId => this.unSelectModelById(modelId));
        } else {
          dataSetModelsIds.map(modelId => this.selectModelById(modelId));
        }
      },
      expandDatasetsModels() {
        const temp = [];
        this.allDatasets.forEach(dataset => {
          temp.push(dataset.dataset_id);
        })
        this.dataSetIsOpenedStateArray = temp;
      },
    },
    created() {
      // Adding this because of reloads on this page 
      // When the stats and test views are their own routes,
      // a better alternative would be to put a lot of the
      // following in the router.
      this.setCurrentView('tutorial-model-hub-view');
      this.expandDatasetsModels();
    }
  }
</script>

<style lang="scss" scoped>
  .project-wrapper {
    height: 100%;
    background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
    border-left: 1px solid rgba(97, 133, 238, 0.4);
    box-sizing: border-box;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
    padding: 30px 30px 50px;
  }
  .header-controls {
    //padding: 7px 16px 7px 40px;
    //border-bottom: 1px solid #464D5F;
    margin-bottom: 30px;
    display: flex;
    .left-side {
      display: flex;

      padding-top: 0.5rem;
      padding-bottom: 0.5rem;

      .import-button-container {
        display: flex;
        justify-content: center;

        margin-right: 2rem;
        cursor: pointer;
      }
    }
  }
  .search-input {
    position: relative;
    width: 333px;
    img {
      cursor: pointer;
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      left: 10px;
    }
    input {
      padding-left: 44px;
      background-color: transparent;
      border: 1px solid #4D556A;
      border-radius: 2px;
      height: 29px;
    }
  }
  .text-button {
    cursor: pointer;
    font-weight: bold;
    background: transparent;
    border-radius: 5px;
    padding: 3px 9px;
    margin: 0 10px;
    font-size: 16px;
    color: #E1E1E1;
    line-height: 23px;
    &.is-disable {
      color: #818181;
      cursor: default;
      pointer-events: none;
    }
    &:hover {
      background: #383F50;
    }
  }
  .img-button {
    cursor: pointer;
    margin: 0 10px 0 10px;
    &.disabledIconButton {
      opacity: 0.4;
      cursor: default;
    }
  }
  .btn-round-icon {
    cursor: pointer;
    // margin-right: 35px;
    width: 19px;
    height: 19px;
    border: 1px solid #fff;
    border-radius: 2px;
    display: flex;
    justify-content: center;
    align-self: center;    
    &.high-lighted {
      position: relative;
      box-shadow: 0 0 10px #FFFFFF;
    }
  }
  .btn-rounded-new {
    border-radius: 2px;
    .btn-rounded-new-image {
      width: 9px;
    }
  }
  .pl-40 {
    padding-left: 40px;
  }
  .models-list {
    background: #23252A;
    border-radius: 4px;
    height: calc(100% - 80px);
    padding: 20px;
    overflow-y: hidden;
  }
  .models-list-row {
    .column-1 {
      position: relative;
      margin-right: auto;
      padding-left: 58px;
      max-width: 300px;
      min-width: 300px;
      width: 300px;
    }
    .column-2 {
      min-width: 210px; 
      cursor: pointer;
    }
    .column-3 {
      min-width: 210px;
    }
    .column-4 {
      min-width: 170px;
    }
    .column-5 {
      min-width: 170px;
    }
    .column-6 {
      min-width: 170px;
    }
    .column-7 {
      min-width: 210px;
      cursor: pointer;

      img {
        margin-left: 10px;
        margin-bottom: 3px
      }
    }
  }
  .model-list-header {
    display: flex;
    height: 43px;
    font-size: 16px;
    font-weight: 500;
    border-bottom: 1px solid #4D556A;
    align-items: center;
    padding-bottom: 10px;
    .column-1 {
      .btn-round-icon {
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%)
      }
    }
    .column-7 {
      padding-left: 20px;
    }
  }
  .model-list-item {
    display: flex;
    font-size: 16px;
    padding: 20px;
    font-weight: 400;
    border-bottom: 1px solid #363E51;
    align-items: center;
    margin-bottom: 10px;
    border: 1px solid transparent;
    border-radius: 4px;
    &:first-of-type {
      margin-top: 10px;
    }
    &.is-selected {
      background: rgba(97, 133, 238, 0.1);
      border: 1px solid #6185EE;
      border-radius: 4px;
    }
    &:hover {
       background: rgba(97, 133, 238, 0.75);
       box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
      .is-favorite{
        path {
          fill: #E1E1E1;
        }
      }
    }
    &.model-list-item-dataset {
      //border-bottom: none;
      .column-1 {
        padding-left: 76px;
        .btn-round-icon {
          left: 0;
        }
      }
    }
    &.model-list-item-child {
      //border-bottom: none;
      .column-1 {
        padding-left: 76px;
        .btn-round-icon {
          left: 38px;
        }
      }
    }
    
    .column-1 {
      display: flex;
      justify-content: flex-start;
      width: 100%;
      .btn-round-icon {
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%)
      }
      .is-favorite {
        cursor: pointer;
        position: absolute;
        left: 80px;
        top: 50%;
        transform: translateY(-50%);
      }
      .is-not-favorite {
        cursor: pointer;
        // opacity: 0;
        position: absolute;
        left: 80px;
        top: 50%;
        transform: translateY(-50%);
        transition: 0.1s;
        // &:hover {
        //   opacity: 1;
        // }
      }
      .model-name {
        cursor: pointer;
      }
    }
    .column-6 {
      display: flex;
      .collaboratorWrapper {
        width: 30px;
      }
    }

    .model-unsaved_changes_indicator {
      margin-right: 10px;
      display: flex;
      justify-content: center;
      align-items: center;

      width: 8rem;
      height: 2rem;

      background: #3F4C70;
      border-radius: 1px;

      margin-left: 2rem;

      > span  {
        font-family: Nunito Sans;
        font-style: normal;
        font-weight: normal;
        font-size: 12px;
      }

      .indicator-circle {
        height: 0.8rem;
        width: 0.8rem;

        border-radius: 50%;
        background-color: #E1E1E1;

        margin-left: 0.5rem;
      }
    }
  }
  .fav-icon-action {
    &:hover {
      path {
        stroke: #6185EE;
        stroke-width: 2px;
        border-radius: 1px;
      }
    }
  }
  .pt-4 {
    padding-top: 4px;
  }
  .create-first-model {
    z-index: 10;
    top: 31px;
    position: absolute;
    background: #6185EE;
    border-radius: 2px;
    font-size: 16px;
    line-height: 21px;
    width: 188px;
    text-align: center;
    padding-top: 11px;
    padding-bottom: 13px;
    &:after {
      content: "";
      top: -8px;
      left: 50%;
      transform: translateX(-50%);
      position: absolute;
      border-bottom: 9px solid #6185EE;
      border-left: 6px solid transparent;
      border-right: 6px solid transparent;
    }
  }
  .file-picker-wrapper {
    position: absolute;
    z-index: 1234;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: black;
    border-radius: 9px;
    border-radius: 0.5rem;
    background-color: #4D556A;
    min-width: 29rem;
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.7);
  }
  .check-model-button {
    position: relative;
    &:before {
      content: '';
      position: absolute;
      width: 0px;
      height: 0px;
      transition: 0.1s;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      border-radius: 50%;
      border: 0 solid rgba(196, 196, 196, 0.3);
      box-sizing: content-box;
    }
    &:hover {
      &:before {
        width: 0px;
        height: 0px;
        border: 20px solid rgba(196, 196, 196, 0.3);
      }
    }
  }
  .modelContext {
    position: fixed;
    background: #1C1C1E;
    border: 1px solid #363E51;
    box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    border-radius: 2px;
    display: flex;
    flex-direction: column;
    z-index: 12;
    padding: 5px 8px;

    background: #131B30;
    border: 1px solid #363E51;
    box-sizing: border-box;
    box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    border-radius: 2px;


    button {
      font-family: 'Nunito Sans';
      padding: 5px 8px;
      background: none;
      font-size: 16px;;
      text-align: left;
    }
  }
  .isTextButtonDisabled {
    cursor: default;
    opacity: 0.4;
  }
  // rename model
  .rename-control {
  }
  .left-header-btn-text {
    display: inline-block;
    margin-left: 8px;
    font-weight: 600;
    color: #E1E1E1;
    font-size: 14px;
  }
  .header-action-button-wrapper {
    display: flex;
    align-items: center;
    cursor: pointer;
  }
  .github-button {
      display: flex;
      align-items: center;
      cursor: pointer;
      &.is-disable {
        cursor: default;
        opacity: 0.4;
        pointer-events: none;
      }
    }
  .github-button-icon {
    margin-right: 10px;
  }
  .github-button-text {
    font-family: 'Nunito Sans';
    font-weight: 600;
    font-size: 14px;
    line-height: 29px;
    color: #E1E1E1;
  }
  .model-name-wrapper {
    text-overflow: ellipsis;
    overflow: hidden;
    max-width: 25vw;
    height: 1.2em;
    white-space: nowrap;
    padding-right: 15px;
  }
  .model-list-scrollbar {
    max-height: calc(100% + 40px);
  }
  .test-link {
    color: #fff;
  }
  .mr-20 {
     margin-right: 20px;
   }
  .project-name {
    font-family: Roboto;
    font-size: 24px;
    line-height: 28px;
    letter-spacing: 0.02em;
    color: #FFFFFF;
    margin-bottom: 30px;
  }
  .dataset-chevron {
    cursor: pointer;
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    left: 38px
  }
  .text-rtl {
    direction: rtl;
  }
</style>
