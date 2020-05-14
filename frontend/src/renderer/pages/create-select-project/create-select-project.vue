<template lang="pug">
  .project-wrapper
    .projectContext(v-if="isContextOpened" :style="projectContextStyles")
      button(@click="renameProject") Rename
      button(@click="deleteProject()") Delete
    .project-box(v-if="!isProjectNameModalOpen")
      .header All projects
      .content
        .sidebar
          button.project-list-filter-button.is-active Local Projects
          button.project-list-filter-button.is-disabled Cloud Projects
        .main
          .main-header
            button.btn-icon
              img(src="../../../../static/img/project-page/import.svg")
            button.btn-icon.rounded-border(@click="openProjectNameModal")
              img(src="../../../../static/img/plus.svg")
            div.search-input
              img(src="../../../../static/img/search-models.svg")
              input(
                type="text"
                placeholder="Search"
                v-model="searchValue"
              )
            div
              sort-by-button(
                :options="[{name: 'Test', value: 1}]"
                :option-selected="0"
              )
          .main-list
            .main-list-header
              .list-name-name Name
              .list-last-opened Last Opened
            div.main-list-item(
             v-for="project in projectsList.filter(pr => pr.name.indexOf(searchValue) !== -1)" 
              @dblclick="onProjectSelectHandler(project)"
              @contextmenu.prevent.stop="openContext($event, project.project_id)"
            ) 
              input.rename-project-input(
                type="text",
                v-model="renameData.projectFieldValue"
                v-show="renameData.projectId === project.project_id && renameData.isProjectFieldActive"
                @keyup.enter="saveProjectName()"
              
              )
              span(v-show="!(renameData.projectId === project.project_id && renameData.isProjectFieldActive)").main-list-name.fz-16 {{project.name | trimText}}
              span.main-list-date.fz-16 {{project.created.toString().substring(0, 16)}}
          
    .project-box.set-project-name(
      v-if="isProjectNameModalOpen"
    )
      .header Set Project Name
      .content
        .set-project-text-label Project name
        input.set-project-text-input(
          type="text"
          v-model="newProjectName"
          @keyup.enter="createNewProject"
          )
        div.project-name-action-wrapper
          button.project-name-btn.create(
            :class="{'disabled': newProjectName === ''}"
            @click="createNewProject"
          ) Create Project
          button.project-name-btn.cancel(
            @click="closeProjectNameModal"
          ) Cancel

</template>
<script>
  import { mapActions, mapMutations } from "vuex";
  import SortByButton from "@/components/sort-by-button";
  import { generateID } from "@/core/helpers";
import { debug } from 'util';

  export default {
    name: 'CreateSelectProject',
    components: {SortByButton},
    data() {
      return {
        searchValue: '',
        contextTargetProject: null,
        isContextOpened: false,
        projectContextStyles: {},
        isProjectNameModalOpen: false,
        newProjectName: '',
        renameData: {
          isProjectFieldActive: false,
          projectFieldValue: '',
          projectId: null,
        }
      }
    },
    created() {
      this.getProjects();
    },
    beforeDestroy() {
      document.removeEventListener('click', this.closeContext);
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
      }
    },
    methods: {
      ...mapMutations({
        selectProject: 'mod_project/selectProject',
        addModelFromLocalDataMutation: 'mod_workspace/add_model_from_local_data',
        loadProjectFromLocalStorage: 'mod_workspace/get_workspacesFromLocalStorage',
        set_currentNetwork : 'mod_workspace/set_currentNetwork',
      }),
      ...mapActions({
        setActivePageAction: 'modal_pages/setActivePageAction',
        closePageAction: 'modal_pages/closePageAction',
        getProjects:    'mod_project/getProjects',
        createProject:    'mod_project/createProject',
        createLocalProjectFolder: 'mod_api/API_createFolder',
        API_getModelAction: 'mod_api/API_getModel',
        deleteProjectAction: 'mod_project/deleteProject',
        updateProjectAction: 'mod_project/updateProject',
      }),
      onProjectSelectHandler(project) {
        const {project_id: projectId} = project;

        this.selectProject(projectId);
        this.closePageAction();
        // this.setPageTitleMutation(`${project.name} / Models`);

        this.loadProjectFromLocalStorage(projectId);
        this.set_currentNetwork(0);
        // project.models.map(modelId => {
          
        //   // @todo extract models from local storage
        //   // make mutation for set the models in store
          
        //   this.API_getModelAction({modelId, projectId})
        //     .then(model => {
        //       this.addModelFromLocalDataMutation(model)
        //     }).catch(e => {
        //       console.log(e);
        //     })
        // })

        this.$router.push({name: 'projects'})
      },
      openProjectNameModal() {
        this.isProjectNameModalOpen = true;
      },
       closeProjectNameModal() {
        this.isProjectNameModalOpen = false;
        this.newProjectName = '';
      },
      createNewProject(projectName) {
        if(this.newProjectName === '') {
          return;
        }

       let payload = {
         name: this.newProjectName,
       };
      
       this.createProject(payload)
        .then(res => {
          this.onProjectSelectHandler(res);
          const projectName = `project_${res.project_id}`; 
          // this.createLocalProjectFolder(projectName);
        })
        this.isProjectNameModalOpen = false;
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
          this.$store.dispatch('globalView/GP_infoPopup', "Only project without modules can be deleted");
          return;
        }

        this.deleteProjectAction({ projectId: contextTargetProject })
          .then(response => {
            console.log(response);
          })
          .catch(e => console.log(e));


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
    background: #1C1C1E;
    border: 1px solid #363E51;
    box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
    border-radius: 2px;
    display: flex;
    flex-direction: column;
    z-index: 12;
    padding: 5px 8px;

    background: #131B30;
    border: 1px solid #363E51;
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
    background-color: transparent;
  }
  .project-box {
    min-width: 680px;
    min-height: 500px;

    background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
    border: 1px solid rgba(97, 133, 238, 0.4);
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
    width: 55%;
  
    
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
    margin-bottom: 16px;
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
    color: #FFFFFF;
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
    color: #FFFFFF;
    &.disabled {
      opacity: 0.5;
    }
    &.create {
      margin-left: 10px;
      background: #6185EE;
    }
  }
</style>