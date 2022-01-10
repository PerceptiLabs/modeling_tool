<template lang="pug">
div
  import-model(v-if="showImportNetworkFromGitHubOrLocalPopup")
  .modelContext(v-if="isContextOpened", :style="modelContextStyles")
    button(@click="handleContextOpenModel()") Open
    button(@click="handleContextRenameModel()") Rename
    button(@click="handleContextRemoveModel()") Delete
    button(
      v-if="!isEnterpriseMode",
      @click="handleContextUnregisterModel(contextModelId)"
    ) Unregister
  .modelContext(v-if="isDatasetContextOpened", :style="modelContextStyles") 
    button(@click="handleContextRemoveDataset(contextDatasetId)") Delete
    button(
      v-if="!isEnterpriseMode",
      @click="handleContextUnregisterDataset(contextDatasetId)"
    ) Unregister
  .project-wrapper(v-show="!showNewModelPopup")
    .header-controls
      .left-side
        .button-container
          button.btn.btn--primary(
            @click="handleAddNetworkModal",
            :data-tutorial-target="'tutorial-model-hub-new-button'"
          )
            span.btn-round-icon
              img(src="/static/img/add-button.svg")
            span.left-header-btn-text Create Project
      .right-side
    // List
    .models-list
      .models-list-row.model-list-header.bold
        .column-1
          base-checkbox.btn-checkbox(
            :value="isAllItemsSelected()",
            @input="toggleSelectedItems"
          )
            | All datasets
        .column-3 Training Status
        .column-4 Duration
        .column-5 Test Available
        .column-6 Last Modified
        .column-7.d-flex.justify-content-between.justify-content-center
          div
          .d-flex.flex-row-reverse.align-items-center
            .button-container(v-tooltip:bottom="'Delete'")
              span.img-button(
                :class="{ disabledIconButton: !isAtLeastOneItemSelected() }",
                @click="removeItems()"
              )
                img(src="/static/img/project-page/remove-red.svg")

      perfect-scrollbar.model-list-scrollbar
        div(v-for="dataset in allDatasets", :key="dataset.dataset_id")
          //-- DATASET ROW --//
          .models-list-row.model-list-item.model-list-item-dataset(
            @contextmenu.stop.prevent="openDatasetContext($event, dataset.dataset_id)"
          )
            .column-1
              base-checkbox.btn-checkbox(
                :value="isDatasetSelected(dataset.dataset_id)",
                @input="toggleDataSet($event, dataset.dataset_id)"
              )
              svg.dataset-chevron(
                @click="toggleDataSetModels(dataset.dataset_id)",
                width="18",
                height="18",
                viewBox="0 0 18 18",
                fill="none",
                xmlns="http://www.w3.org/2000/svg"
              )
                path(
                  v-if="isDatasetOpened(dataset.dataset_id)",
                  fill-rule="evenodd",
                  clip-rule="evenodd",
                  d="M1.85178 5.22678C1.90403 5.17439 1.9661 5.13283 2.03444 5.10448C2.10278 5.07612 2.17604 5.06152 2.25003 5.06152C2.32402 5.06152 2.39728 5.07612 2.46562 5.10448C2.53396 5.13283 2.59603 5.17439 2.64828 5.22678L9.00003 11.5797L15.3518 5.22678C15.4041 5.17448 15.4662 5.13299 15.5345 5.10469C15.6028 5.07639 15.6761 5.06182 15.75 5.06182C15.824 5.06182 15.8972 5.07639 15.9656 5.10469C16.0339 5.13299 16.096 5.17448 16.1483 5.22678C16.2006 5.27908 16.2421 5.34117 16.2704 5.4095C16.2987 5.47783 16.3132 5.55107 16.3132 5.62503C16.3132 5.69899 16.2987 5.77223 16.2704 5.84056C16.2421 5.90889 16.2006 5.97098 16.1483 6.02328L9.39828 12.7733C9.34603 12.8257 9.28395 12.8672 9.21562 12.8956C9.14728 12.9239 9.07402 12.9385 9.00003 12.9385C8.92604 12.9385 8.85278 12.9239 8.78444 12.8956C8.7161 12.8672 8.65403 12.8257 8.60178 12.7733L1.85178 6.02328C1.7994 5.97103 1.75783 5.90895 1.72948 5.84062C1.70112 5.77228 1.68652 5.69902 1.68652 5.62503C1.68652 5.55104 1.70112 5.47778 1.72948 5.40944C1.75783 5.3411 1.7994 5.27903 1.85178 5.22678Z",
                  fill="#fff"
                )
                path(
                  v-else,
                  fill-rule="evenodd",
                  clip-rule="evenodd",
                  d="M5.22776 16.6472C5.17537 16.595 5.13381 16.5329 5.10545 16.4646C5.0771 16.3962 5.0625 16.323 5.0625 16.249C5.0625 16.175 5.0771 16.1017 5.10545 16.0334C5.13381 15.9651 5.17537 15.903 5.22776 15.8507L11.5806 9.49899L5.22775 3.14724C5.17546 3.09495 5.13397 3.03286 5.10567 2.96453C5.07736 2.89619 5.06279 2.82296 5.06279 2.74899C5.06279 2.67503 5.07736 2.6018 5.10567 2.53346C5.13397 2.46513 5.17546 2.40304 5.22775 2.35074C5.28005 2.29845 5.34214 2.25696 5.41047 2.22866C5.4788 2.20035 5.55204 2.18578 5.626 2.18578C5.69997 2.18578 5.7732 2.20035 5.84154 2.22866C5.90987 2.25696 5.97196 2.29845 6.02425 2.35074L12.7743 9.10074C12.8266 9.153 12.8682 9.21507 12.8966 9.28341C12.9249 9.35175 12.9395 9.42501 12.9395 9.49899C12.9395 9.57298 12.9249 9.64624 12.8966 9.71458C12.8682 9.78292 12.8266 9.84499 12.7743 9.89724L6.02426 16.6472C5.972 16.6996 5.90993 16.7412 5.84159 16.7695C5.77325 16.7979 5.69999 16.8125 5.62601 16.8125C5.55202 16.8125 5.47876 16.7979 5.41042 16.7695C5.34208 16.7412 5.28001 16.6996 5.22776 16.6472Z",
                  fill="white"
                )
              .editable-field.model-name-wrapper
                bdi {{ dataset.name | datasetFormat }}
                | &nbsp;
                strong(v-if="dataset.exists_on_disk === false") (Missing Data)
            .column-7.d-flex
              .new-model-btn(
                v-tooltip:networkElement="'Experimental'",
                v-if="dataset.exists_on_disk === true",
                @click="loadModelIntoExistingDataset(dataset.dataset_id)"
              ) + Load Model
              .new-model-btn(
                v-if="dataset.exists_on_disk === true",
                @click="createModelWithCurrentDataSetPath(dataset.dataset_id)"
              )
                div + New Model
              template(v-else)
                span.img-button(
                  :class="{ disabledIconButton: dataset.models.length > 0 }",
                  @click="deleteDataset(dataset.dataset_id)"
                )
                  img(src="/static/img/project-page/remove-red.svg")

          //-- MODELS BELONG TO DATASET --//
          template(v-if="isDatasetOpened(dataset.dataset_id)")
            .models-list-row.model-list-item.model-list-item-child(
              v-for="(model, index) in getModelsByDataSetId(dataset.dataset_id)",
              @contextmenu.stop.prevent="openContext($event, model.networkID)",
              :key="'Valid_' + model.networkID",
              :class="{ 'is-selected': isItemSelected(model.networkID) }"
            )
              .column-1
                base-checkbox.btn-checkbox(
                  :value="isItemSelected(model.networkID)",
                  :onClick="() => toggleItemSelection(model.networkID)"
                )
                .editable-field.model-name-wrapper
                  span.model-name(
                    :title="model.networkName",
                    v-if="!isRenamingItem(model.networkID)",
                    v-tooltip:bottom="'Click to open Model'",
                    @click.stop="goToNetworkView(model.networkID)"
                  ) {{ model.networkName }}
                  input.rename-control(
                    v-else,
                    v-model="renameValue",
                    @blur="renameModel",
                    @keyup.enter="renameModel",
                    ref="titleInput"
                  )

                .model-unsaved_changes_indicator(
                  v-if="hasUnsavedChanges(model.networkID)"
                )
                  span Unsaved
                  .indicator-circle

              .column-3
                model-status(
                  :statusData="model.networkMeta.coreStatus",
                  :coreError="model.networkMeta.coreError"
                )
              .column-4
                span(@click.stop="") {{ model && model.networkMeta && model.networkMeta.coreStatus && model.networkMeta.coreStatus.Training_Duration ? model.networkMeta.coreStatus.Training_Duration.toFixed(2) + 's' : '-' }}
              .column-5
                router-link.test-link(
                  v-if="typeof model.networkMeta.openTest === 'boolean'",
                  :to="{ name: 'test' }"
                ) Run Test
                  svg(
                    width="14",
                    height="14",
                    viewBox="0 0 20 20",
                    fill="none",
                    xmlns="http://www.w3.org/2000/svg"
                  )
                    path(
                      d="M19.375 1.25V6.875C19.375 7.22047 19.0955 7.5 18.75 7.5C18.4045 7.5 18.125 7.22047 18.125 6.875V2.75875L9.19187 11.6919C9.06984 11.8139 8.90984 11.875 8.75 11.875C8.59016 11.875 8.43016 11.8139 8.30813 11.6919C8.06391 11.4477 8.06391 11.0522 8.30813 10.8081L17.2413 1.875H13.125C12.7795 1.875 12.5 1.59547 12.5 1.25C12.5 0.904531 12.7795 0.625 13.125 0.625H18.75C19.0955 0.625 19.375 0.904531 19.375 1.25ZM16.875 17.5V10C16.875 9.65453 16.5955 9.375 16.25 9.375C15.9045 9.375 15.625 9.65453 15.625 10V17.5C15.625 17.8448 15.3448 18.125 15 18.125H2.5C2.15516 18.125 1.875 17.8448 1.875 17.5V5C1.875 4.65516 2.15516 4.375 2.5 4.375H10C10.3455 4.375 10.625 4.09547 10.625 3.75C10.625 3.40453 10.3455 3.125 10 3.125H2.5C1.46609 3.125 0.625 3.96609 0.625 5V17.5C0.625 18.5339 1.46609 19.375 2.5 19.375H15C16.0339 19.375 16.875 18.5339 16.875 17.5Z",
                      fill="none"
                    )
              .column-6
                collaborator-avatar(
                  v-if="showUser",
                  :list="[{ id: 1, name: (user && user.email) || '', img: null }]"
                )
                span {{ model && model.apiMeta && model.apiMeta.updated ? formatDate(model.apiMeta.updated) : '' }}&nbsp;
              .column-7(@click.stop="")
        //-- DELETED MODELS --//
        .models-list-row.model-list-item(
          v-for="(model, index) in unparsedModels",
          :key="'Unparsed_' + model.id",
          :class="{ 'is-selected': isItemSelected(model.networkID) }",
          @click="onClickDeletedModel(model, index)"
        )
          .column-1
            span.model-name {{ model.name }}
          .column-2 Deleted
          .column-4
            span(@click.stop="") -
          .column-7 Deleted
          .column-3
            span(@click.stop="") -
          .column-6(@click.stop="")
            collaborator-avatar(
              :list="[{ id: 1, name: (user && user.firstName) || '', img: null }]"
            )
            | {{ model && model && model.updated ? formatDate(model.updated) : '' }}

  select-model-modal(
    v-if="showNewModelPopup",
    @close="onCloseSelectModelModal",
    @onChose="onTemplateChoseSelectModelModal"
  )
  workspace-load-network(v-if="showLoadSettingPopup")
</template>

<script>
import SortByButton from "@/pages/projects/components/sort-by-button.vue";
import CollaboratorAvatar from "@/pages/projects/components/collaborator-avatar.vue";
import SelectModelModal from "@/pages/projects/components/select-model-modal.vue";
import ModelStatus from "@/components/different/model-status.vue";
import WorkspaceLoadNetwork from "@/components/global-popups/workspace-load-network.vue";
import ImportModel from "@/components/global-popups/import-model-popup.vue";

import { mapActions, mapState, mapGetters } from "vuex";
import { assembleModel }                  from "@/core/helpers/model-helper";
import { getModelJson as rygg_getModelJson } from "@/core/apiRygg";
import { getNextModelName as rygg_getNextModelName } from "@/core/apiRygg";
import {
  pickFile as rygg_pickFile,
} from "@/core/apiRygg";
import { renderingKernel } from "@/core/apiRenderingKernel.js";
import { arrayIncludeOrOmit } from "@/core/helpers";
import {
  convertModelRecommendationToVisNodeEdgeList,
  createVisNetwork,
} from "@/core/helpers/layer-positioning-helper";
import { buildLayers } from "@/core/helpers/layer-creation-helper";

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
  data: function() {
    return {
      selectedListIds: [],
      selectedDatasetIds: [],
      isImportModelsOpen: false,
      contextModelId: null,
      isContextOpened: false,
      modelContextStyles: {},
      timeoutIds: {},
      contextDatasetId: null,
      isDatasetContextOpened: false,

      // for renaming models
      renameId: null,
      renameValue: null,
      showUser: !process.env.NO_KC,
      dataSetIsOpenedStateArray: [],
    };
  },
  created() {
    // Adding this because of reloads on this page
    // When the stats and test views are their own routes,
    // a better alternative would be to put a lot of the
    // following in the router.
    this.setCurrentView("tutorial-model-hub-view");
    this.expandDatasetsModels();
  },
  computed: {
    ...mapGetters({
      user: "mod_user/GET_userProfile",
      currentProject: "mod_project/GET_project",
      getCurrentStepCode: "mod_tutorials/getCurrentStepCode",
      isEnterpriseMode: "globalView/get_isEnterpriseApp",
      allDatasets: "mod_datasets/GET_datasets",
      projectPath: "mod_project/GET_projectPath",
    }),
    ...mapState({
      currentProjectId: state => state.mod_project.currentProject,
      showFilePickerPopup: state =>
        state.globalView.globalPopup.showFilePickerPopup,
      showNewModelPopup: state =>
        state.globalView.globalPopup.showNewModelPopup,
      showLoadSettingPopup: state =>
        state.globalView.globalPopup.showLoadSettingPopup,
      workspaceContent: state => state.mod_workspace.workspaceContent,
      unparsedModels: state => state.mod_workspace.unparsedModels,
      showImportNetworkFromGitHubOrLocalPopup: state =>
        state.globalView.globalPopup.showImportNetworkfromGitHubOrLocalPopup,
    }),
    get_modelIndexById() {
      return this.$store.getters["mod_workspace/GET_networkIndexById"](
        this.renameId,
      );
    },
  },
  watch: {
    getCurrentStepCode: {
      handler(newVal, oldVal) {
        if (!this.isTutorialMode) {
          return;
        }
        if (newVal !== "tutorial-model-hub-new-button") {
          return;
        }

        this.activateCurrentStep();
      },
      immediate: true,
    },
    "allDatasets.length": {
      handler(newVal, oldVal) {
        if (newVal !== 0 && newVal !== oldVal) {
          this.expandDatasetsModels();
        }
      },
    },
  },
  methods: {
    ...mapActions({
      popupConfirm: "globalView/GP_confirmPopup",
      popupNewModel: "globalView/SET_newModelPopup",
      showErrorPopup: "globalView/GP_errorPopup",
      showInfoPopup: "globalView/GP_infoPopup",
      set_currentNetwork: "mod_workspace/SET_currentNetwork",
      set_currentModelIndex: "mod_workspace/SET_currentModelIndex",
      createProjectModel: "mod_project/createProjectModel",
      setActivePageAction: "modal_pages/setActivePageAction",
      delete_networkById: "mod_workspace/DELETE_networkById",
      closeStatsTestViews: "mod_workspace/SET_statisticsAndTestToClosed",
      setCurrentView: "mod_tutorials/setCurrentView",
      setNextStep: "mod_tutorials/setNextStep",
      deleteDataset: "mod_datasets/deleteDataset",
      refreshDatasets: "mod_datasets/getDatasets",
      SET_openStatistics: "mod_workspace/SET_openStatistics",
      SET_openTest: "mod_workspace/SET_openTest",
      setNetworkNameAction: "mod_workspace/SET_networkName",
      addNetwork: "mod_workspace/ADD_network",
    }),
    goToNetworkView(networkID) {
      // maybe should receive a id and search index by it
      this.$store.commit("mod_workspace/update_network_meta", {
        key: "hideModel",
        networkID: networkID,
        value: false,
      });

      const index = this.workspaceContent.findIndex(
        wc => wc.networkID == networkID,
      );
      this.set_currentNetwork(index > 0 ? index : 0);

      this.closeStatsTestViews({ networkId: networkID });

      this.set_currentModelIndex(index > 0 ? index : 0);
      this.$store.commit("mod_empty-navigation/set_emptyScreenMode", 0);

      if (index !== -1) {
        this.$store.dispatch("mod_workspace/setViewType", "model");
        // this.SET_openStatistics(false);
        // this.SET_openTest(false);
        this.$router.push({ name: "app" });

        this.$nextTick(() => {
          this.setCurrentView("tutorial-workspace-view");
        });
      }
    },
    openTemplate(path) {
      rygg_getModelJson(path);
    },
    isItemSelected(itemId) {
      itemId = parseInt(itemId);
      return this.selectedListIds.indexOf(itemId) !== -1;
    },
    toggleItemSelection(modelId) {
      modelId = parseInt(modelId);
      this.selectedListIds = arrayIncludeOrOmit(this.selectedListIds, modelId);
    },
    isAtLeastOneItemSelected() {
      return (
        this.selectedListIds.length > 0 || this.selectedDatasetIds.length > 0
      );
    },
    isOneModelItemSelected() {
      return this.selectedListIds.length === 1;
    },
    async removeItems() {
      if (!this.selectedListIds.length && !this.selectedDatasetIds.length)
        return; // prevent removing modal when no item are selected

      // checking if dataset have models which are not be deleted
      if (this.selectedDatasetIds.length) {
        let datasets = this.allDatasets
          .map(ds => ({
            id: ds.dataset_id,
            models: ds.models,
          }))
          .filter(ds => this.selectedDatasetIds.includes(ds.id));

        const datasetHasModels =
          datasets
            .map(
              ds =>
                ds.models.filter(x => !this.selectedListIds.includes(x))
                  .length !== 0,
            )
            .filter(x => x).length !== 0;
        if (datasetHasModels) {
          this.showErrorPopup("Dataset has models remove them first");
          return;
        }
      }

      const modelsToDeleteNames = this.workspaceContent
        .filter(model => this.selectedListIds.includes(model.networkID))
        .map(m => m.networkName)
        .join(", ");

      const datasetsToDeleteNames = this.allDatasets
        .filter(ds => this.selectedDatasetIds.includes(ds.dataset_id))
        .map(ds => ds.name)
        .join(`, `);

      let removeMessageStr = `Are you sure you want to delete ${
        datasetsToDeleteNames ? `${datasetsToDeleteNames} ` : ""
      }
      ${datasetsToDeleteNames && modelsToDeleteNames ? " and " : ""}
      ${modelsToDeleteNames ? `${modelsToDeleteNames} ` : ""}`;

      this.popupConfirm({
        type: "DANGER",
        text: removeMessageStr,
        ok: async () => {
          const remove = async () => {
            for (const networkId of this.selectedListIds) {
              await this.delete_networkById(networkId);
            }
            for (let datasetId of this.selectedDatasetIds) {
              await this.$store.dispatch(
                "mod_datasets/deleteDataset",
                datasetId,
              );
            }
            this.selectedListIds = [];
            this.selectedDatasetIds = [];
          };

          if (datasetsToDeleteNames) {
            this.$nextTick(() => {
              this.popupConfirm({
                type: "DANGER",
                text: `You are about to remove one or more of your own datasets <br/> from your hard drive, are you SURE you want to do this?`,
                ok: async () => {
                  remove();
                },
              });
            });
          } else {
            remove();
          }
        },
      });
    },
    isAllItemsSelected() {
      return (
        this.selectedListIds.length === this.workspaceContent.length &&
        this.workspaceContent.length !== 0 &&
        this.selectedDatasetIds.length === this.allDatasets.length &&
        this.allDatasets.length !== 0
      );
    },
    toggleSelectedItems() {
      try {
        if (this.isAllItemsSelected()) {
          this.selectedListIds = [];
          this.selectedDatasetIds = [];
        } else {
          let newWorkspaceContent = [...this.workspaceContent];
          this.selectedListIds = newWorkspaceContent.map(networkItem =>
            parseInt(networkItem.networkID, 10),
          );
          this.selectedDatasetIds = this.allDatasets.map(dataset => {
            return dataset.dataset_id;
          });
        }
      } catch (e) {
        throw new Error(e);
      }
    },
    handleAddNetworkModal() {
      this.setNextStep({
        currentStep: "tutorial-model-hub-new-button",
        activateNextStep: false, // or extra notification will appear
      });

      // open modal
      this.popupNewModel(true);
    },
    onCloseSelectModelModal() {
      this.popupNewModel(false);
    },
    onTemplateChoseSelectModelModal() {},
    confirmFilePickerSelection(selectedItems) {
      this.clearPath();
    },
    clearPath(x) {
      this.isImportModelsOpen = false;
    },
    openLoadModelPopup() {
      // this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.onLoadNetworkConfirmed});
      this.$store.dispatch(
        "globalView/SET_showImportNetworkfromGitHubOrLocalPopup",
        true,
      );
    },
    openContext(e, modelId) {
      this.closeDatasetContext();
      const { pageX, pageY } = e;
      this.modelContextStyles = {
        top: pageY + "px",
        left: pageX + "px",
      };
      this.isContextOpened = true;
      this.contextModelId = modelId;
      document.addEventListener("click", this.closeContext);
    },
    closeContext() {
      document.removeEventListener("click", this.closeContext);
      this.contextModelId = null;
      this.isContextOpened = false;
    },
    handleContextOpenModel() {
      this.goToNetworkView(this.contextModelId);
      this.closeContext();
    },

    async handleContextRemoveModel() {
      const modelId = this.contextModelId;
      const modelName = this.workspaceContent.find(
        model => model.networkID === modelId,
      ).networkName;
      this.popupConfirm({
        type: "DANGER",
        text: `Are you sure you want to delete ${modelName} model from Model Hub?`,
        ok: async () => {
          await this.delete_networkById(modelId);
        },
      });

      this.closeContext();
    },
    async handleContextUnregisterModel() {
      const modelId = this.contextModelId;

      this.popupConfirm({
        type: "DANGER",
        text: `Are you sure you want to unregister ${modelName} model from Overview?`,
        ok: () => {
          this.$store.dispatch("mod_workspace/UNREGISTER_networkById", modelId);
        },
      });

      this.closeContext();
    },
    onClickDeletedModel(model, index) {
      this.popupConfirm({
        type: "DANGER",
        text: `Are you sure you want to remove ${model.name} from Model Hub since it is no longer connected to the Project?`,
        ok: () => {
          this.$store.dispatch("mod_tracker/EVENT_modelDeletion", "Unparsed");
          this.$store
            .dispatch("mod_project/deleteModel", model)
            .then(serverResponse => {
              this.unparsedModels.splice(index, 1);
            });
        },
      });
    },

    // Rename Module
    handleContextRenameModel() {
      this.renameId = this.contextModelId;
      this.renameValue = this.workspaceContent[
        this.get_modelIndexById
      ].networkName;
      setTimeout(() => {
        this.$refs.titleInput[0].focus();
      }, 300);
    },

    isRenamingItem(modelId) {
      return this.renameId === modelId;
    },

    renameModel() {
      // this.setNetworkNameAction(text);
      if (this.renameId !== null) {
        const networkIndex = this.get_modelIndexById;
        this.set_currentNetwork(networkIndex); // @todo
        this.setNetworkNameAction(this.renameValue);
      }
      this.renameId = null;
      this.renameValue = null;
    },

    openDatasetContext(e, datasetId) {
      this.closeContext();

      const { pageX, pageY } = e;
      this.modelContextStyles = {
        top: pageY + "px",
        left: pageX + "px",
      };
      this.isDatasetContextOpened = true;
      this.contextDatasetId = datasetId;
      document.addEventListener("click", this.closeDatasetContext);
    },
    closeDatasetContext() {
      document.removeEventListener("click", this.closeDatasetContext);
      this.contextDatasetId = null;
      this.isDatasetContextOpened = false;
    },
    async handleContextRemoveDataset(datasetId) {
      const models = this.getModelsByDataSetId(this.contextDatasetId);

      if (models.length > 0) {
        this.showInfoPopup(
          "Please remove your models first in order to delete dataset",
        );
        this.closeDatasetContext();
        return;
      }

      const datasetName = this.allDatasets.find(
        dataset => dataset.dataset_id === datasetId,
      ).name;
      this.popupConfirm({
        type: "DANGER",
        text: `Are you sure you want to delete ${datasetName} dataset?`,
        ok: async () => {
          this.$nextTick(() => {
            this.popupConfirm({
              type: "DANGER",
              text: `You are about to remove one or more of your own datasets <br/> from your hard drive, are you SURE you want to do this?`,
              ok: async () => {
                await this.deleteDataset(datasetId);
              },
            });
          }, 0);
        },
      });

      this.closeDatasetContext();
    },
    async handleContextUnregisterDataset(datasetId) {
      if (this.isCoreOffline) {
        this.closeDatasetContext();
        return this.showInfoPopup(
          "Kernel is offline when calling 'handleContextUnregisterDataset'",
        );
      }

      const models = this.getModelsByDataSetId(datasetId);

      if (models.length > 0) {
        this.showInfoPopup(
          "Please remove your models first in order to unregister dataset",
        );
        this.closeDatasetContext();
        return;
      }
      const datasetName = this.allDatasets.find(
        dataset => dataset.dataset_id === datasetId,
      ).name;
      this.popupConfirm({
        type: "DANGER",
        text: `Are you sure you want to unregister ${datasetName} dataset from Model Hub?`,
        ok: async () => {
          await this.$store.dispatch(
            "mod_datasets/unregisterDataset",
            datasetId,
          );
        },
      });
    },
    formatDate(dateString) {
      if (!dateString) {
        return "";
      }
      let date = new Date(dateString);
      return `${date.toLocaleDateString(
        navigator.language,
      )} ${date.toLocaleTimeString([], { hour12: false })}`;
    },
    hasUnsavedChanges(networkId) {
      return this.$store.getters["mod_workspace-changes/get_hasUnsavedChanges"](
        networkId,
      );
    },
    openExportToGithubModal() {
      if (!this.isOneModelItemSelected()) {
        return;
      }
      const modelId = this.selectedListIds[0];
      this.goToNetworkView(modelId);
      this.$store.dispatch("globalView/SET_exportNetworkToGithubPopup", true);
    },
    handleLoadDataClick() {
      this.handleAddNetworkModal();
    },
    getModelsByDataSetId(dataSetId) {
      let matchedModels = [];
      const models = this.workspaceContent;
      models.forEach(model => {
        if (
          model.apiMeta.datasets &&
          model.apiMeta.datasets.includes(dataSetId)
        ) {
          matchedModels.push(model);
        }
      });
      return matchedModels;
    },
    isDatasetOpened(dataSetId) {
      const isOpened = this.dataSetIsOpenedStateArray.includes(dataSetId);
      return isOpened;
    },
    toggleDataSetModels(dataSetId) {
      this.$nextTick(() => {
        this.dataSetIsOpenedStateArray = arrayIncludeOrOmit(
          this.dataSetIsOpenedStateArray,
          dataSetId,
        );
      });
    },
    selectModelById(modelId) {
      if (this.selectedListIds.indexOf(modelId) === -1) {
        this.selectedListIds.push(modelId);
      }
    },
    unSelectModelById(modelId) {
      const idIndex = this.selectedListIds.indexOf(modelId);
      if (idIndex === -1) {
        return;
      }
      this.selectedListIds = [
        ...this.selectedListIds.slice(0, idIndex),
        ...this.selectedListIds.slice(idIndex + 1),
      ];
    },
    createModelWithCurrentDataSetPath(datasetId) {
      this.popupNewModel({ datasetId });
    },
    async loadModelIntoExistingDataset(datasetId) {
      const selectedModelFile = await rygg_pickFile(
        "Choose model to load",
        this.startupDatasetPath,
        [{ extensions: ["*.zip"] }],
      );

      const res = await renderingKernel.importModel(
        datasetId,
        selectedModelFile.path,
      );

      if (res.error) {
        this.showErrorPopup(res.error.message + "\n\n" + res.error.details);
        return;
      }

      const inputData = convertModelRecommendationToVisNodeEdgeList(
        res.graphSpec,
      );
      const network = createVisNetwork(inputData);

      // Wait till the 'stabilized' event has fired
      await new Promise(resolve =>
        network.on("stabilized", async data => resolve()),
      );

      // Creating the networkElementList for the network
      var ids = inputData.nodes.getIds();
      var nodePositions = network.getPositions(ids); // TODO: create a ticket for parsing this if it isn't resolved...

      const layerMeta = await buildLayers(res.graphSpec, nodePositions);

      const namePrefix = "Loaded";
      const modelName = await rygg_getNextModelName(namePrefix);

      const apiMeta = await this.createProjectModel({
        name: modelName,
        project: this.currentProjectId,
        location: `${this.projectPath}/${modelName}`,
        datasets: [datasetId],
      });

      let frontendSettings = {
        apiMeta: apiMeta,
        networkName: modelName,
        networkMeta: null, // Use default
        layerMeta: layerMeta,
      };

      const newNetwork = assembleModel(
        res.datasetSettings,
        res.trainingSettings,
        res.graphSpec,
        frontendSettings,
      );

      await this.$store.dispatch("mod_workspace/setViewType", "model");
      await this.addNetwork({ newNetwork: newNetwork, apiMeta });
    },
    // dataset handlers
    toggleDataSet(value, datasetId) {
      this.selectedDatasetIds = arrayIncludeOrOmit(
        this.selectedDatasetIds,
        datasetId,
      );
    },
    isDatasetSelected(datasetId) {
      return this.selectedDatasetIds.includes(datasetId);
    },

    expandDatasetsModels() {
      const temp = [];
      this.allDatasets.forEach(dataset => {
        temp.push(dataset.dataset_id);
      });
      this.dataSetIsOpenedStateArray = temp;
    },
  },
  created() {
    // Adding this because of reloads on this page
    // When the stats and test views are their own routes,
    // a better alternative would be to put a lot of the
    // following in the router.
    this.setCurrentView("tutorial-model-hub-view");
    this.expandDatasetsModels();
  },
  filters: {
    datasetFormat(val) {
      let lestSlashIx = val.lastIndexOf("/");
      const datasetName = val.substring(lestSlashIx + 1);
      const folderName = val.substring(
        val.substring(0, lestSlashIx).lastIndexOf("/") + 1,
        lestSlashIx,
      );
      if (folderName) {
        return `${folderName[0].toUpperCase() +
          folderName.substring(1)} - ${datasetName}`;
      } else {
        return datasetName;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$header-height: 60px;

* {
  font-family: "Roboto";
}
.project-wrapper {
  height: 100%;
  box-sizing: border-box;
  background-color: theme-var($neutral-7);
  border-radius: 15px 0px 0px 0px;
  padding: 10px 20px;
}
.header-controls {
  display: flex;
  .left-side {
    display: flex;

    margin-bottom: 10px;

    .import-button-container {
      display: flex;
      justify-content: center;

      margin-right: 2rem;
      cursor: pointer;
    }
  }
  .right-side {
    margin-left: auto;
    display: flex;
    align-items: center;
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
  color: #e1e1e1;
  line-height: 23px;
  &.is-disable {
    color: #818181;
    cursor: default;
    pointer-events: none;
  }
  &:hover {
    background: #383f50;
  }
}
.img-button {
  cursor: pointer;
  margin: 0 10px 0 10px;
  &.disabledIconButton {
    // opacity: 0.4;
    filter: grayscale(100%);
    cursor: default;
  }
}
.btn-round-icon {
  cursor: pointer;
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
  background: theme-var($neutral-8);
  border: $border-1;
  box-sizing: border-box;
  border-radius: 4px;
  min-height: calc(100% - #{$header-height});
}

.models-list-row {
  .column-1 {
    position: relative;
    margin-right: auto;
    padding-left: 80px;
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
    min-width: 190px;
    max-width: 190px;
  }
  .column-7 {
    min-width: 180px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;

    img {
      margin-left: 10px;
      margin-bottom: 3px;
    }
  }
}
.model-list-header {
  display: flex;
  height: 43px;
  font-size: 16px;
  align-items: center;
  border-radius: 4px 4px 0px 0px;
  background: theme-var($neutral-7);
  border-bottom: $border-1;
  // padding-right: 20px;
  // padding: 0px 40px;

  .column-1 {
    .btn-checkbox {
      position: absolute;
      left: 41px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 16px;
    }
  }
  .column-6 {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
.model-list-item {
  display: flex;
  height: 56px;
  font-size: 16px;
  font-weight: 400;
  align-items: center;
  border-radius: 4px;
  margin: 10px 0px;
  border: 1px solid transparent;

  &:hover:not(.is-selected) {
    // background: rgba(97, 133, 238, 0.75);
    // box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    background: $color-6;
    color: white;
    .is-favorite {
      path {
        fill: #e1e1e1;
      }
    }

    & .model-unsaved_changes_indicator {
      color: $color-6;
    }

    & .test-link {
      color: white;
      & path {
        fill: white;
      }
    }
  }

  &.is-selected {
    background: theme-var($neutral-6);
    border: 1px solid $color-6;
  }

  .column-1 {
    display: flex;
    justify-content: flex-start;
    flex: 1;
    .btn-checkbox {
      position: absolute;
      left: 41px;
      top: 50%;
      transform: translateY(-50%);
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
      font-size: 16px;
    }
  }
  .column-6 {
    display: flex;
    .collaboratorWrapper {
      width: 30px;
      margin-right: 8px;
    }
  }

  .model-unsaved_changes_indicator {
    margin-right: 10px;
    display: flex;
    justify-content: center;
    align-items: center;

    width: 8rem;
    min-width: 8rem;
    height: 2rem;

    background: theme-var($neutral-8);
    border-radius: 45px;
    border: 1px solid $color-6;

    margin-left: 2rem;

    > span {
      font-family: Nunito Sans;
      font-style: normal;
      font-weight: normal;
      font-size: 12px;
    }

    .indicator-circle {
      height: 0.8rem;
      width: 0.8rem;

      border-radius: 50%;
      background-color: #e1e1e1;

      margin-left: 0.5rem;
    }
  }
  &.model-list-item-child {
    //border-bottom: none;
    .column-1 {
      .btn-checkbox {
        position: absolute;
        left: 81px;
        top: 50%;
        transform: translateY(-50%);
      }
    }
    .column-1 {
      padding-left: 120px;
      .btn-round-icon {
        left: 38px;
      }
    }
  }
}
.fav-icon-action {
  &:hover {
    path {
      stroke: #6185ee;
      stroke-width: 2px;
      border-radius: 1px;
    }
  }
}
.pt-4 {
  padding-top: 4px;
}

.model-no-item {
  color: theme-var($neutral-1);
  text-align: center;

  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);

  & .no-item-mark {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-left: auto;
    margin-right: auto;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: theme-var($neutral-7);
    margin-bottom: 20px;
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
  background-color: #4d556a;
  min-width: 29rem;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.7);
}
.check-model-button {
  width: 18px;
  height: 18px;
  background: theme-var($neutral-8);
  border: $border-1;
  box-sizing: border-box;
  border-radius: 2px;
}
.modelContext {
  position: fixed;
  background: theme-var($neutral-8);
  box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
  border-radius: 2px;
  display: flex;
  flex-direction: column;
  z-index: 12;
  padding: 5px 8px;

  button {
    font-family: "Nunito Sans";
    padding: 5px 8px;
    background: none;
    font-size: 16px;
    text-align: left;

    &:hover {
      color: $color-6;
    }
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
  font-weight: 400;
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
  font-family: "Nunito Sans";
  font-weight: 600;
  font-size: 14px;
  line-height: 29px;
  color: #e1e1e1;
}
.model-name-wrapper {
  // text-overflow: ellipsis;
  overflow: hidden;
  min-width: 100%;
  // height: 1.2em;
  white-space: nowrap;
  padding-right: 15px;
}
.model-list-scrollbar {
  height: calc(100vh - 212px);
  max-height: calc(100vh - 212px);
}
.test-link {
  display: flex;
  align-items: center;
  color: theme-var($text-highlight);
  & svg {
    margin-left: 8px;
    path {
      fill: $color-6;
    }
  }
}
.align-center {
  display: flex;
  align-items: center;
}
.mr-20 {
  margin-right: 20px;
}
.dataset-chevron {
  margin-right: 20px;
  min-width: 18px;
  path {
    fill: theme-var($text-highlight);
  }
}
.new-model-btn {
  margin-right: 20px;
  white-space: nowrap;
  font-size: 16px;
}
</style>
