import {
  getDatasets as rygg_getDatasets,
  deleteDataset as rygg_deleteDataset,
  unregisterModel as rygg_unregisterModel
} from "@/core/apiRygg.js";
const namespaced = true;

const state = {
  datasets: []
};

const getters = {
  GET_datasets(state) {
    return state.datasets;
  }
};
const mutations = {
  SET_datasets(state, value) {
    state.datasets = value;
  },

  DELETE_dataset(state, datasetId) {
    state.datasets = state.datasets.filter(
      dataset => dataset.dataset_id !== datasetId
    );
  },

  DELETE_model(state, modelId) {
    state.datasets = state.datasets.map(dataset => {
      return {
        ...dataset,
        models: dataset.models.filter(model => model !== modelId)
      };
    });
  }
};

const actions = {
  async getDatasets({ commit }) {
    const { data } = await rygg_getDatasets();
    commit(
      "SET_datasets",
      data.results.map(dataset => {
        // adjust path
        return {
          ...dataset,
          name: dataset.name.replace(/\\/g, "/"),
          location: dataset.location.replace(/\\/g, "/")
        };
      })
    );
    return data;
  },

  async deleteDataset({ commit, dispatch }, datasetId) {
    await rygg_deleteDataset(datasetId);

    commit("DELETE_dataset", datasetId);
    dispatch("mod_public-datasets/getPublicDatasetList", null, { root: true });
  },

  deleteModel({ commit }, modelId) {
    commit("DELETE_model", modelId);
  },

  async unregisterModel({ state, dispatch }, modelId) {
    const dataset = state.datasets.find(dataset => {
      return !!dataset.models.find(model => model === modelId);
    });

    if (dataset) {
      await rygg_unregisterModel(dataset.dataset_id, modelId);

      dispatch("deleteModel", modelId);
    }
  }
};

export default {
  getters,
  namespaced,
  state,
  mutations,
  actions
};
