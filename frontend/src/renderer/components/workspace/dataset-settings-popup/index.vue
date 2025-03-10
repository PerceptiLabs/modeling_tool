<template lang="pug">
base-global-popup(
  :title="popupTitle",
  title-align="text-center",
  @closePopup="closeModal"
)
  template(:slot="popupTitle + '-content'")
    .main-wrapper.data-settings-modal
      chart-spinner(v-if="isLoadingDataset")
      template(v-else)
        chart-spinner(v-if="isUpdatingDataset")
        .current-dataset
          .form_row
            h5.default-text Current dataset:
            input.dataset-location(disabled, :value="datasetPath")
            //- button.btn.btn--secondary(
            //-   @click="replaceDataset"
            //- ) Replace
        csv-table(
          v-if="dataset",
          :dataSet="dataset",
          :dataSetTypes="dataSetTypes",
          :elementToFeatures="elementToFeatures",
          :locked="true",
          @update="handleCSVDataTypeUpdates"
        )
        data-column-option-sidebar(
          :key="index",
          v-for="index in csvData && csvData.dataTypes.length",
          :columnSelectedType="csvData && csvData.dataTypes",
          :columnNames="csvData && csvData.columnNames",
          :preprocessingTypes="csvData && csvData.preprocessingTypes",
          @handleChange="updatePreprocessingTypes",
          :saveOnMount="false",
          :elementIndex="index - 1"
        )

        //- span.default-text.error(v-if="isAllIOType1sFilled() && !hasInputAndTarget()") Make sure to have at least one input and one target to proceed
        //- span.default-text.error(v-else-if="isAllIOTypesFilled() && !hasOneTarget()") Make sure to have only one target to proceed
        .data-partition-wrapper
          h5.default-text Data partitions:
          triple-input(
            v-model="datasetSettings.partitions",
            separate-sign="%",
            :validate-min="1",
            :validate-max="98",
            :validate-sum="100",
            :withLabels="true"
          )
        div(style="display: flex")
          info-tooltip(
            text="Select random samples to place in each partition, good practice if your dataset is ordered"
          )
          base-checkbox(
            style="font-size: 14px; white-space: nowrap",
            v-model="datasetSettings.randomizedPartitions"
          ) Randomize partition

  template(slot="action", v-if="!isLoadingDataset")
    button.btn.btn--primary.btn--disabled(@click="closeModal()") Cancel
    button.btn.btn--primary(
      @click="updateDataset()",
      :disabled="!isDatasetAvailable"
    )
      | Save
</template>
<script>
import { mapState, mapGetters, mapActions } from "vuex";
import cloneDeep from "lodash.clonedeep";

import { getDatasetContent as rygg_getDatasetContent } from "@/core/apiRygg";
import { getDataset as rygg_getDataset } from "@/core/apiRygg";
import { pickFile as rygg_pickFile } from "@/core/apiRygg";

import CsvTable from "@/components/different/csv-table.vue";
import TripleInput from "@/components/base/triple-input";
import InfoTooltip from "@/components/different/info-tooltip.vue";
import ChartSpinner from "@/components/charts/chart-spinner";
import DataColumnOptionSidebar from "@/components/different/data-column-option-sidebar";
import BaseGlobalPopup from "@/components/global-popups/base-global-popup";

import { makeDatasetSettings } from "@/core/helpers";
import { renderingKernel } from "@/core/apiRenderingKernel";

export default {
  components: {
    CsvTable,
    TripleInput,
    InfoTooltip,
    ChartSpinner,
    DataColumnOptionSidebar,
    BaseGlobalPopup,
  },
  data: () => ({
    dataset: null,
    datasetPath: "",
    datasetSettings: null,
    dataSetTypes: [],
    csvData: null,
    isLoadingDataset: false,
    isUpdatingDataset: false,
    filePickerOptions: {
      showToTutotialDataFolder: true,
    },
    elementToFeatures: {},
    isDatasetAvailable: true,
    popupTitle: "Data Settings",
  }),
  computed: {
    ...mapState({
      startupDatasetPath: state => state.mod_datasetSettings.startupFolder,
    }),
    ...mapGetters({
      currentNetworkDatasetSettings:
        "mod_workspace/GET_currentNetworkDatasetSettings",
      currentNetwork: "mod_workspace/GET_currentNetwork",
    }),
  },

  created() {
    this.loadCurrentDatasetSettings();
  },

  methods: {
    ...mapActions({
      showErrorPopup: "globalView/GP_errorPopup",
    }),

    async loadCurrentDatasetSettings() {
      this.datasetSettings = cloneDeep(this.currentNetworkDatasetSettings);

      const { data } = await rygg_getDataset(this.datasetSettings.datasetId);
      this.datasetPath = data.location;
      console.log('this.datasetPath', this.datasetSettings, this.datasetPath);

      this.loadDataset();
    },
    closeModal() {
      this.$store.dispatch("globalView/SET_datasetSettingsPopupAction", false);
    },
    async loadDataset() {
      const datasetId = this.datasetSettings.datasetId;

      this.isLoadingDataset = true;
      this.$store.dispatch(
        "mod_datasetSettings/setStartupFolder",
        this.datasetPath.match(/(.*)[\/\\]/)[1] || "",
      );

      const fileContents = await rygg_getDatasetContent(datasetId);
      this.dataSetTypes = await renderingKernel
        .getDataTypes(datasetId, this.userEmail)
        .then(res => {
          if ("errorMessage" in res) {
            this.showErrorPopup(
              "Couldn't get model recommendation due to: " +
                res["errorMessage"],
            );
          }
          return res;
        })
        .catch(err => {
          console.error(err);
          this.showErrorPopup("Error: Couldn't infer data types");
        });

      if (fileContents) {
        this.dataset = fileContents;
      }

      let elementToFeatures = {};
      Object.keys(this.datasetSettings.featureSpecs).forEach(key => {
        let el = this.datasetSettings.featureSpecs[key];
        elementToFeatures[key] = {
          layerName: el.iotype,
          dataType: el.datatype,
        };
      });

      this.elementToFeatures = elementToFeatures;

      this.isLoadingDataset = false;
    },
    handleCSVDataTypeUpdates(payload) {
      this.csvData = payload;
      if (
        this.currentNetworkDatasetSettings &&
        this.currentNetworkDatasetSettings.featureSpecs
      ) {
        this.csvData.ioTypes = Object.keys(
          this.currentNetworkDatasetSettings.featureSpecs,
        ).map(
          column =>
            this.currentNetworkDatasetSettings.featureSpecs[column].iotype,
        );
        this.csvData.preprocessingTypes = Object.keys(
          this.currentNetworkDatasetSettings.featureSpecs,
        ).map(
          column =>
            this.currentNetworkDatasetSettings.featureSpecs[column]
              .preprocessing,
        );
      }
    },
    resetDatasetSettings() {
      this.datasetSettings = {
        randomizedPartitions: true,
        partitions: [70, 20, 10],
      };
    },
    async replaceDataset() {
      const selectedDataset = await rygg_pickFile(
        "Choose data to load",
        this.startupDatasetPath,
        [{ extensions: ["*.csv"] }],
      );

      if (selectedDataset && selectedDataset.path) {
        await this.handleDataPathUpdates([selectedDataset.path]);
      }
    },
    async handleDataPathUpdates(dataPath) {
      if (!dataPath || !dataPath.length || !dataPath[0]) {
        return;
      }
      this.datasetPath = dataPath[0];
      this.resetDatasetSettings();
      await this.loadDataset();
      this.checkDataset();
    },
    async updateDataset() {
      this.isUpdatingDataset = true;
      try {
        const datasetSettings = makeDatasetSettings(
          this.datasetSettings.randomizedPartitions,
          this.datasetSettings.partitions,
          this.datasetSettings.randomSeed,      
          this.csvData,
          this.datasetSettings.datasetId          
        );      

        await renderingKernel.waitForDataReady(datasetSettings);

        const newNetwork = cloneDeep(this.currentNetwork);
        const backupCurrentNetwork = cloneDeep(this.currentNetwork);

        // update dataset settings
        newNetwork.networkMeta.datasetSettings = datasetSettings;

        // update component settings
        Object.keys(newNetwork.networkElementList).forEach(key => {
          const layerSettings =
            newNetwork.networkElementList[key].layerSettings;
          if (layerSettings.Type === "IoInput") {
            layerSettings.FilePath = this.datasetPath;

            layerSettings.DataType =
              datasetSettings.featureSpecs[layerSettings.FeatureName].datatype;
          }
        });
        await this.$store.dispatch(
          "mod_workspace/UPDATE_currentNetwork",
          newNetwork,
        );

        const updatePreviewResult = await this.$store.dispatch(
          "mod_workspace/UPDATE_all_previews",
        );
        if (updatePreviewResult.response) {
          await this.$store.dispatch(
            "mod_workspace/UPDATE_currentNetwork",
            backupCurrentNetwork,
          );
          await this.$store.dispatch("mod_workspace/UPDATE_all_previews");

          this.showErrorPopup(
            "Couldn't update dataset due to: " +
              updatePreviewResult.response.data,
          );
        }
      } catch (e) {
        this.showErrorPopup("Couldn't update dataset due to: " + e);
        console.log("Couldn't update dataset due to: " + e);    
      } finally {
        this.isUpdatingDataset = false;
        this.closeModal();
      }
    },
    checkDataset() {
      const columns = Object.keys(
        this.currentNetworkDatasetSettings.featureSpecs,
      );

      this.isDatasetAvailable =
        columns.length === this.csvData.columnNames.length &&
        columns.every(
          (column, index) => column === this.csvData.columnNames[index],
        );

      if (this.isDatasetAvailable) {
        this.csvData.ioTypes = this.csvData.columnNames.map(
          columnName =>
            this.currentNetworkDatasetSettings.featureSpecs[columnName].iotype,
        );
      } else {
        this.showErrorPopup("Couldn't load new dataset");
        this.loadCurrentDatasetSettings();
      }
    },

    updatePreprocessingTypes(numColumn, value) {
      this.csvData.preprocessingTypes.splice(numColumn, 1, value);
    },
  },
};
</script>
<style lang="scss" scoped>
.data-settings-modal {
  min-width: 800px;
  max-width: 80vw;
}

.header {
  position: relative;
  height: 64px;
  display: flex;
  //justify-content: center;
  padding-left: 30px;
  align-items: center;

  background-color: rgb(20, 28, 49);
  border: 1px solid rgba(97, 133, 238, 0.4);
  border-radius: 2px 2px 0px 0px;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.25);

  font-size: 14px;
  line-height: 19px;
  //text-align: center;
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 600;
  color: #b6c7fb;
}

.close-cross {
  position: absolute;
  right: 26px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  cursor: pointer;
  &:after {
    content: "";
    position: absolute;
    width: 18px;
    height: 2px;
    background-color: #6185ee;
    left: 50%;
    top: 50%;
    transform-origin: 50% 50%;
    transform: translate(-50%, -50%) rotate(45deg);
  }
  &:before {
    content: "";
    position: absolute;
    width: 18px;
    height: 2px;
    background-color: #6185ee;
    left: 50%;
    top: 50%;
    transform-origin: 50% 50%;
    transform: translate(-50%, -50%) rotate(-45deg);
  }
}

.main-wrapper {
  // border-right-width: 0;
}
.btn.btn--primary {
  height: auto;
  padding: 10px;
}

.footer-actions {
  padding-top: 30px;
  margin-top: auto;
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  button {
    max-width: 140px;
  }
}

h5 {
  font-size: 14px;
  margin-right: 12px;
  margin-bottom: 0;
}

.data-partition-wrapper {
  // display: flex;
  padding-top: 20px;
  align-items: center;
  margin-bottom: 10px;

  h5 {
    margin-bottom: 10px;
  }
}
.dataset-settings {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 30px;

  .custom-checkbox {
    display: flex;
    cursor: pointer;
  }
}

.current-dataset {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  .form_row {
    width: 100%;
  }

  .dataset-location {
    // width: 100%;
    margin-right: 12px;
  }
  // .dataset-location {
  //   width: 50%;
  //   height: 36px;
  //   background: #232837;
  //   border: 1px solid #5e6f9f;
  //   border-radius: 2px;
  //   margin-right: 12px;
  // }
}

.default-text {
  font-family: Roboto, sans-serif;
  font-style: normal;
  font-weight: normal;
  font-size: 16px;
  line-height: 19px;
  white-space: nowrap;
  // color: #000000;
}
</style>
