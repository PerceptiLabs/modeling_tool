<template lang="pug">
  .upload-file(
    :class="{'form_row': showPath, 'invisible': hiddenComponent}"
    )
    input.form_input(type="text" readonly
      v-if="showPath"
      v-model="path"
      )
    //-.btn
    label.upload-file_box(ref="inputFile")
      input.upload-file_input(type="file"
        :multiple="inputMultiple"
        :webkitdirectory="uploadFolder"
        :mozdirectory="uploadFolder"
        :directory="uploadFolder"
        :disabled="inputDisabled"
        @change="uploadFile"
        )
      slot

</template>

<script>

  export default {
    name: "WebUploadFile",
    props: {
      inputMultiple:  { type: Boolean, default: false },
      inputDisabled:  { type: Boolean, default: false },
      showPath:       { type: Boolean, default: true  },
      uploadFolder:   { type: Boolean, default: false },
      hiddenComponent:{ type: Boolean, default: false },
    },
    mounted() {

    },
    data() {
      return {
        path: ''
      }
    },
    methods: {
      openLoadWindow() {
        this.$refs.inputFile.click()
      },
      uploadFile(ev) {
        let selectFiles = ev.target.files;
        let arrNames = [];
        this.$emit('input', selectFiles);
        for(var i=0; i<selectFiles.length; i++) {
          arrNames.push(selectFiles[i].name)
        }
        this.path = `.../${arrNames.join(', ')}`;
      }
    },
  }
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .upload-file {
    margin-bottom: 1rem;
  }
  .upload-file_input {
    width: 0.1px;
    height: 0.1px;
    opacity: 0;
    position: absolute;
    left: -9999px;
    z-index: -10;
  }
</style>
