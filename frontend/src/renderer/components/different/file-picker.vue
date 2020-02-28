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
          @click="calcFolderPath(index)"
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
      osPathPrefix: isOsWindows() ? '' : '/',
      osPathSuffix: isOsWindows() && this.filePickerType === 'folder' ? '/' : '', // on windows folder should end with `/`
    }
  },
  mounted() {
    this.fetchPathInformation('');
  },
  methods: {
    isSelected(name) {
      return (this.selectedFiles.includes(name));
    },
    calcBreadcrumbPath(pathIdx) {
      let breadcrumbPath = this.osPathPrefix + this.currentPath.slice(0,pathIdx + 1).join('/') + this.osPathSuffix;
      this.fetchPathInformation(breadcrumbPath);
    },
    calcFolderPath(folderIndex) {
      let folderPath = this.osPathPrefix + this.currentPath.join('/') + '/' + this.directories[folderIndex] + this.osPathSuffix ;
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
        console.log('Clicked OK', this.selectedFiles);
        this.$emit(
          'files-selected',
          this.selectedFiles.map(f => this.osPathPrefix + this.currentPath.join('/') + '/' + f));
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
//   background-color: $bg-window;
  height: 24rem;
  min-width: 28rem;
  margin: 2rem;
  overflow-y: overlay;
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
