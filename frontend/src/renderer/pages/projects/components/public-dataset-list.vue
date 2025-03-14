<template lang="pug">
.container
  chart-spinner(v-if="isLoadingDataSet")
  .public-datasets-page(v-else)
    .search-bar
      i.icon.icon-search
      input(v-model="filter", placeholder="Search dataset by keyword")
    perfect-scrollbar.table-container
      .dataset-table
        .row(
          v-for="(dataset, index) in filteredList",
          :key="dataset.Name + index",
          :class="{ loading: isDatasetDownloading(dataset), loaded: dataset.downloadStatus }"
        )
          .cell.w-250
            strong {{ dataset['Name'] }}
          .cell.font-small.w-100 {{ dataset['Size'] }}
          .cell.font-small.w-150 {{ dataset['Industry'] }}
          .cell.font-small.w-150 {{ dataset['Category'] }}
          .cell.w-100
            a.source-link(
              v-if="dataset['sourceUrl']",
              :href="dataset['sourceUrl']",
              target="_blank",
              v-tooltip:bottom="'Go To Source'"
            )
              img.source-icon(
                :src="categoryList[dataset['Source']] && categoryList[dataset['Source']].iconLink"
              )
          .cell
            button.action-button(
              v-if="!dataset.downloadStatus",
              type="button",
              @click="download(dataset)",
              v-tooltip:bottom="'License: ' + dataset.license"
            ) Load
            button.action-button(
              v-else-if="isDatasetDownloading(dataset)",
              type="button",
              @click="cancelDownload(dataset.UniqueName)"
            ) Cancel
            button.action-button(
              v-else
              type="button",
              @click="useDataset(dataset)"
            ) Create
          .progress-bar(
            v-if="isDatasetDownloading(dataset)",
            :style="{ width: downloadProgress(dataset) + '%' }"
          )
        .mt-50.d-flex.justify-content-center(v-if="isListEmpty") There's no dataset listed.
</template>

<script>
import { mapActions, mapState, mapGetters } from "vuex";
import ChartSpinner from "@/components/charts/chart-spinner";
import { AZURE_BLOB_PATH_PREFIX, modelTypes } from "@/core/constants.js";
import { isTaskComplete as rygg_isTaskComplete } from "@/core/apiRygg";
import { debounce } from "@/core/helpers";
export default {
  components: { ChartSpinner },
  data: () => ({
    filter: "",
    modelTypes: modelTypes,
  }),
  props: {
    modelType: {
      type: String,
      default: "",
    }
  },
  watch: {
    filter: function(value) {
      this.sendSearchingValueToMixPanel(value, this.$store); // sent store to dispatch ev
    },
  },
  computed: {
    ...mapState({
      isDatasetLoaded: state => state["mod_public-datasets"].isDatasetLoaded,
      isLoadingDataSet: state => state["mod_public-datasets"].isLoadingDataSet,
      datasetList: state => state["mod_public-datasets"].datasetList,
      categoryList: state => state["mod_public-datasets"].categoryList,
      currentProject: state => state["mod_project"].currentProject,
    }),
    ...mapGetters({
      projectPath: "mod_project/GET_projectPath",
      datasets: "mod_datasets/GET_datasets",
    }),
    filteredList() {
      let listToBeFiltered = this.datasetList;

      listToBeFiltered = this.datasetList.filter(item => {
        switch (this.modelType) {
          case this.modelTypes.CLASSIFICATION:
            return item.Category.toLowerCase().includes("image classification");
          case this.modelTypes.SEGMENTATION:
            return item.Category.toLowerCase().includes("image segmentation");
          case this.modelTypes.OBJECT_DETECTION:
            return item.Category.toLowerCase().includes("object detection");
          case this.modelTypes.MULTI_MODAL:
            return (
              !item.Category.toLowerCase().includes("image classification") &&
              !item.Category.toLowerCase().includes("image segmentation") &&
              !item.Category.toLowerCase().includes("object detection")
            );
        }
      });

      if (this.filter) {
        listToBeFiltered = listToBeFiltered.filter(
          item =>
            item.Category.toLowerCase().includes(this.filter.toLowerCase()) ||
            item.Name.toLowerCase().includes(this.filter.toLowerCase()) ||
            item.Industry.toLowerCase().includes(this.filter.toLowerCase()),
        );
      }

      return listToBeFiltered;
    },
    isListEmpty() {
      return this.filteredList.length === 0;
    },
  },

  methods: {
    ...mapActions({
      getPublicDatasetList: "mod_public-datasets/getPublicDatasetList",
      downloadDataset: "mod_public-datasets/downloadDataset",
      deleteDownload: "mod_public-datasets/deleteDownload",
    }),
    download(dataset) {
      this.$store.dispatch("mod_tracker/TRACK_datasetDownload", {
        UniqueName: dataset.UniqueName,
        name: dataset.Name,
      });
      this.downloadDataset({
        id: dataset.UniqueName,
        name: dataset.Name,
        projectId: this.currentProject,
        path: this.projectPath + "/Datasets/" + dataset.Name,
        type: this.modelType,
      });
    },
    useDataset(publicDataset) {
      const dataset = this.datasets.find(
        dataset =>
          dataset.source_url ===
          `${AZURE_BLOB_PATH_PREFIX}${publicDataset.UniqueName}`,
      );
      if (dataset) {
        this.$emit("loadDataset", [dataset.location]);
      } else {
        throw new Error("Dataset is not created");
      }
    },
    downloadProgress(dataset) {
      if (dataset.downloadStatus) {
        const { expected, so_far } = dataset.downloadStatus;
        return (so_far / expected) * 100;
      }
      return 0;
    },
    cancelDownload(datasetId) {
      this.deleteDownload(datasetId);
    },
    isDatasetDownloading(dataset) {
      return (
        dataset.downloadStatus &&
        !rygg_isTaskComplete(dataset.downloadStatus.state)
      );
    },
    sendSearchingValueToMixPanel: debounce((value, store) => {
      const isNotEmptyValue = value.length !== 0;
      if (isNotEmptyValue) {
        store.dispatch("mod_tracker/TRACK_datasetSearch", value);
      }
    }, 1000),
  },

  mounted() {
    if (!this.isDatasetLoaded) {
      this.getPublicDatasetList();
    }
  },
};
</script>

<style lang="scss" scoped>
.container {
  position: relative;
  min-height: 200px;
}
.public-datasets-page {
  padding: 0px;
  margin-top: 30px;
  border-radius: 4px;
  overflow: hidden;
  background-color: theme-var($neutral-7);

  .header {
    display: flex;
    span {
      font-size: 16px;
      line-height: 36px;
    }
    .select {
      width: 150px;
    }
  }
}
.table-container {
  height: 300px;
  overflow: auto;
  border: none;
}
.dataset-table {
  width: 100%;
  font-size: 16px;
  line-height: 32px;

  .row {
    display: flex;
    align-items: center;
    z-index: 10000;
    background-color: theme-var($neutral-7);
    border: 1px solid transparent;

    &.disabled {
      pointer-events: none;
      filter: grayscale(1);
      * {
        color: grey;
      }
    }

    &.loading {
      position: relative;

      &:after {
        content: "";
        position: absolute;
        width: 100%;
        height: 4px;
        background: #505050;
        bottom: 0;
        left: 0;
      }
    }
    .progress-bar {
      position: absolute;
      height: 4px;
      background: $color-6;
      bottom: 0;
      left: 0;
      z-index: 1;
    }

    .action-button {
      display: none;
    }

    &.loading,
    &:hover {
      z-index: 10001;
      background: theme-var($neutral-6);
      border-color: $color-6 !important;
    }
    &.loading,
    &:hover,
    &.loaded {
      .action-button {
        display: block;
      }
    }
  }
  .cell {
    border: none;
    height: 100%;
    padding: 4px 8px;
    &:last-child {
      width: 158px;
    }

    a {
      text-decoration: underline;
      color: #b6c7fb;
    }
  }
}

.go-back-btn {
  border: none;
  background: transparent;
  color: #fff;
  font-size: 16px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  img {
    margin-right: 20px;
  }
}

.search-bar {
  display: flex;
  align-items: center;
  border: $border-1;
  background: theme-var($neutral-7);
  padding: 8px 16px;
  font-size: 16px;
  line-height: 20px;

  input {
    background: transparent;
    outline: none;
  }
}

.action-button {
  height: 32px;

  background: $color-6;
  box-sizing: border-box;
  border-radius: 2px;
  box-shadow: none !important;

  font-family: Nunito Sans, sans-serif;
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  line-height: 22px;

  text-align: center;

  color: #ffffff;
  &.is-disabled {
    background-color: rgb(120, 120, 120);
    cursor: not-allowed;
  }
}

.source-link {
  border-radius: 4px;
  padding: 6px 10px;
  background-color: white;
  margin: 0;
}

.source-icon {
  height: 14px;
}

.font-small {
  font-size: 0.8em;
}
.w-100 {
  width: 100px;
}
.w-150 {
  width: 150px;
}
.w-250 {
  width: 250px;
}
.mt-50 {
  margin-top: 50px;
}
</style>
