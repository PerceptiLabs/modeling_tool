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
          .form_input
            triple-input(
              v-model="file.settings"
              separate-sign="%"
              :validate-min="1"
              :validate-max="98"
              :validate-sum="100"
            )
    button.btn.btn--link(type="button" @click="addFile") + Add {{ nameAddItem }}

</template>

<script>

  import TripleInput    from "@/components/base/triple-input";
export default {
  name: "SettingsFileList",
  components: {TripleInput},
  props: {
    value: {
      type: Array,
      default: function() { return [] }
    },
    nameAddItem: {
      type: String,
      default: ''
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
        this.fileList = JSON.parse(JSON.stringify(newVal))
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
    height: 20rem;
    overflow-y: auto;
    background-color: $bg-input;
    margin: 0 (-$file-list-indent) .5rem;
    border-radius: $bdrs;
  }
  .file-list_item {
    padding: $file-list-indent;
    border-bottom: 1px solid $bg-toolbar;
    .form_label {
      display: flex;
      overflow-y: hidden;
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
</style>