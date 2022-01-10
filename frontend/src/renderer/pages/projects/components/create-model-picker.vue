<template lang="pug">
.create-model-folder-picker
  p.create-model-folder-picker-label(v-if="!pathLocation") {{ label }}
  p.create-model-folder-picker-path(v-else, :title="pathLocation") {{ pathLocation }}
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
import { whenCeleryTaskDone } from "@/core/helpers";
import { uploadDatasetToFileserver as rygg_uploadDatasetToFileserver } from "@/core/apiRygg";
import { getDataset as rygg_getDataset } from "@/core/apiRygg";
import { mapState } from "vuex";
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
    isEnterpriseMode: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    ...mapState({
      startupDatasetPath: state => state.mod_datasetSettings.startupFolder,
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
    async enterpriseSelect() {
      try {
        this.isWaitingToPick = true;
        const fileInput = document.createElement("input");
        fileInput.setAttribute("type", "file");
        fileInput.setAttribute("accept", ".csv,.zip");
        fileInput.addEventListener("change", async e => {
          const file = e.target.files[0];
          const {
            data: { task_id, dataset_id },
          } = await rygg_uploadDatasetToFileserver(file);
          await whenCeleryTaskDone(task_id, e => console.log(e));
          const {
            data: { location: path },
          } = await rygg_getDataset(dataset_id);
          if (path) this.sendPath(path);
        });
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
  padding: 0 85px 0 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  direction: rtl;
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