<template lang="pug">
  .page-projects
    aside.page-projects_sidebar
      include ./sidebar/sidebar.pug
    .page-projects_basic-templates
      include ./basic-templates/basic-templates.pug
      router-link.btn.btn--outline-blue-rev.projects-templates_link(
        v-if="networkIsNotEmpty"
        :to="{name: 'app'}")
        span Back to Workspace
        i.icon.icon-shevron-right
    main.page-projects_recent-files
      include ./recent-files/recent-files.pug
    file-picker-popup(
      v-if="showFilePickerPopup"
      popupTitle="Load Project Folder"
      :confirmCallback="confirmCallback"
    )
</template>
<script>
  import {filePCRead, folderPCDelete, deepCopy, projectPathModel}  from '@/core/helpers.js'
  import {mapState, mapGetters, mapMutations, mapActions} from 'vuex';
  import FilePickerPopup        from "@/components/global-popups/file-picker-popup.vue";

  import imageClassification    from '@/core/basic-template/image-classification.js'
  import reinforcementLearning  from '@/core/basic-template/reinforcement-learning.js'
  import timeseriesRegression   from '@/core/basic-template/timeseries-regression.js'

  export default {
    name: 'PageProjects',
    created() {
      this.$store.dispatch('mod_workspace/GET_workspacesFromLocalStorage');
    },
    mounted() {
      this.checkCloudToken()
    },
    data() {
      return {
        source: 'computer',
        service: '',
        search: '',
        projects: [],
        basicTemplates: [
          {
            title: 'Image Classification',
            imgPath: './static/img/project-page/image-classification.svg',
            template: imageClassification
          },
          {
            title: 'Timeseries Regression',
            imgPath: './static/img/project-page/time-series-regression.svg',
            template: timeseriesRegression
          },
          {
            title: 'Reinforcement Learning',
            imgPath: './static/img/project-page/reinforcement-learning.svg',
            template: reinforcementLearning
          },
        ]
      }
    },
    components: {
      FilePickerPopup
    },
    computed: {
      ...mapGetters({
        networkIsNotEmpty:  'mod_workspace/GET_networkIsNotEmpty',
        localUserInfo:      'mod_user/GET_LOCAL_userInfo'
      }),
      ...mapState({
        appVersion:          state => state.globalView.appVersion,
        hotKeyPressDelete:   state => state.mod_events.globalPressKey.del,
        showFilePickerPopup: state => state.globalView.globalPopup.showFilePickerPopup
      }),
      filteredProjects() {
        this.selectedProject = null;
        return this.projects.filter((project)=> project.name.match(this.search))
      }
    },
    watch: {
      'localUserInfo.projectsList.length': {
        handler() {
          if(!this.localUserInfo) return;

          let localProjectsList = deepCopy(this.localUserInfo.projectsList);
          if (Array.isArray(localProjectsList)) {
            localProjectsList.forEach((el) => {
              el.notExist = false;
              el.isChecked = false;
              filePCRead(projectPathModel(el.pathProject))
                .then(() => { })
                .catch((err) => {
                  el.notExist = true
                })
            });
            this.projects = localProjectsList;
          }
        },
        immediate: true
      },
      hotKeyPressDelete() {
        const indexCheckedProj = this.projects.findIndex((el)=> el.isChecked === true);
        if(indexCheckedProj < 0) return;

        const selectedProject = this.projects[indexCheckedProj];
        //const isProjectNotExist = selectedProject.notExist;
        const pathDelete = selectedProject.pathProject;
        folderPCDelete(pathDelete)
          .then(()=> {
            const newProjectsList = deepCopy(this.localUserInfo.projectsList);
            newProjectsList.splice(indexCheckedProj, 1);
            this.saveLocalUserInfo({key: 'projectsList', data: newProjectsList });
            this.$nextTick(()=> this.showInfoPopup("The project has been successfully deleted"))
          })
          .catch ((err)=> {console.error(err)})
      }
    },
    methods: {
      ...mapMutations({
        setTutorialMode:      'mod_tutorials/SET_isTutorialMode',
        setTutorialStoryBoard:'mod_tutorials/SET_showTutorialStoryBoard',
        restore_network:      'mod_workspace/RESTORE_network',
      }),
      ...mapActions({
        openNetwork:      'mod_events/EVENT_openNetwork',
        loadNetwork:      'mod_events/EVENT_loadNetwork',
        beginTutorial:    'mod_tutorials/START_storyboard',
        addNetwork:       'mod_workspace/ADD_network',
        saveLocalUserInfo:'mod_user/UPDATE_LOCAL_userInfo',
        showInfoPopup:    'globalView/GP_infoPopup',
        checkCloudToken:  'mod_apiCloud/CloudAPI_checkStatus',
      }),
      loadFolderPath() {
        this.$store.commit("globalView/set_filePickerPopup", true);
      },
      confirmCallback(el) {
        this.openTemplate(el[0]);
        this.$store.commit("globalView/HIDE_allGlobalPopups");
      },
      openTemplate(path) {
        this.loadNetwork(path)
      },
      selectTemplate(selectEl) {
        this.projects.forEach((el)=> el.isChecked = false);
        selectEl.isChecked = true
      },
      addNewProject() {
        this.addNetwork()
      },
      openBasicTemplate(net) {
        this.addNetwork(net.network)
      },
      openLastWS() {
        this.restore_network(this.localUserInfo.workspace);
        this.goNextPage()
      },
      goNextPage() {
        this.$router.push({name: 'app'});
      },
    }
  }
</script>
<style lang="scss" scoped>
  @import '../../scss/base';

  $section-indent: 6rem;

  @import './sidebar/sidebar';
  @import './basic-templates/basic-templates';
  @import './recent-files/recent-files';


  .page-projects {
    display: grid;
    background: $bg-workspace;
    grid-template-columns: $w-sidebar 1fr;
    grid-template-rows: auto 1fr;
    grid-template-areas: "sidebar basic-templates"
                        "sidebar recent-files";
  }

  .page-projects_sidebar {
    grid-area: sidebar;
    padding: 2rem 1rem 1rem 1rem;
    background: $col-txt2;
    h3 {
      margin: 2rem 0;
    }
  }
  .projects-sidebar_link {
    font-size: 1.4rem;
    width: 15rem;
    margin-bottom: 2rem;
    text-align: center;
    font-weight: normal;
    > * {
      vertical-align: middle;
    }
  }
  .page-projects_basic-templates {
    grid-area: basic-templates;
    display: flex;
    border-bottom: 1px solid $colorGrey;
    margin: 0 $section-indent;
    padding: $section-indent 0;
    position: relative;
  }
  .projects-templates_link {
    position: absolute;
    right: 0;
    top: 1rem;
  }
  .page-projects_recent-files {
    grid-area: recent-files;
    padding: $section-indent $section-indent $section-indent/2 $section-indent;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    width: 100%;
  }

  .page-projects_title {
    margin-bottom: $section-indent;
    display: flex;
    align-items: center;
    justify-content: space-between;
    &.get-started-title-margin {
     margin-bottom: 7rem;
    }
    h2 {
      display: flex;
      align-items: center;
      text-transform: uppercase;
      font-weight: 500;
      font-size: 1.8rem;
      margin-bottom: 0;
    }

    .title-box_projectscount {
      font-size: 1.2rem;
      margin-left: 1rem;
    }
  }
  .page-projects_project-list {
    flex: 1 1 100%;
    overflow: auto;
    margin-right: -1.4rem;
  }
</style>
