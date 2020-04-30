<template lang="pug">
  .project-wrapper
    .projectContext(v-if="isContextOpened" :style="projectContextStyles")
      button(@click="renameProject") Rename
      button(@click="deleteProject()") Delete
    .project-box
      .header Projects
      .content
        .sidebar
          button.project-list-filter-button.is-active Local Projects
          button.project-list-filter-button Cloud Projects
        .main
          .main-header
            button.btn-icon
              img(src="../../../../static/img/project-page/import.svg")
            button.btn-icon.rounded-border(@click="createNewProject")
              img(src="../../../../static/img/plus.svg")
            div.search-input
              img(src="../../../../static/img/search-input.svg")
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
        renameData: {
          isProjectFieldActive: false,
          projectFieldValue: '',
          projectId: null,
        }
      }
    },
    created() {
      // this.setActivePageAction()
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
        setPageTitleMutation: 'globalView/setPageTitleMutation',
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
        this.setPageTitleMutation(`${project.name} / Models`);

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
      createNewProject() {
       let payload = {
         name: 'New project ' + Date.now().toString(),
       };
      
       this.createProject(payload)
        .then(res => {
          this.onProjectSelectHandler(res);
          const projectName = `project_${res.project_id}`; 
          // this.createLocalProjectFolder(projectName);
        })
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
        
        // debugger;
        this.deleteProjectAction({ projectId: contextTargetProject })
          .then(response => {
            console.log(response);
            debugger;
          })
          .catch(e => console.log(e));


      },
      renameProject() {
    
        const { contextTargetProject } = this;
        const theProject = this.projectsList.filter(project => project.project_id === contextTargetProject)[0];



          this.renameData.isProjectFieldActive = true;
          this.renameData.projectFieldValue = theProject.name;
          this.renameData.projectId = theProject.project_id;
        debugger;
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
    button {
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
    background: #1C1C1E;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
    border-radius: 2px;
  }
  .header {
    background: #363E50;
    border-radius: 2px 2px 0 0;
    height: 38px;
    width: 687px;
    font-size: 14px;
    line-height: 38px;
    text-align: center;
  }
  .content {
    display: flex;
    padding: 23px 0;
  }
  /* Sidebar */
  .sidebar {
    width: 30%;
    padding-left: 29px;
    margin-right: 30px;
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
    padding-left: 15px;
    display: block;
    background-color: transparent;
    border-left: 3px solid transparent;
    font-size: 16px;
    height: 29px;
    margin-bottom: 16px;
    &.is-active {
      border-left: 3px solid #fff;
     }
  }
  /* main */
  .main {
    width: 70%;
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
      border: 1px solid #363E51;
      border-radius: 5px;
      height: 29px;
      font-size: 16px;
    }
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
  }
  .fz-16 {
    font-size: 16px;
  }
  .btn-icon {
    background: none;
    &.rounded-border {
      border: 1px solid #fff;
      border-radius: 50%;
      padding: 3px;
      line-height: 100%;
    }
  }
  .rename-project-input {
    width: 260px;
  }
</style>