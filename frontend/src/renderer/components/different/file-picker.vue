<template lang="pug">
  div
    .filepicker
      .directory-breadcrumb
        .breadcrumb(
          @click="calcBreadcrumbPath(pathIndex)"
          v-for="(pathName, pathIndex) in currentPath"
          v-if="pathIndex >= currentPath.length - 3"
          :key="pathIndex")
          span {{ pathName }}

      .selectable-list
        .list-item(
          :class="{selected:isSelected(directory)}"
          @click="onDirectoryClick(directory)"
          @dblclick="onDirectoryDoubleClick(directory)"
          v-for="(directory, index) in directories"
          :key="index")
          img(src="/static/img/file-picker/folder.svg" class="svg-icon")
          span {{ directory }}

        .list-item(
          :class="{selected:isSelected(f)}"
          @click="toggleSelectedFile(f)"
          v-for="f in files"
          v-if="filePickerType === 'file'"
          :key="f")
          img(src="/static/img/file-picker/file.svg" class="svg-icon")
          span {{ f }}

      .button-group
        button.btn.btn--primary.btn--disabled(type="button"
          @click="onCancel"
          ) Cancel
        button.btn.btn--primary(type="button"
          @click="onConfirm"
          ) Confirm
</template>


<script>
import { coreRequest } from '@/core/apiWeb.js';
import { isOsWindows } from '@/core/helpers.js';

export default {
  name: 'FilePicker',
  props: {
    filePickerType: {
      type: String,
      default: 'file' // can also be 'folder'
    },
    fileTypeFilter: {
      type: Array,
      default: []
    }
  },
  data() {
    return {
      popupTitle: ['Load files'],
      currentPath: [],
      directories: [],
      files: [],
      selectedFiles: [],
      selectedDirectories: [],
      osPathPrefix: isOsWindows() ? '' : '/',
      osPathSuffix: isOsWindows() && this.filePickerType === 'folder' ? '/' : '', // on windows folder should end with `/`
      clickTimer: null,
    }
  },
  mounted() {
    this.fetchPathInformation('');
  },
  methods: {
    isSelected(name) {
      return (this.selectedFiles.includes(name)) || (this.selectedDirectories.includes(name));
    },
    calcBreadcrumbPath(pathIdx) {
      let breadcrumbPath = this.osPathPrefix + this.currentPath.slice(0,pathIdx + 1).join('/') + this.osPathSuffix;
      this.fetchPathInformation(breadcrumbPath);
    },
    calcFolderPath(dirName) {
      let folderPath = this.osPathPrefix + this.currentPath.join('/') + '/' + dirName + this.osPathSuffix ;
      this.fetchPathInformation(folderPath);
    },
    onDirectoryClick(dirName) {
      this.toggleSelectedDirectory(dirName);
    },
    onDirectoryDoubleClick(dirName) {
      this.calcFolderPath(dirName);
    },
    toggleSelectedFile(fileName) {
      if (this.filePickerType !== 'file') { return; }
      if (this.selectedFiles.includes(fileName)) {
          const idxToRemove = this.selectedFiles.findIndex(el => el === fileName);
          this.selectedFiles.splice(idxToRemove, 1);
      } else {
          this.selectedFiles.push(fileName);
      }
    },
    toggleSelectedDirectory(dirName) {
      if (this.filePickerType !== 'folder') { return; }

      // ensuring that only one directory can be chosen
      this.selectedDirectories = [];
      this.selectedDirectories.push(dirName);
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
          this.directories = jsonData.dirs.filter(d => !d.startsWith('.')).sort();
          if (this.fileTypeFilter.length === 0) {
            this.files = jsonData.files;  
          } else {
            this.files = jsonData.files.filter(f => {
              let ext = f.replace(/.*\./, '').toLowerCase();
              return ~this.fileTypeFilter.indexOf(ext);
            })  
          }
      });
    },
    onConfirm() {
        let emitPayload;
        
        if (this.filePickerType === 'file') {
          emitPayload = this.selectedFiles.map(f => this.osPathPrefix + this.currentPath.join('/') + '/' + f);
        } else if (this.filePickerType === 'folder') {
          emitPayload = this.selectedDirectories.map(f => this.osPathPrefix + this.currentPath.join('/') + '/' + f);
          console.log('onConfirm emitPayload', emitPayload);
        }

        this.$emit('confirm-selection', emitPayload);
    },
    onCancel() {
        this.$emit('close');
    },
  },
}
</script>


<style lang="scss" scoped>
@import "../../scss/base";
@import "../../scss/common/info-popup";

.filepicker {

  display: flex;
  flex-direction: column;
  min-height: 20rem;
  max-height: 30rem;
  width: 100%;
  font-size: 1.1rem;
}

.directory-breadcrumb {
  display: flex;
  padding: 1rem;
  border-top: 0.1rem solid $color-8;
  border-bottom: 0.1rem solid $color-8;

  .breadcrumb {
    cursor: pointer;

    & + .breadcrumb:before
    {
      content: '\00a0\00a0>\00a0\00a0';
    }
  }
}

.selectable-list {
  display: flex;
  flex-direction: column;
  flex: auto;  
  overflow-y: scroll;
  padding: 0.3rem 0;
  background-color: $bg-workspace-2;

  .list-item {
    display: flex;
    justify-content: left;
    align-items: center;
    padding: 0.2rem 1rem;

    span {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    .svg-icon {
      height: 1rem;
      width: 1rem;
      margin: 0 1rem 0 2rem;
      filter: invert(100%);
    }

    &.selected {
      background-color: $bg-toolbar;
    }

    &:hover {
      background-color: $col-primary2;
    }
  }

}

.button-group {
  display: flex;
  justify-content: flex-end;
  border-top: 0.1rem solid $color-8;

  button {
    margin: 1rem 1rem 1rem 0;
  }
}

</style>
