<template lang="pug">
    base-global-popup(:tab-set="popupTitle")
        template(slot="Parser-content")
        .form_row
            .form_label Trainable:
            .form_input
        .form_row
            .form_label Create containers:
            .form_input
        .form_row
            .form_label End points:
            .form_input
        .form_row
            .form_label Pb or pbtxt:
            .form_input
        .form_row
            .form_label Checkpoint:
            .form_input


        template(slot="action")
        button.btn.btn--primary.btn--disabled(type="button"
            @click="closePopup"
            ) Cancel
        button.btn.btn--primary(type="button"
            @click="applySet"
            ) Confirm

</template>

<script>
import BaseGlobalPopup  from "@/components/global-popups/base-global-popup";

export default {
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

            // coreRequest(theData)
            // .then(jsonData => {
            //     console.log('response', jsonData);
            //     this.currentPath = jsonData.current_path.split('/').filter(el => el);   
            //     this.directories = jsonData.dirs;
            //     this.files = jsonData.files;
            // })
        },
        applySet() {
            this.closePopup();
            this.$store.commit('mod_workspace/SET_showStartTrainingSpinner', true);
            this.sendParseModel(this.settings)
                .then(()=> { this.$store.commit('mod_workspace/SET_showStartTrainingSpinner', false) })
                .catch(()=> {})
            },
        closePopup() {
            this.$store.commit('globalView/HIDE_allGlobalPopups');
        },
    },
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