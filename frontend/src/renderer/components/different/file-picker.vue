<template lang="pug">
  div
    .filepicker
      .directory-breadcrumb
        .breadcrumb(
          @click="calcBreadcrumbPath(pIdx)"
          v-for="(p, pIdx) in currentPath" 
          :key="p") 
          span {{ p }}

      .selectable-list
        .list-item(
          @click="calcFolderPath(dIdx)"
          v-for="(d,dIdx) in directories" 
          :key="d") 
          img(src="/static/img/file-picker/folder.svg" class="svg-icon") 
          span {{ d }}

        .list-item(
          :class="{selected:isSelected(f)}"
          @click="toggleSelectedFile(f)"
          v-for="f in files" 
          :key="f")
          img(src="/static/img/file-picker/file.svg" class="svg-icon")
          span {{ f }}

    .button-group
      button.btn.btn--primary.btn--disabled(type="button"
        @click="closePopup"
        ) Cancel
      button.btn.btn--primary(type="button"
        @click="applySet"
        ) Confirm
</template>


<script>
import { coreRequest } from '@/core/apiWeb.js';

export default {
  name: 'FilePicker',
  data() {
    return {
      popupTitle: ['Load files'],
      currentPath: [],
      directories: [],
      files: [],
      selectedFiles: []
    }
  },
  methods: {
    isSelected(name) {
      return (this.selectedFiles.includes(name));
    },
    calcBreadcrumbPath(pathIdx) {
      let breadcrumbPath = '/' + this.currentPath.slice(0,pathIdx + 1).join('/');
      this.fetchPathInformation(breadcrumbPath);
    },
    calcFolderPath(folderIndex) {
      let folderPath = '/' + this.currentPath.join('/') + '/' + this.directories[folderIndex];
      console.log(folderPath);
      this.fetchPathInformation(folderPath);
    },
    toggleSelectedFile(fileName) {
      if (this.selectedFiles.includes(fileName)) {
          const idxToRemove = this.selectedFiles.findIndex(el => el === fileName);
          this.selectedFiles.splice(idxToRemove, 1);
      } else {
          this.selectedFiles.push(fileName);
      }
    },
    fetchPathInformation(path) {
      this.selectedFiles = [];

      let theData = {
          reciever: '0',
          action: 'getFolderContent',
          value: path
      };

      coreRequest(theData)
      .then(jsonData => {
          this.currentPath = jsonData.current_path.split('/').filter(el => el);   
          this.directories = jsonData.dirs;
          this.files = jsonData.files;
      });
    },
    applySet() {
    //   this.$store.dispatch('mod_filepicker/SET_selectedFilePaths', this.selectedFiles);
    //   this.closePopup();
        console.log('Clicked OK', this.selectedFiles);
    },
    closePopup() {
      // this.$store.commit('globalView/HIDE_allGlobalPopups');
    //   this.$store.commit('globalView/gp_filePickerPopup', false);
        console.log('Clicked Cancel');
    },
  },
  mounted() {
    this.fetchPathInformation('');
  }
}
</script>


<style lang="scss" scoped>
@import "../../scss/base";
@import "../../scss/common/info-popup";

.filepicker {
//   background-color: $bg-window;
  height: 24rem;
  min-width: 28rem;
  margin: 2rem;
  overflow-y: auto;
  font-size: 1.1rem;
}

.directory-breadcrumb {
  display: flex;
  margin-bottom: 1rem;

  .breadcrumb {
    cursor: pointer;

    & + .breadcrumb:before
    {
      content: '\00a0\00a0>\00a0\00a0';
    }
  }
}

.selectable-list {

  width: 100%;

  .list-item { 
    display: flex;
    justify-content: left;
    align-items: center;
    padding: 0 1rem;

    .svg-icon {
      margin-right: 1rem;
      filter: invert(100%);
    }

    &:hover {
      background-color: $bg-workspace;
    }

    &.selected {
      background-color: $bg-workspace;
    }
  }
  
}

img {
  width: 1rem;
  height: 1rem;
}

.button-group {
  display: flex;
  justify-content: flex-end;

  button {
    margin-right: 1rem;
  }
}

</style>