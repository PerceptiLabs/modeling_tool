import Vue from "vue";
import {
  rygg,
  downloadDataset,
  getPublicDatasets,
  getPublicDatasetCategories,
  getTaskStatus,
  isTaskComplete,
  TASK_SUCCEEDED_STATE,
} from "@/core/apiRygg.js";
import { AZURE_BLOB_PATH_PREFIX } from "@/core/constants.js";
const namespaced = true;

const state = {
  fields: [],
  datasetList: [],
  categoryList: [],
  isDatasetLoaded: false,
  isLoadingDataSet: false,

  downloadingCount: 0,
};

const getters = {
  getDatasetByName(state) {
    return name => {
      return state.datasetList.find(d => d.Name === name);
    };
  },
};

const mutations = {
  setFields(state, fields) {
    state.fields = fields;
  },
  setDatasetList(state, list) {
    state.datasetList = list;
    state.isDatasetLoaded = true;
  },
  setCategoryList(state, list) {
    state.categoryList = list;
  },
  setDatasetLoading(state, isLoading) {
    state.isLoadingDataSet = isLoading;
    if (isLoading === true) {
      state.isDatasetLoaded = false;
    }
  },
  setDatasetDownloadStatus(state, { name, status }) {
    const dataset = state.datasetList.find(d => d.Name === name);

    if (dataset) {
      Vue.set(dataset, "downloadStatus", status);
    }
  },
  changeDownloadingCount(state, isIncrease = true) {
    state.downloadingCount = state.downloadingCount + (isIncrease ? 1 : -1);
  },
};

const actions = {
  async getPublicDatasetList({ rootState, commit }) {
    commit("setDatasetLoading", true);

    try {
      let [dataList, categoryList] = await Promise.all([
        getPublicDatasets(),
        getPublicDatasetCategories(),
      ]);

      dataList = dataList.map(publicDataset => {
        const dataset = rootState.mod_datasets.datasets.find(
          dataset =>
            dataset.source_url ===
            `${AZURE_BLOB_PATH_PREFIX}${publicDataset.UniqueName}`,
        );
        if (dataset) {
          return {
            ...publicDataset,
            downloadStatus: {
              downloadTaskId: null,
              expected: 100,
              message: "complete",
              path: dataset.location,
              progress: 0,
              so_far: 100,
              state: TASK_SUCCEEDED_STATE,
              text: "",
              timerId: null,
            },
          };
        }
        return publicDataset;
      });

      const fields = dataList.length > 0 ? Object.keys(dataList[0]) : [];

      commit("setFields", fields);
      commit("setDatasetList", dataList);
      commit("setCategoryList", categoryList);

      commit("setDatasetLoading", false);
    } catch (e) {
      console.log("error", e);
    }
  },

  async downloadDataset({ commit, dispatch }, { id, name, projectId, path, type }) {
    const task_id = await downloadDataset({ id, name, projectId, path, type });

    commit("changeDownloadingCount", true);

    const timerId = setInterval(() => {
      dispatch("getDownloadStatus", name);
    }, 1000);

    commit("setDatasetDownloadStatus", {
      name,
      status: {
        timerId,
        path,
        downloadTaskId: task_id,
        progress: 0,
        text: "",
      },
    });
  },

  async getDownloadStatus({ commit, getters, dispatch }, name) {
    const dataset = getters.getDatasetByName(name);

    if (dataset) {
      const res = await getTaskStatus(dataset.downloadStatus.downloadTaskId);
      const newStatus = { ...dataset.downloadStatus, ...res };

      if (isTaskComplete(res.state)) {
        clearInterval(newStatus.timerId);
        newStatus.timerId = null;
        newStatus.so_far = newStatus.expected;
        dispatch("mod_datasets/getDatasets", null, { root: true });
        commit("changeDownloadingCount", false);
      }
      commit("setDatasetDownloadStatus", {
        name,
        status: newStatus,
      });
    }
  },

  async deleteDownload({ commit, getters }, name) {
    const dataset = getters.getDatasetByName(name);
    if (dataset) {
      const res = await rygg.delete(
        `/tasks/${dataset.downloadStatus.downloadTaskId}`,
      );

      clearInterval(dataset.downloadStatus.timerId);
      commit("changeDownloadingCount", false);
      commit("setDatasetDownloadStatus", {
        name,
        status: null,
      });
    }
  },
};

export default {
  namespaced,
  getters,
  state,
  mutations,
  actions,
};
