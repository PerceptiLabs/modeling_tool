<template lang="pug">
div
  spinner(v-show="isUploadingFile", :text="uploadStatus")
  .switch(v-show="!isUploadingFile")
    base-switch(
      :options="options",
      :value="selectedLoadOption",
      @change="onSelectLoadOption"
    )
  .content(v-show="!isUploadingFile")
    template(v-if="selectedLoadOption === LoadDatasetOptions.public")
      public-dataset-list(
        @loadDataset="handleDataPathUpdates",
        :modelType="modelType"
      )
      button.mt-20.link.back-to-previous-step(@click="$emit('back')")
        img(src="/static/img/back-arrow.svg")
        | Back
    template(v-else)
      .form_row.align-items-baseline.mt-20.mb-20
        label.form_label Project Name:
        .form_input
          input.normalize-inputs(
            type="text",
            v-model="datasetName",
          )
          .warning(
            v-if="isDuplicatedDatasetName"
          )
            | Duplicated name
      template(v-if="modelType === modelTypes.CLASSIFICATION")
        .form_row.align-items-baseline.mt-20.mb-20
          label.form_label Save to:
          .form_input
            create-model-picker(
              label="Select Upload Folder",
              @onPick="handleImageClassificationFolderPicker($event)"
            )
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
        .d-flex.justify-content-between
          button.link.back-to-previous-step(@click="backToPreviousStep")
            img(src="/static/img/back-arrow.svg")
            | Back
          button.btn.btn--primary(
            :disabled="isImageClassificationNextButtonDisabled",
            @click="$emit('handleImageClassificationNext', datasetName, imageClassificationFolderPath)"
          ) Next

      template(v-if="modelType === modelTypes.SEGMENTATION")
        .form_row.align-items-baseline.mt-20.mb-20
          label.form_label Save to:
          .form_input
            // LOADING FILE BUTTONS
            .mb-10
              create-model-picker(
                label="Select Image Folder",
                @onPick="handleImageSegmentationImageFolderPicker($event)"
              )
            .mb-10
              create-model-picker(
                label="Select Mask Folder",
                @onPick="handleImageSegmentationMaskFolderPicker($event)"
              )
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

        .d-flex.justify-content-between
          button.link.back-to-previous-step(@click="$emit('back')")
            img(src="/static/img/back-arrow.svg")
            | Back
          button.btn.btn--primary(
            :disabled="isImageSegmentationNextButtonDisabled",
            @click="$emit('handleImageSegmentationNext', datasetName, imageSegmentationImageFolderPath, imageSegmentationMaskFolderPath)"
          ) Next

      template(v-if="modelType === modelTypes.MULTI_MODAL")
        .form_row.align-items-baseline.mt-20.mb-20
          label.form_label Save to:
          .form_input
            create-model-picker(
              label="Select .csv",
              @onPick="handleMultiModalCsvPicker($event)",
              :pickCsv="true"
            )
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
        .d-flex.justify-content-between
          button.link.back-to-previous-step(@click="$emit('back')")
            img(src="/static/img/back-arrow.svg")
            | Back
          button.btn.btn--primary(
            :disabled="isMultiModalNextButtonDisabled",
            @click="$emit('handleMultiModalNext', datasetName, multiModalCsvPath)"
          ) Next
      template(v-if="modelType === modelTypes.OBJECT_DETECTION")
        .form_row.align-items-baseline.mt-20.mb-20
          label.form_label Save to:
          .form_input
            // LOADING FILE BUTTONS
            create-model-picker(
              label="Select .csv",
              @onPick="handleObjectDetectionCsvPicker($event)",
              :pickCsv="true"
            )
        .model-local-wrapper
          .d-flex
            .w-50
              h4.load-guide-title File Guide
              .load-guide-list
                .d-flex
                  span 1.
                  p Ensure CSV file links to images, and contains the bounding boxes, coordinates and classes.
                .d-flex
                  span 2.
                  p If there multiple bounding boxes in one image, enter one bounding box per row, linking to the same image.
                .d-flex
                  span 3.
                  p Ensure that the images are in any of the following formats: .jpg/.jpeg/.png/.tiff/.tif.
            .w-50.d-flex.flex-row-reverse
              .object-detection-image-wrapper
                img(src="static/img/object-detection-guide-csv.png")

        .d-flex.justify-content-between
          button.link.back-to-previous-step(@click="$emit('back')")
            img(src="/static/img/back-arrow.svg")
            | Back
          button.btn.btn--primary(
            :disabled="isObjectDetectionNextButtonDisabled",
            @click="$emit('handleObjectDetectionNext')"
          ) Next
</template>

<script>
import PublicDatasetList from "./public-dataset-list";
import CreateModelPicker from "./create-model-picker.vue";
import Spinner from "@/components/charts/chart-spinner";
import { modelTypes } from "@/core/constants";
const LoadDatasetOptions = {
  public: "Public",
  local: "Local",
};

export default {
  name: "LoadDataSet",
  components: {
    PublicDatasetList,
    CreateModelPicker,
    Spinner,
  },
  data: () => ({
    options: Object.keys(LoadDatasetOptions).map(key => ({
      value: LoadDatasetOptions[key],
      label: LoadDatasetOptions[key],
    })),
    LoadDatasetOptions: LoadDatasetOptions,
    selectedLoadOption: LoadDatasetOptions.public,
    modelTypes: modelTypes,
    datasetName: "",

    imageClassificationFolderPath: null,
    imageSegmentationImageFolderPath: null,
    imageSegmentationMaskFolderPath: null,
    multiModalCsvPath: null,
    objectDetectionCsvPath: null,
  }),
  props: {
    modelType: {
      type: String,
      default: "",
    },
    uploadStatus: {
      type: String,
      default: "",
    },
  },
  computed: {
    isUploadingFile() {
      return this.uploadStatus.length;
    },
    isDuplicatedDatasetName() {
      const allDatasets = this.$store.getters["mod_datasets/GET_datasets"];
      return allDatasets.map((dataset) => dataset.name.toLowerCase()).includes(this.datasetName.toLowerCase());
    },

    isImageClassificationNextButtonDisabled() {
      return this.datasetName === '' || this.isDuplicatedDatasetName || this.imageClassificationFolderPath === null;
    },
    isImageSegmentationNextButtonDisabled() {
      return (
        this.datasetName === '' || this.isDuplicatedDatasetName ||
        this.imageSegmentationImageFolderPath === null ||
        this.imageSegmentationMaskFolderPath === null
      );
    },
    isMultiModalNextButtonDisabled() {
      return this.datasetName === '' || this.isDuplicatedDatasetName || this.multiModalCsvPath === null;
    },
    isObjectDetectionNextButtonDisabled() {
      return this.datasetName === '' || this.isDuplicatedDatasetName || this.objectDetectionCsvPath === null;
    }
  },
  methods: {
    onSelectLoadOption(ev) {
      this.selectedLoadOption = ev;
    },
    handleDataPathUpdates(value) {
      this.$emit("handleDataPathUpdates", value);
    },
    backToPreviousStep() {
      this.$emit("back");
    },

    
    handleImageClassificationFolderPicker(folderPath) {
      this.imageClassificationFolderPath = folderPath;
    },
    handleImageSegmentationImageFolderPicker(path) {
      this.imageSegmentationImageFolderPath = path;
    },
    handleImageSegmentationMaskFolderPicker(path) {
      this.imageSegmentationMaskFolderPath = path;
    },
    handleMultiModalCsvPicker(path) {
      this.multiModalCsvPath = path;
    },
    handleObjectDetectionCsvPicker(path) {
      this.objectDetectionCsvPath = path;
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
.multi-modal-image-wrapper, .object-detection-image-wrapper {
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
.mb-10 {
  margin-bottom: 10px;
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
.align-items-baseline {
  align-items: baseline;
}
.warning {
  position: absolute;
}
</style>
