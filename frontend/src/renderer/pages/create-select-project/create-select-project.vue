<template lang="pug">
  .project-wrapper#pr-wrapper(@click="onProjectWrapperClick($event)")
    .projectContext(v-if="isContextOpened" :style="projectContextStyles")
      button(@click="renameProject") Rename
      button(@click="deleteProject()") Delete
    .project-box(v-if="!isProjectNameModalOpen")
      .header All projects
      .content
        .sidebar
          button.project-list-filter-button.is-active Local Projects
          //- button.project-list-filter-button.is-disabled Cloud Projects
        .main
          .main-header
            button.btn-icon(
              @click="openProjectImport"
              v-tooltip:bottom="'Import Project'"
              )
              img(src="../../../../static/img/project-page/import.svg")
            button.btn-icon.rounded-border(@click="openProjectNameModal" v-tooltip:bottom="'New Project'")
              img(src="../../../../static/img/plus.svg")
            div.search-input
              img(src="../../../../static/img/search-models.svg")
              input(
                type="text"
                placeholder="Search"
                v-model="searchValue"
              )
            //- div
              //- sort-by-button(
              //-   :options="[{name: 'Test', value: 1}]"
              //-   :option-selected="0"
              //- )
          .main-list
            .main-list-header
              .list-name-name Name
              .list-last-opened Last Opened
            div.main-list-item(
              v-for="project in projectsList.filter(pr => pr.name.indexOf(searchValue) !== -1)"
              @dblclick="onProjectSelect(project)"
              @contextmenu.prevent.stop="openContext($event, project.project_id)"
            )
              input.rename-project-input(
                type="text",
                v-model="renameData.projectFieldValue"
                v-show="renameData.projectId === project.project_id && renameData.isProjectFieldActive"
                @keyup.enter="saveProjectName()"

              )
              span(v-show="!(renameData.projectId === project.project_id && renameData.isProjectFieldActive)").main-list-name.fz-16 {{project.name | trimText}}
              span.main-list-date.fz-16 {{project.created.toString().substring(0, 16).replace("T", " ")}}

    .project-box.set-project-name(
      v-if="isProjectNameModalOpen"
    )
      .header Set Project Name
      .content
        div.project-name-group
          .set-project-text-label Project name
          input.set-project-text-input(
            type="text"
            v-model="newProjectName"
            @keyup.enter="createNewProject"
            )
        div.project-directory-group(
          v-if="!isEnterprise"
        )
          .set-project-text-label Project directory
          input.set-project-text-input(
            readonly
            type="text"
            v-model="newProjectLocation"
            @click="openProjectPathFilePicker"
            )
        div.project-name-action-wrapper
          button.project-name-btn.create(
            :class="{'disabled': !canSave}"
            @click="createNewProject"
          ) Create Project
          button.project-name-btn.cancel(
            @click="closeProjectNameModal"
          ) Cancel

</template>
<script>
  import { mapState, mapGetters, mapActions, mapMutations } from "vuex";
  import SortByButton from "@/components/sort-by-button";
  // import FilePickerPopup        from "@/components/global-popups/file-picker-popup.vue";
  import { generateID } from "@/core/helpers";
  import { coreRequest } from '@/core/apiWeb.js';
  import cloneDeep from 'lodash.clonedeep';
  import { pickFile as rygg_pickFile } from '@/core/apiRygg';
  import { pickDirectory as rygg_pickDirectory } from '@/core/apiRygg';
  import { isEnterpriseApp as rygg_isEnterpriseApp } from '@/core/apiRygg';

  export default {
    name: 'CreateSelectProject',
    components: { SortByButton },
    data() {
      return {
        searchValue: '',
        contextTargetProject: null,
        isContextOpened: false,
        projectContextStyles: {},
        isProjectNameModalOpen: false,
        newProjectName: '',
        newProjectLocation: '',
        renameData: {
          isProjectFieldActive: false,
          projectFieldValue: '',
          projectId: null,
        },
        isEnterprise: true,
      }
    },
    created() {
      document.addEventListener('keyup', this.closeModalByEvent);
    },
    async mounted() {
      this.isEnterprise = await rygg_isEnterpriseApp()
    },
    beforeDestroy() {
      document.removeEventListener('click', this.closeContext);
      // document.removeEventListener('keydown', this.onKeyDown);
    },
    computed:{
      isOpen() {
        return this.$store.state.modal_pages.isOpen
      },
      currentPage() {
        return this.$store.state.modal_pages.currentPage
      },
      projectsList() {
        return this.$store.state.mod_project.projectsList;
      },
      canSave() {
        return this.newProjectName && (this.newProjectLocation || this.isEnterprise);
      },
      ...mapGetters({
        networksWithChanges:                  'mod_workspace-changes/get_networksWithChanges',
        GET_isProjectWithThisDirectoryExist:  'mod_project/GET_isProjectWithThisDirectoryExist',
        GET_isProjectSelected:                'mod_project/GET_isProjectSelected'
      })
    },
    methods: {
      ...mapMutations({
        selectProject:                 'mod_project/selectProject',
        addModelFromLocalDataMutation: 'mod_workspace/add_model_from_local_data',
        deleteNetworkById:             'mod_workspace/delete_networkById',
      }),
      ...mapActions({
        showInfoPopup:            'globalView/GP_infoPopup',
        popupConfirm:             'globalView/GP_confirmPopup',
        setActivePageAction:      'modal_pages/setActivePageAction',
        closePageAction:          'modal_pages/closePageAction',
        getProjects:              'mod_project/getProjects',
        createProject:            'mod_project/createProject',
        deleteProjectAction:      'mod_project/deleteProject',
        updateProjectAction:      'mod_project/updateProject',
        createProjectModel:       'mod_project/createProjectModel',
        addNetwork:               'mod_workspace/ADD_network',
        resetNetwork:             'mod_workspace/RESET_network',
        setStatisticsAvailability:'mod_workspace/setStatisticsAvailability',
        setCheckpointAvailability:'mod_workspace/setCheckpointAvailability',
        clearNetworkChanges:      'mod_workspace-changes/clearNetworkChanges',

      }),
      onProjectWrapperClick(e){
        if(e.target.id === 'pr-wrapper' && this.GET_isProjectSelected) {
          this.closePageAction();
        }
      },
      closeModalByEvent(e){
        const hasTargetProject = this.GET_isProjectSelected;
        const isEscKey = e.keyCode === 27;
        if(hasTargetProject && isEscKey) {
          this.closePageAction();
          document.removeEventListener('keyup', this.closeModalByEvent);
        }
      },
      onProjectSelect(project) {
        const {project_id: projectId} = project;
        if (this.networksWithChanges.length > 0) {
          this.popupConfirm(
          {
            text: 'There are unsaved networks. Are you sure you want to change projects?',
            cancel: () => {
              this.closePageAction();
            },
            ok: () => {
              this.clearNetworkChanges();
            }
          });
        } else {
          this.goToProject(projectId);
        }
      },
      goToProject(projectId) {
        // Setting the projectId to something nonsensical so the watcher
        // can be triggered. This is because everything is now done in the
        // project components now.
        this.selectProject(-1);
        this.selectProject(projectId);
        this.closePageAction();

        this.$nextTick(() => {
          this.setStatisticsAvailability;
          this.setCheckpointAvailability()
        });

        // load models and set them in the workspace from:
        // 1. model's "location" property
        // 2. <project path>/<model name>.json
        if (this.$route.name !== 'projects') {
          this.$router.push({name: 'projects'});
        }
      },
      openProjectNameModal() {
        this.isProjectNameModalOpen = true;
      },
      closeProjectNameModal() {
        this.isProjectNameModalOpen = false;
        this.newProjectName = '';
      },
      async openProjectPathFilePicker() {
        const selectedDirectory = await rygg_pickDirectory(
          "Choose default directory for project"
        );
        if (selectedDirectory && selectedDirectory.path) {
          this.setNewProjectPath([selectedDirectory.path])
        }
      },
      setNewProjectPath(filepath) {
        this.newProjectLocation = filepath && filepath[0] ? filepath[0] : ''
      },
      createNewProject() {
        if(!this.canSave) {
          return;
        }

        const newFolderPath = this.newProjectLocation + '/' + this.newProjectName
        this.createProject({ name: this.newProjectName, default_directory: newFolderPath })
        .then(createProjectRes => {
          this.getProjects();
          this.onProjectSelect(createProjectRes);
          this.newProjectName = '';
        })
        .catch(error => {
          console.error(error);
        })
        .finally(_ =>{
          this.isProjectNameModalOpen = false;
        });
      },
      openContext(e, projectId) {
        const { pageX, pageY } = e;
        this.projectContextStyles = {
          top: pageY + 'px',
          left: pageX + 'px',
        };
        this.isContextOpened = true;
        this.contextTargetProject = projectId;
        document.addEventListener('click', this.closeContext);
      },
      deleteProject() {
        const { contextTargetProject } = this;
        const theProject = this.projectsList.filter(project => project.project_id === contextTargetProject)[0];
        const theProjectModels = theProject.models;
        if(!!theProjectModels.length) {
          this.$store.dispatch('globalView/GP_confirmPopup', {
            text: 'There are still models inside this project. Are you sure you want to delete the project and all its containing models?',
            ok: () => {

              const deleteModelsPromises = theProjectModels.map(model_id => {
                  this.$store.dispatch('mod_project/deleteModel', { model_id });
                  this.$store.dispatch('mod_api/API_closeCore', model_id, { root: true });
              });

              Promise.all(deleteModelsPromises)
                .then(()=> {
                   return this.deleteProjectAction({ projectId: contextTargetProject });
                })
                .catch(e => console.log(e))
                .finally(_ => {
                  for(const id of theProjectModels) {
                    this.deleteNetworkById(id);
                  }
                  this.getProjects();
                })
            },
          })
          return;
        } else {
          this.deleteProjectAction({ projectId: contextTargetProject })
          .catch(e => console.log(e));
        }
      },
      renameProject() {

        const { contextTargetProject } = this;
        const theProject = this.projectsList.filter(project => project.project_id === contextTargetProject)[0];

          this.renameData.isProjectFieldActive = true;
          this.renameData.projectFieldValue = theProject.name;
          this.renameData.projectId = theProject.project_id;
      },
      closeContext() {
        document.removeEventListener('click', this.closeContext);
        this.contextTargetProject = null;
        this.isContextOpened = false
      },
      saveProjectName() {
        const { projectId, projectFieldValue } = this.renameData;
        this.updateProjectAction({projectId, name: projectFieldValue})
          .then(() => {
            this.renameData.isProjectFieldActive = false;
          this.renameData.projectFieldValue = '';
          this.renameData.projectId = null;
          });
      },
      async openProjectImport() {
        const selectedProject = await rygg_pickFile(
          "Choose project to import"
        )
        if (selectedProject && selectedProject.path) {
          this.handleProjectImportConfirm([selectedProject.path])
        }
      },
      async handleProjectImportConfirm (filepath) {
        const processedFilePath = filepath && filepath[0] ? filepath[0] : ''

        let projectName = '';
        if(processedFilePath[processedFilePath.length -1] === '/') {
          const trimedPath = processedFilePath.substring(0, processedFilePath.length - 1);
          projectName = trimedPath.substring(trimedPath.lastIndexOf('/') + 1);
        } else {
          projectName = processedFilePath.substring(processedFilePath.lastIndexOf('/') + 1);
        }

        const createProjectReq = {
            name: projectName,
            default_directory: processedFilePath
        };

        if(this.GET_isProjectWithThisDirectoryExist(processedFilePath)) {
          this.showInfoPopup('This project already exist');
          return;
        }


        this.selectedFiles = [];
        try {
          const { dirs, current_path} = await rygg_getFolderContent(processedFilePath);
          const haveDirectories = dirs.length > 0;
          if(!haveDirectories) {
            // cerate project only with that dir
            const createdProject = await this.createProject(createProjectReq);
            this.selectProject(createdProject.project_id);
            this.closePageAction();

          } else {

            const createdProject = await this.createProject(createProjectReq);

            const modelPaths = dirs.map(dirPath => current_path + '/' + dirPath);

            const promiseArray =
              modelPaths.map(modelPath => rygg_getModelJson(modelPath + '/model.json'));

            let localModelsData = await Promise.all(promiseArray);
            localModelsData = localModelsData.filter(model => model);
            const atLeastOneFolderHaveModelsJsonFile = localModelsData.length !== 0;
            if(atLeastOneFolderHaveModelsJsonFile) {
              this.resetNetwork();
              let modelCreationPromises = [];
              for(let index in localModelsData) {
                const loadedModel = localModelsData[index];
                modelCreationPromises.push(this.createProjectModel({
                  name: loadedModel.networkName,
                  project: createdProject.project_id,
                  location: loadedModel.apiMeta.location,
                }))
              }


              const modelCreatinResponses = await Promise.all(modelCreationPromises);

              for(let index in modelCreatinResponses) {
                const apiMeta = modelCreatinResponses[index];
                const modelJson = localModelsData[index];

                let template = cloneDeep(modelJson);
                template.networkName = modelJson.networkName;
                template.networkID = apiMeta.model_id;
                delete template.apiMeta;
                await this.addNetwork({network: template, apiMeta: apiMeta, focusOnNetwork: false});
              }
            }
            await this.$store.dispatch('mod_project/getProjects');
            this.clearNetworkChanges();
            this.selectProject(createdProject.project_id);
            this.closePageAction();

          }


        } catch(e) {
          return false;
        }
      }
    },
    filters: {
      trimText (value) {
        return value.length > 24 ? value.substring(0, 24) + '..' : value;
      }
    }
  }

</script>
<style lang="scss" scoped>
  * {
    font-family: "Nunito Sans";
  }
  .projectContext {
    position: fixed;
    box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    border-radius: 2px;
    display: flex;
    flex-direction: column;
    z-index: 12;
    padding: 5px 8px;

    background: white;
    box-sizing: border-box;
    box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    border-radius: 2px;


    button {
      font-family: 'Nunito Sans';
      padding: 5px 8px;
      background: none;
      font-size: 16px;;
      text-align: left;
    }
  }
  .project-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: theme-var($neutral-7);
    border-radius: 15px 0px 0px 0px;
    padding: 10px 20px;
  }
  .project-box {
    min-width: 680px;
    min-height: 500px;

    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
    border-radius: 2px;
    &.set-project-name {
      min-width: 320px;
      min-height: 100px;
      .content {
        display: block;
        padding: 20px;
      }
    }
  }
  .header {
    background: #363E50;
    border-radius: 2px 2px 0 0;
    height: 38px;
    width: 100%;
    font-size: 14px;
    line-height: 38px;
    text-align: center;

    background: rgba(97, 133, 238, 0.2);
    border: 1px solid rgba(97, 133, 238, 0.4);
    border-radius: 2px 2px 0px 0px;
    font-family: "Nunito Sans";
    font-style: normal;
    font-weight: 600;
    font-size: 14px;
    line-height: 38px;

    color: #B6C7FB;
  }
  .content {
    display: flex;
    padding: 23px 0;

  }
  /* Sidebar */
  .sidebar {
    width: 30%;
    padding-left: 29px;
    margin-right: 10px;
  }
  .create-new-button {
    margin-bottom: 30px;
    font-size: 16px;
    background: #1C1C1E;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
    border: 1px solid #E1E1E1;
    border-radius: 2px;
    line-height: 29px;
    width: 100%;
    img {
      margin-right: 7px;
    }
  }
  .project-list-filter-button {
    position: relative;
    padding-left: 15px;
    display: block;
    background-color: transparent;
    border-left: 3px solid transparent;
    font-size: 16px;
    height: 29px;
    margin-bottom: 16px;
    font-family: 'Nunito Sans';
    color: #E1E1E1;
    &.is-active {
      color: #9BB2F6;
      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 3px;
        height: 24px;
        border-radius: 3px;
        background-color: #9BB2F6;
      }
     }
  }
  /* main */
  .main {
    width: 70%;
    position: relative;
    &::after{
      content: '';
      position: absolute;
      top: 0;
      height: 100%;
      width: 1px;
      background-color: #363E51;
      left: -23px;
    }
  }
  .main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  .search-input {
    position: relative;
    /*width: 333px;*/
    width: auto;
    width: 75%;
    margin-right: 30px;


    img {
      cursor: pointer;
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      left: 10px;
    }
    input {
      padding-left: 44px;
      background-color: transparent;
      border-radius: 5px;
      height: 29px;
      font-size: 16px;
      border: 1px solid #4D556A;
      border-radius: 2px;
    }
  }
  .main-list {

  }
  .main-list-header {
    display: flex;
    justify-content: space-between;
    padding: 14px 30px 14px 10px;
    border-top: 1px solid #363E51;
    border-bottom: 1px solid #363E51;
  }
  .list-name-name {
    font-size: 16px;
    color: #818181;
    font-weight: bold;
  }
  .list-last-opened {
    font-size: 16px;
    color: #fff;
    font-weight: bold;
  }
  .main-list-item {
    position: relative;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    padding: 14px 30px 14px 10px;
    border-bottom: 1px solid #363E51;
    font-family: 'Nunito Sans';
    &:hover {
      background: rgba(97,133,238, 0.5);
    }
  }
  .fz-16 {
    font-size: 16px;
  }
  .btn-icon {
    background: none;
    &.rounded-border {
      border: 1px solid #fff;
      border-radius: 2px;
      padding: 3px;
      line-height: 100%;
    }
  }
  .rename-project-input {
    width: 260px;
  }
  .is-disabled {
    color: #818181;
    cursor: default;
  }
  .set-project-text-label {
    font-family: Nunito Sans;
    font-weight: 300;
    font-size: 12px;
    line-height: 16px;
    color: #9E9E9E;
    margin-bottom: 1rem;
  }
  .set-project-text-input {
    width: 100%;
    height: 35px;
    border: 1px solid #4D556A;
    background: transparent;
    box-sizing: border-box;
    border-radius: 2px;
    font-family: Nunito Sans;
    font-weight: 600;
    font-size: 14px;
    line-height: 19px;
    color: theme-var($neutral-1);

    + .set-project-text-label {
      margin-top: 2rem;
    }
  }
  .project-name-action-wrapper {
    display: flex;
    flex-direction: row-reverse;
    margin-top: 20px;
  }
  .project-name-btn {
    height: 32px;
    background: rgba(97, 133, 238, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-sizing: border-box;
    border-radius: 2px;

    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 600;
    font-size: 14px;
    line-height: 19px;
    color: theme-var($neutral-1);
    &.disabled {
      opacity: 0.5;
    }
    &.create {
      margin-left: 10px;
      background: #6185EE;
    }
  }
</style>
