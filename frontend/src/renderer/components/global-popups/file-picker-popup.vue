<template lang="pug">
  base-global-popup(:tab-set="popupTitle")
    template(:slot="slotContentName")

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
            img(src="/static/file-picker/folder.svg") 
            span {{ d }}

          .list-item(
            :class="{selected:isSelected(f)}"
            @click="toggleSelectedFile(f)"
            v-for="f in files" 
            :key="f")
            img(src="/static/file-picker/file.svg")
            span {{ f }}

    template(slot="action")
      button.btn.btn--primary.btn--disabled(type="button"
        @click="closePopup"
        ) Cancel
      button.btn.btn--primary(type="button"
        @click="applySet"
        ) Confirm

</template>

<script>
import BaseGlobalPopup  from '@/components/global-popups/base-global-popup';

import { coreRequest } from '@/core/apiWeb.js';

export default {
  name: 'FilePicker',
  components: {BaseGlobalPopup},
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

      console.log('request', theData);

      coreRequest(theData)
      .then(jsonData => {
          console.log('response', jsonData);
          this.currentPath = jsonData.current_path.split('/').filter(el => el);   
          this.directories = jsonData.dirs;
          this.files = jsonData.files;
      });
    },
    applySet() {
      this.closePopup();
    },
    closePopup() {
      this.$store.commit('globalView/HIDE_allGlobalPopups');
    },
  },
  computed: {
    slotContentName() {
      return this.popupTitle ? this.popupTitle[0] + '-content' : '';
    }
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
  width: 48rem;
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

  .list-item { 
    display: flex;
    justify-content: left;
    align-items: center;
    padding: 0 1rem;

    img {
      margin-right: 1rem;
    }

    &:hover {
      background-color: powderblue;
    }

    &.selected {
      background-color: powderblue;
    }
  }
  
}

img {
  width: 1rem;
  height: 1rem;
}

</style>