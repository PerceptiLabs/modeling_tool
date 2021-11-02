<template lang="pug">
div
  .switch
    base-switch(
      :options="options"
      :value="selectedLoadOption"
      @change="onSelectLoadOption"
    )
  .content
    public-dataset-list(
      v-if="selectedLoadOption === LoadDatasetOptions.public"
      @loadDataset="handleDataPathUpdates"
    )
    template(v-else)
      .main-file-structure-contents
        .load-contents-group
          button.btn.btn--primary.load-dataset(
            @click="openFilePicker('setDataPath')"
          ) Upload .CSV
      div.find-out-message Find our starting guide 
        span.guide-link(@click="openPLVideoTutorialPage") here.
</template>

<script>
import PublicDatasetList from "./public-dataset-list";

const LoadDatasetOptions = {
  public: "Public",
  local: "Local"
};

export default {
  name: "LoadDataSet",
  components: { PublicDatasetList },
  data: () => ({
    options: Object.keys(LoadDatasetOptions).map(key => ({
      value: LoadDatasetOptions[key],
      label: LoadDatasetOptions[key]
    })),
    LoadDatasetOptions: LoadDatasetOptions,
    selectedLoadOption: LoadDatasetOptions.public,
  }),
  methods: {
    onSelectLoadOption(ev) {
      this.selectedLoadOption = ev;
    },
    openFilePicker() {
      this.$emit("openFilePicker");
    },
    openPLVideoTutorialPage() {
      this.$emit("openPLVideoTutorialPage");
    },
    handleDataPathUpdates(value) {
      this.$emit("handleDataPathUpdates", value);
    }
  }
};
</script>

<style lang="scss" scoped>
.main-file-structure-contents {
  margin: 24px 0;
  border: 1px dashed #5E6F9F;
  border-radius: 2px;
  height: 250px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
}

.load-contents-group {
  display: flex;
  justify-content: center;
  align-content: center;
  flex-direction: column;

  .load-dataset {
    padding: 10px;
    font-weight: 700;
    font-size: 14px;
    box-shadow: none;
  }
}

.switch {
  width: 200px;
  margin: 0 auto;
}
</style>
