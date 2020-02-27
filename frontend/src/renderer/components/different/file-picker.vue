<template>
    <div class="filepicker">
        <div class="directory-breadcrumb">
            <div class="breadcrumb" 
                @click="calcBreadcrumbPath(pIdx)"
                v-for="(p, pIdx) in currentPath" :key="p">
                {{ p }}
            </div>
        </div>
        <div class="selectable-list">
            <div class="list-item"
                @click="calcFolderPath(dIdx)"
                v-for="(d,dIdx) in directories" 
                :key="d">
                <img src="/static/file-picker/folder.svg" /> {{ d }}
            </div>
            <div class="list-item"
                :class="{selected:isSelected(f)}"
                @click="toggleSelectedFile(f)"
                v-for="f in files" 
                :key="f">
                <img src="/static/file-picker/file.svg" /> {{ f }}
            </div>
        </div>
    </div>
</template>

<script>
import { coreRequest } from '@/helper/core';
export default {    
    data() {
        return {
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
            })
        }
    },
    // computed: {
    //     isSelected(name) {
    //         return (this.files.includes(name));
    //     }
    // },
    mounted() {
        this.fetchPathInformation('');
    }
}
</script>


<style lang="scss" scoped>

.filepicker {
  background-color: white;
  height: 24rem;
  width: 48rem;
  padding: 2rem;
  overflow-y: auto;
}

.directory-breadcrumb {
    display: flex;
    margin: 1rem;

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
        // width: 100%;

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