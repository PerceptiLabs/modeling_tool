<template lang="pug">
  .data-file-settings
    .form_row.file-settings_title
      .form_label Files
      .form_input
        span Train
        span Validate
        span Test
    ul.file-settings_list
      li.file-list_item(
        v-for="(file, i) in fileList"
        :key="i"
      )
        .form_row
          .form_label
            button.btn.btn--icon.icon.icon-app-close(type="button" @click="deleteItem(i)")
            span.file-item_path {{ file.path }}
            spinner-upload-file.spinner-upload-file(v-if="loadingFlag")
          .form_input
            triple-input.file-list-item_settings(
              v-model="file.settings"
              separate-sign="%"
              :validate-min="1"
              :validate-max="98"
              :validate-sum="100"
            )

    button.btn.btn--link(type="button" @click="addFile") + Add {{ nameAddItem }}

</template>

<script>
  import { deepCopy } from "@/core/helpers.js";
  import TripleInput        from "@/components/base/triple-input";
  import SpinnerUploadFile  from "@/components/different/spinner-upload-file.vue";
  import mixinData  from '@/core/mixins/net-element-settings-data.js';
export default {
  name: "SettingsFileList",
  mixins: [mixinData],
  components: {TripleInput, SpinnerUploadFile},
  props: {
    value: {
      type: Array,
      default: function() { return [] }
    },
    nameAddItem: {
      type: String,
      default: ''
    },
    showSpinner: {
      type: Boolean,
    }
  },
  data() {
    return {
      fileList: []
    }
  },
  watch: {
    value: {
      handler(newVal) {
        this.fileList = deepCopy(newVal)
      },
      deep: true,
      immediate: true
    },
    fileList: {
      handler(newVal) {
        if(JSON.stringify(newVal) !== JSON.stringify(this.value)) this.$emit('input', newVal);
      },
      deep: true,
    }
  },
  computed: {
    loadingFlag() {
      return this.$store.state.mod_workspace.webLoadingDataFlag;
    },
  },
  methods: {
    deleteItem(index) {
      this.fileList.splice(index, 1);
    },
    addFile() {
      this.$emit('add-file');
    }
  }
}
</script>
<style lang="scss" scoped>
  @import "../../../scss/base";
  $file-list-indent: .5rem;
  .data-file-settings {
    width: 100%;
    .btn--link {
      color: $color-5;
      text-decoration: underline;
      &:hover {
        text-decoration: none;
      }
    }
  }
  .file-settings_title {
    font-size: 1.4rem;
    margin-bottom: 1rem;
    .form_label {
      font-size: inherit !important;
    }
    .form_input {
      display: flex;
      justify-content: space-between;
      padding: 0 1.5em 0 1rem;
    }
  }
  .file-settings_list {
    max-height: 20rem;
    overflow-y: auto;
    background-color: $bg-input;
    margin: 0 (-$file-list-indent) .5rem;
    border-radius: $bdrs;
  }
  .file-list_item {
    padding: $file-list-indent;
    border-bottom: 1px solid $bg-toolbar;
    .form_row {
      align-items: stretch;
    }
    .form_label {
      display: flex;
      overflow-y: hidden;
      align-items: center;
    }
    .btn--icon {
      font-size: .75rem;
      margin-right: .5rem;
    }
  }

  .file-item_path {
    max-width: 10rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    direction: rtl;
  }
  .form_label {
    position: relative;
  }
  .spinner-upload-file {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
  }
</style>
