import Vue from "vue";
import {
  downloadDataset,
  getPublicDatasets,
  getPublicDatasetCategories,
  getTaskStatus,
  cancelTask,
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
  getDatasetById(state) {
    return id => {
      return state.datasetList.find(d => d.UniqueName === id);
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
  setDatasetDownloadStatus(state, { id, status }) {
    const dataset = state.datasetList.find(d => d.UniqueName === id);

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
      dispatch("getDownloadStatus", id);
    }, 1000);

    commit("setDatasetDownloadStatus", {
      id,
      status: {
        timerId,
        path,
        downloadTaskId: task_id,
        progress: 0,
        text: "",
      },
    });
  },

  async getDownloadStatus({ commit, getters, dispatch }, id) {
    const dataset = getters.getDatasetById(id);

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
        id,
        status: newStatus,
      });
    }
  },

  async deleteDownload({ commit, getters }, id) {
    const dataset = getters.getDatasetById(id);
    if (dataset) {
      const res = await cancelTask(dataset.downloadStatus.downloadTaskId);

      clearInterval(dataset.downloadStatus.timerId);
      commit("changeDownloadingCount", false);
      commit("setDatasetDownloadStatus", {
        id,
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
