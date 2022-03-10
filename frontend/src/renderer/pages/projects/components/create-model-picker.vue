<template lang="pug">
.create-model-folder-picker
  .create-model-folder-picker-label(v-if="!pathLocation") {{ label }}
  div(v-tooltip:bottom="pathLocation", v-else)
    perfect-scrollbar.create-model-folder-picker-path {{ pathLocation }}
  button.btn.btn--primary.create-model-folder-picker-button(
    @click="onClick",
    :disabled="isWaitingToPick"
  ) Browse
</template>
<script>
import {
  pickDirectory as rygg_pickDirectory,
  pickFile as rygg_pickFile,
} from "@/core/apiRygg.js";
import { mapGetters, mapState } from "vuex";
export default {
  name: "CreateModelPicker",
  data() {
    return {
      pathLocation: null,
      isWaitingToPick: false,
    };
  },
  props: {
    label: {
      type: String,
      default: "Select folder",
    },
    pickCsv: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    ...mapState({
      startupDatasetPath: state => state.mod_datasetSettings.startupFolder,
    }),
    ...mapGetters({
      isEnterpriseMode: "globalView/get_isEnterpriseApp",
    }),
  },
  methods: {
    onClick() {
      if (this.pickCsv) {
        this.selectFile();
      } else {
        this.selectFolder();
      }
    },
    async selectFolder() {
      if (this.isEnterpriseMode) {
        return this.enterpriseSelect();
      }
      try {
        this.isWaitingToPick = true;
        const { path } = await rygg_pickDirectory(this.label);
        if (path) this.sendPath(path);
      } finally {
        this.isWaitingToPick = false;
      }
    },
    async selectFile() {
      if (this.isEnterpriseMode) {
        return this.enterpriseSelect();
      }
      try {
        this.isWaitingToPick = true;
        const { path } = await rygg_pickFile(
          this.label,
          this.startupDatasetPath,
          [{ extensions: ["*.csv"] }],
        );
        if (path) this.sendPath(path);
      } finally {
        this.isWaitingToPick = false;
      }
    },
    async onFilePicked(e) {
      const file = e.target.files[0];
      this.pathLocation = file.name;
      this.$emit("onPick", file);
    },
    async enterpriseSelect() {
      try {
        this.isWaitingToPick = true;
        const fileInput = document.createElement("input");
        fileInput.setAttribute("type", "file");
        fileInput.setAttribute("accept", ".zip");
        fileInput.addEventListener("change", this.onFilePicked);
        fileInput.click();
      } finally {
        this.isWaitingToPick = false;
      }
    },
    sendPath(path) {
      this.pathLocation = path;
      this.$emit("onPick", path);
    },
  },
};
</script>
<style lang="scss">
.create-model-folder-picker {
  position: relative;
  width: 270px;
  height: 40px;
  border-radius: 4px;
  background: var(--neutral-7);
}
.create-model-folder-picker-label {
  font-size: 16px;
  line-height: 40px;
  padding: 0 85px 0 10px;
}
.create-model-folder-picker-path {
  font-size: 16px;
  line-height: 40px;
  padding: 0 0 0 10px;
  margin-right: 85px;
  white-space: nowrap;
}
.create-model-folder-picker-button {
  position: absolute;
  top: 0;
  right: 0;
  height: 40px;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
</style>