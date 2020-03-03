<template lang="pug">
  div
    .settings-layer_section
      .form_row
        button.btn.btn--link(type="button" @click="onCancel")
          i.icon.icon-backward
          span Back
      .search.search-input-box
        i.icon.icon-close(@click="clearSearchValue")
        input.search-input(:class="{error: searchDirNotFound}" type="text" v-model="searchValue" @keyup.enter="searchPath")
    .filepicker
      .directory-breadcrumb
        .breadcrumb(
          @click="calcBreadcrumbPath(pathIndex)"
          v-for="(pathName, pathIndex) in currentPath"
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
          :class="{selected:isSelected(fileName)}"
          @dblclick="onFileDoubleClick(fileName)"
          @click="toggleSelectedFile(fileName, $event)"
          v-for="fileName in files"
          v-if="filePickerType === 'file'"
          :key="fileName")
          img(src="/static/img/file-picker/file.svg" class="svg-icon")
          span {{ fileName }}

      .button-group
        span {{ buttonGroupMessage }}
        button.btn.btn--primary.btn--disabled(type="button"
          @click="onCancel"
          ) Cancel
        button.btn.btn--primary(type="button"
          @click="onConfirm"
          :disabled="isConfirmButtonDisabled"
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
      searchValue: '',
      searchDirNotFound: false,
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
    onFileDoubleClick(fileName) {
      if (this.filePickerType !== 'file') { return; }
      this.selectedFiles = [fileName];
      this.onConfirm();
    },
    toggleSelectedFile(fileName, event) {
      if (this.filePickerType !== 'file') { return; }

      if (event.ctrlKey || event.metaKey) {
        if (this.selectedFiles.includes(fileName)) {
          const idxToRemove = this.selectedFiles.findIndex(el => el === fileName);
          this.selectedFiles.splice(idxToRemove, 1);
        } else {
          this.selectedFiles.push(fileName);
        }
      } else {
        this.selectedFiles = [fileName];
      }

    },
    toggleSelectedDirectory(dirName) {
      if (this.filePickerType !== 'folder') { return; }

      // ensuring that only one directory can be chosen
      this.selectedDirectories = [];
      this.selectedDirectories.push(dirName);
    },
    fetchPathInformation(path, isSearching = false) {
      this.selectedFiles = [];
      let theData = {
          reciever: '0',
          action: 'getFolderContent',
          value: path
      };

      coreRequest(theData)
      .then(jsonData => {
          const pathNotFound = jsonData.current_path === "";
          if(isSearching && pathNotFound) {
            this.searchDirNotFound = true;
            return 0;
          } else {
            this.searchDirNotFound = false;
          }
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
          if (!this.selectedDirectories) {
            // if not active directory select, take current
            emitPayload = this.osPathPrefix + this.currentPath.join('/') + '/';
          } else {
            emitPayload = this.selectedDirectories.map(f => this.osPathPrefix + this.currentPath.join('/') + '/' + f);
          }
          console.log('onConfirm emitPayload', emitPayload);
        }

        this.$emit('confirm-selection', emitPayload);
    },
    onCancel() {
        this.$emit('close');
    },
    clearSearchValue() {
      this.searchValue = '';
      this.searchDirNotFound = false;
    },
    searchPath() {
      if(!!this.searchValue) {
        const path = this.osPathPrefix + this.searchValue + this.osPathSuffix
        this.fetchPathInformation(path, true);
      } else {
        this.fetchPathInformation('');
      }
    }
  },
  computed: {
    buttonGroupMessage() {
      if (this.filePickerType === 'file') {
        return this.selectedFiles.length + ' files selected'
      } else {
        return '';
      }
    },
    isConfirmButtonDisabled() {
      if (this.filePickerType === 'file' && this.selectedFiles.length === 0) {
        return true;
      }

      return false;
    }
  }
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
  min-width: 450px;
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
  align-items: center;
  border-top: 0.1rem solid $color-8;

  > * {
    margin: 1rem 1rem 1rem 0;
  }
}

.settings-layer_section {
  margin-top: 0;
  justify-content: space-between;
}

.search-input-box {
  position: relative;
}
.search-input-box .icon-close {
  position: absolute;
  cursor: pointer;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  font-size: 6px;
  display: block;
  text-align: center;
  line-height: 10px;
  border-radius: 50%;
  background-color: #5C6680;
}
.search-input-box .icon-search {
  cursor: pointer;
  position: absolute;
  left: 6px;
  top: 50%;
  transform: translateY(-50%);
}
.search-input {
  width: 150px;
  height: 20px;
  padding-left: 9px;
  padding-right: 15px;
  font-size: 12px;
  color: #E1E1E1;
  border: 1px solid #5C6680;
  background: #4D556A;
  border-radius: 5px;
}
.search-input.error {
  border: 1px solid red;
}
.search-input:focus {
  background: #4D556A;
}
</style>
