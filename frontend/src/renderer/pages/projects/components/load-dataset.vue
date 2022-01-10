<template lang="pug">
div
  .switch
    base-switch(
      :options="options",
      :value="selectedLoadOption",
      @change="onSelectLoadOption"
    )
  .content
    //- filter should ne passed here to filter model types 
    template(v-if="selectedLoadOption === LoadDatasetOptions.public")
      public-dataset-list(
        @loadDataset="handleDataPathUpdates",
        :modelType="modelType"
      )
      button.mt-20.link.back-to-previous-step(v-if="isFolderLoadingEnabled")(
        @click="$emit('back')"
      )
        img(src="/static/img/back-arrow.svg")
        | Back
    template(v-else)
      template(v-if="modelType === modelTypes.CLASSIFICATION")
        .model-local-wrapper
          .d-flex
            .w-50
              h4.load-guide-title Folder Structure Guide
              .load-guide-list
                .d-flex
                  span 1.
                  p Create separate folders for each <br/> different category of images.
                .d-flex
                  span 2.
                  p Group them into a folder for upload.
            .w-50.d-flex.flex-row-reverse
              .classification-image-wrapper
                img(src="static/img/classification-model-structure.png")
        .d-flex.justify-content-center.mb-20
          create-model-picker(
            label="Select Upload Folder",
            @onPick="$emit('handleImageClassificationFolderPicker', $event)"
          )
        .d-flex.justify-content-between
          button.link.back-to-previous-step(@click="backToPreviousStep")
            img(src="/static/img/back-arrow.svg")
            | Back
          button.btn.btn--primary(
            :disabled="isImageClassificationNextButtonDissabled",
            @click="$emit('handleImageClassificationNext')"
          ) Next

      template(v-if="modelType === modelTypes.SEGMENTATION")
        .model-local-wrapper
          .d-flex
            .w-50
              h4.load-guide-title File Separation Guide
              .load-guide-list
                .d-flex
                  span 1.
                  p Ensure all files are in .jpg/.jpeg/.png/.tiff/.tif.
                .d-flex
                  span 2.
                  p Separate files for Images and Masks into different folders.
                .d-flex
                  span 3.
                  p Name each image and mask pair identically.
                .d-flex
                  span 4.
                  p Ensure Image files all in either RGB or Grayscale.
                .d-flex
                  span 5.
                  p Ensure Mask files are in Grayscale where the pixel value is the class value.
            .w-50.d-flex.justify-content-around
              .segmentation-image-wrapper
                img(src="static/img/segmentation-guide-image.png")
                h2.segmentation-image-name Images/Four_1.jpg
              .segmentation-image-wrapper
                img(src="static/img/segmentation-guide-mask.png")
                h2.segmentation-image-name Masks/Four_1.png

        // LOADING FILE BUTTONS
        .d-flex.justify-content-center.mb-20
          create-model-picker(
            label="Select Image Folder",
            @onPick="$emit('handleImageSegmentationImageFolderPicker', $event)"
          )
        .d-flex.justify-content-center.mb-20
          create-model-picker(
            label="Select Mask Folder",
            @onPick="$emit('handleImageSegmentationMaskFolderPicker', $event)"
          )
        .d-flex.justify-content-between
          button.link.back-to-previous-step(@click="$emit('back')")
            img(src="/static/img/back-arrow.svg")
            | Back
          button.btn.btn--primary(
            :disabled="isImageSegmentationNextButtonDisabled",
            @click="$emit('handleImageSegmentationNext')"
          ) Next

      template(v-if="modelType === modelTypes.MULTI_MODAL")
        .model-local-wrapper
          .d-flex
            .w-50
              h4.load-guide-title File Guide
              .load-guide-list
                .d-flex
                  span 1.
                  p Ensure CSV file contains two or more columns separated by comma “,” where every column will correspond to either an Input or Target feature.
                .d-flex
                  span 2.
                  p Ensure the first row contains the name of each column as headers. Make sure these names are unique and reflect the content of the column.
            .w-50.d-flex.flex-row-reverse
              .multi-modal-image-wrapper
                img(src="static/img/multi-modal-guide-csv.png")
        .d-flex.justify-content-center.mb-20
          create-model-picker(
            label="Select .csv",
            @onPick="$emit('handleMultiModalCsvPicker', $event)",
            :pickCsv="true",
            :isEnterpriseMode="isEnterpriseMode"
          )
        .d-flex.justify-content-between
          button.link.back-to-previous-step(@click="$emit('back')")
            img(src="/static/img/back-arrow.svg")
            | Back
          button.btn.btn--primary(
            :disabled="isMultiModalNextButtonDisabled",
            @click="$emit('handleMultiModalNext')"
          ) Next
      template(v-if="!isFolderLoadingEnabled")
        .main-file-structure-contents
          .load-contents-group
            button.btn.btn--primary.load-dataset(
              @click="openFilePicker('setDataPath')",
              :disabled="isFilePickerOpened"
            ) Upload .CSV
        .find-out-message Find our starting guide
          span.guide-link(@click="openPLVideoTutorialPage") here.
</template>

<script>
import PublicDatasetList from "./public-dataset-list";
import CreateModelPicker from "./create-model-picker.vue";
import { modelTypes } from "@/core/constants";
import { isFolderLoadingEnabled } from "@/core/helpers";
import { mapGetters } from "vuex";
const LoadDatasetOptions = {
  public: "Public",
  local: "Local",
};

export default {
  name: "LoadDataSet",
  components: {
    PublicDatasetList,
    CreateModelPicker,
  },
  data: () => ({
    options: Object.keys(LoadDatasetOptions).map(key => ({
      value: LoadDatasetOptions[key],
      label: LoadDatasetOptions[key],
    })),
    LoadDatasetOptions: LoadDatasetOptions,
    selectedLoadOption: LoadDatasetOptions.public,
    modelTypes: modelTypes,
    isFolderLoadingEnabled: isFolderLoadingEnabled(),
    // under feature flag
    multiModalPath: null,
  }),
  props: {
    modelType: {
      type: String,
      default: "",
    },
    isImageClassificationNextButtonDissabled: {
      type: Boolean,
    },
    isImageSegmentationNextButtonDisabled: {
      type: Boolean,
    },
    isMultiModalNextButtonDisabled: {
      type: Boolean,
    },
    isFilePickerOpened: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    ...mapGetters({
      isEnterpriseMode: "globalView/get_isEnterpriseApp",
    }),
  },
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
    },
    backToPreviousStep() {
      this.$emit("handleImageSegmentationImageFolderPicker", null);
      this.$emit("handleImageSegmentationMaskFolderPicker", null);
      this.$emit("handleImageClassificationFolderPicker", null);
      this.$emit("handleMultiModalCsvPicker", null);
      this.$emit("back");
    },
  },
};
</script>

<style lang="scss" scoped>
.main-file-structure-contents {
  margin: 24px 0;
  border: 1px dashed #5e6f9f;
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

.find-out-message {
  font-size: 14px;
  line-height: 21px;
  margin-top: 20px;
}
.guide-link {
  cursor: pointer;
  color: $color-6;
  text-decoration: underline;
}
.model-local-wrapper {
  margin: 24px 0;
  background: var(--neutral-7);
  border-radius: 4px;
  padding: 30px;
  min-height: 150px;
}
.classification-image-wrapper {
  border: $border-1;
  padding: 20px;
  background-color: #fff;
}
.multi-modal-image-wrapper {
  border: $border-1;
  padding: 20px;
  background-color: var(--neutral-8);
}
.load-guide-title {
  font-size: 16px;
  margin-bottom: 20px;
}
.load-guide-list {
  font-size: 14px;
  p {
    margin-left: 5px;
    margin-bottom: 0;
  }
}
.mb-20 {
  margin-bottom: 20px;
}
.segmentation-image-wrapper {
  height: 150px;
  width: 150px;
  border: $border-1;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 17px 30px;
  background-color: var(--neutral-8);
}

.segmentation-image-name {
  margin-top: 10px;
  font-size: 10px;
}
.mt-20 {
  margin-top: 20px;
}
.back-to-previous-step {
  border: none;
  background: transparent;
  font-size: 16px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  img {
    margin-right: 20px;
  }
}
</style>
