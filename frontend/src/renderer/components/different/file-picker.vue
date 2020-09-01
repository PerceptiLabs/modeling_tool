<template lang="pug">
  div
    .settings-layer_section
      .form_row
        button.btn.btn--link(
          v-if="options.showBackButton"
          type="button" 
          @click="onCancel")
          img(src="../../../../static/img/back.svg")
      .search.search-input-box
        i.icon.icon-close(@click="clearSearchValue")
        input.search-input(
          ref="navigate-to-search-input"
          :class="{error: searchDirNotFound}" 
          type="text" 
          v-model="searchValue" 
          @keyup.enter="searchPath"
          @click="onNavigateToClick"
          placeholder="Navigate to...")
    .filepicker(ref="file-picker")
      .directory-breadcrumb(ref="directory-breadcrumb")
        .breadcrumb.home(@click="calcRootFolderPath")
          img(src="/static/img/file-picker/home.svg" class="svg-icon")
        .breadcrumb.ellipsis(v-if="currentPath.length > breadcrumbShowLastXPositions")
          span ...
        .breadcrumb(
          v-for="(pathName, pathIndex) in currentPath"
          v-if="pathIndex >= currentPath.length - breadcrumbShowLastXPositions"
          :key="pathIndex")
          span.directory-crumb(@click="calcBreadcrumbPath(pathIndex)") {{ pathName }}

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
        button.btn.btn--primary(type="button"
          @click="onToTutorialData"
          ) To Tutorial Data Folder
        span.spacer
        span(v-if="options.showNumberSelectedFiles") {{ buttonGroupMessage }}
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
import { filePickerStorageKey } from '@/core/constants.js';
import { mapGetters } from "vuex";

const breadcrumbCharacterLength = 58;


export default {
  name: 'FilePicker',
  props: {
    filePickerType: {
      type: String,
      default: 'file' // can also be 'folder'
    },
    fileTypeFilter: {
      type: Array,
      default: () => []
    },
    confirmCallback: {
      type: Function,
      default: () => {}
    },
    cancelCallback: {
      type: Function,
      default: () => {}
    },
    options: {
      type: Object,
      default: () => ({
        showBackButton: true,
        showNumberSelectedFiles: true,
      })
    },
    startupFolder: {
      type: String,
      default: ''
    },
  },
  data() {
    return {
      popupTitle: ['Load files'],
      currentPath: [],
      directories: [],
      files: [],
      selectedFiles: [],
      selectedDirectories: [],
      osPathPrefix: this.isOsWindows ? '' : '/',
      osPathSuffix: this.isOsWindows && this.filePickerType === 'folder' ? '/' : '', // on windows folder should end with `/`
      clickTimer: null,
      searchValue: '',
      searchDirNotFound: false,
      breadcrumbShowLastXPositions: 5,
      isOsWindows: false
    }
  },
  mounted() {
    let path = '';
    
    if (this.startupFolder) {
      path = this.startupFolder;
    }
    else if(localStorage.hasOwnProperty(filePickerStorageKey) && !this.isTutorialMode) {
      path = localStorage.getItem(filePickerStorageKey);
    }
    
    this.fetchPathInformation(path)
          .then(response => {
            if (response == false) {
              this.fetchPathInformation('');
            }
          });
  },
  methods: {
    onNavigateToClick() {
      if (this.$refs['navigate-to-search-input']) {
        this.$refs['navigate-to-search-input'].focus();
      }
    },
    setOsSpecifics(platform) {
      if (!platform) { return; }

      this.isOsWindows = platform.toLowerCase().includes('windows');
      this.osPathPrefix = this.isOsWindows ? '' : '/';
      this.osPathSuffix = this.isOsWindows && this.filePickerType === 'folder' ? '/' : ''; // on windows folder should end with `/`
    },
    calculateBreadcrumbsLength(path) {
      const reducer = (accumulator, currentValue, index) => {
        const nextValue = accumulator + currentValue;
        if(nextValue > breadcrumbCharacterLength && accumulator <= breadcrumbCharacterLength) {
          this.breadcrumbShowLastXPositions = index ;
        }
        return accumulator + currentValue
      };
      const breadCrumbsArray = path.split('/').map(path => path.length).reverse(); // fill array with elements length and inverse it
      this.breadcrumbShowLastXPositions = breadCrumbsArray.length; // reset to show full length of breadcrumbs
      breadCrumbsArray.reduce(reducer); // set the breadcrumbs length
    },
    isSelected(name) {
      return (this.selectedFiles.includes(name)) || (this.selectedDirectories.includes(name));
    },
    calcBreadcrumbPath(pathIdx) {

      let breadcrumbPath = this.osPathPrefix + this.currentPath.slice(0,pathIdx + 1).join('/') + this.osPathSuffix;;
      if (this.isOsWindows && 
        this.currentPath[pathIdx] && 
        this.currentPath[pathIdx].charAt(this.currentPath[pathIdx].length - 1) === ':') {
        // to handle click on paths such as C:
        breadcrumbPath += '/';
      }

      this.fetchPathInformation(breadcrumbPath);
    },
    calcRootFolderPath() {
      let folderPath = this.isOsWindows ? '.' : this.osPathPrefix + this.osPathSuffix ;
      this.fetchPathInformation(folderPath);
    },
    calcFolderPath(dirName) {
      let folderPath;

      if (this.isOsWindows && this.currentPath.length === 0) {
        folderPath = dirName + this.osPathSuffix;
      } else {
        folderPath = this.osPathPrefix + this.currentPath.join('/') + '/' + dirName + this.osPathSuffix;
      }
      this.fetchPathInformation(folderPath);
    },
    onDirectoryClick(dirName) {
      this.toggleSelectedDirectory(dirName);
    },
    onDirectoryDoubleClick(dirName) {
      this.selectedDirectories = [];
      this.calcFolderPath(dirName);
    },
    onFileDoubleClick(fileName) {
      if (this.filePickerType !== 'file') { return; }
      this.selectedFiles = [fileName];
      this.onConfirm();
    },
    onToTutorialData() {
      this.fetchPathInformation('');
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
    async fetchPathInformation(path, isSearching = false) {
      this.selectedFiles = [];
      let theData = {
          reciever: '0',
          action: 'getFolderContent',
          value: path
      };

      this.$store.dispatch('globalView/ShowCoreNotFoundPopup', null, { root: true });

      try {
        const jsonData = await coreRequest(theData);
        
        this.setOsSpecifics(jsonData.platform);

        const pathNotFound = jsonData.current_path === "";
        if(isSearching && pathNotFound) {
          this.searchDirNotFound = true;
          return 0;
        } else {
          this.searchDirNotFound = false;
        }
        
        if(!pathNotFound) {
          this.calculateBreadcrumbsLength(jsonData.current_path);
          if(!this.isTutorialMode) {
            localStorage.setItem(filePickerStorageKey, jsonData.current_path);
          }
        }
        
        if (jsonData.current_path === '.') {
          this.currentPath = [];
        } else {
          this.currentPath = jsonData.current_path.split('/').filter(el => el);
        }

        this.directories = jsonData.dirs.filter(d => !d.startsWith('.')).sort();
        if (this.fileTypeFilter.length === 0) {
          this.files = jsonData.files;
        } else {
          this.files = jsonData.files.filter(f => {
            let ext = f.replace(/.*\./, '').toLowerCase();
            return ~this.fileTypeFilter.indexOf(ext);
          })
        }
      } catch(e) {
        return false;
      } 
    },
    onConfirm() {
        let emitPayload;

        if (this.filePickerType === 'file') {
          emitPayload = this.selectedFiles.map(f => this.osPathPrefix + this.currentPath.join('/') + '/' + f);
        } else if (this.filePickerType === 'folder') {
          if (!this.selectedDirectories || this.selectedDirectories.length === 0) {
            // if not active directory select, take current
            emitPayload = [this.osPathPrefix + this.currentPath.join('/') + this.osPathSuffix];
          } else {
            emitPayload = this.selectedDirectories.map(d => this.osPathPrefix + this.currentPath.join('/') + '/' + d + this.osPathSuffix);
          }
        }

        this.$store.dispatch('globalView/SET_filePickerPopup', false);
        this.confirmCallback(emitPayload);
    },
    onCancel() {
        this.$store.dispatch('globalView/SET_filePickerPopup', false);
        this.cancelCallback();
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
    },
    ...mapGetters({
      isTutorialMode: 'mod_tutorials/getIstutorialMode',
    })
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

    display: flex;
    justify-content: center;
    align-items: center;

    min-width: 1rem;

    margin: 0 0.2rem;

    & + .breadcrumb:before
    {
      content: '\00a0\00a0>\00a0\00a0';
      pointer-events: none;
    }

    .directory-crumb {
      cursor: pointer;
    }

    &.home {
      cursor: pointer;
    }

    &.ellipsis {
      cursor: default;
    }

    .svg-icon {
      height: 1rem;
      filter: brightness(0) invert(1);
    }
  }
}

.selectable-list {
  display: flex;
  flex-direction: column;
  flex: auto;
  overflow-y: auto;
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

.filename-input {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  border-top: 0.1rem solid $color-8;

  * {
    margin-left: 1rem;

    &:last-child {
      margin-right: 1rem;
    }
  }
}

.button-group {
  display: flex;
  align-items: center;
  border-top: 0.1rem solid $color-8;

  padding: 1rem;

  > *:not(:last-child) {
    margin-right: 1rem;
  }

  span.spacer {
    flex-grow: 1;
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
  border: 1px solid #5C6680;
  background: #363E51;
  color: #B6C7FB;
  border-radius: 5px;

  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 300;
  font-size: 11px;
  line-height: 15px;

  &:focus {
    border: 1px solid $color-6;
  }
}
.search-input.error {
  border: 1px solid red;
}
</style>
