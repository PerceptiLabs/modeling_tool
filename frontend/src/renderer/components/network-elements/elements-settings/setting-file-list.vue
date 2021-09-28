<template lang="pug">
  .data-file-settings
    .form_row.file-settings_title
      .form_label.heavy-text Files
    ul.file-settings_list
      li.file-list_item(
        style="overflow: hidden"
        v-for="(file, i) in fileList"
        :key="i"
      )
        .form_row
          .form_label
            span(:title="file.path").file-item_path.heavy-text {{ file.path }}
            spinner-upload-file.spinner-upload-file(v-if="loadingFlag")

    //- button.btn.btn--link.light-text(type="button" @click="addFile") + Add {{ nameAddItem }}

</template>

<script>
  import { deepCopy } from "@/core/helpers.js";
  import TripleInput        from "@/components/base/triple-input";
  import SpinnerUploadFile  from "@/components/different/spinner-upload-file.vue";
  import mixinData  from '@/core/mixins/net-element-settings-data.js';


  let mixinArray = [];
  if(!(navigator.userAgent.toLowerCase().indexOf(' electron/') > -1)) {
    mixinArray.push(mixinData);
  }
  
export default {
  name: "SettingsFileList",
  mixins: mixinArray,
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
  
  $file-list-indent: .5rem;

  .heavy-text {      
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 600;
    font-size: 1.2rem;
    line-height: 1.6rem;
  }

  .light-text {
    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 300;
    font-size: 1.1rem;
    line-height: 1.5rem;
  }

  .data-file-settings {
    width: 100%;
    box-sizing: border-box;
    .btn--link {
      color: $toolbar-button-border;
      margin-left: 1rem;

      &:hover {
        text-decoration: none;
      }
    }
  }
  .file-settings_title {   
    margin-bottom: 0.5rem;

    .form_label {
      font-size: 1.2rem;
    }
    .form_input {
      display: flex;
      justify-content: space-around;
      padding-left: 0;
      padding-right: 2rem;

      color: $color-12;
    }
  }
  .file-settings_list {
    max-height: 20rem;
    overflow-y: auto;
    margin-bottom: .5rem;
    border-radius: $bdrs;

    background: theme-var($neutral-7);
    border: 1px solid $bg-toolbar-2;
  }
  .file-list_item {
    padding: $file-list-indent;
    border-bottom: 1px solid $bg-toolbar;
    overflow: hidden;
    background: theme-var($neutral-7);
    .form_row {
      align-items: stretch;
    }
    .form_label {
      flex: 0 0 100%;
      max-width: 100%;
      display: flex;
      overflow-y: hidden;
      align-items: center;
    }
    .btn--icon {
      font-size: 1rem;
      color: $toolbar-separator-color;
      margin-right: .5rem;
    }
  }

  .file-item_path {
    color: $color-12;
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

  .file-list-item_settings {
    /deep/ .triple-input_input {
      background: #2D3754;
    }
  }
</style>
