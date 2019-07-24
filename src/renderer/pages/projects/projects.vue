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

</template>
<script>
  import fs               from 'fs';
  import {readLocalFile}  from '@/core/helpers.js'
  import {mapMutations, mapActions} from 'vuex';

  import basicTemplate1 from '@/core/basic-template/base-template-1.js'

  export default {
    name: 'PageProjects',
    mounted() {
      let localProjectsList = JSON.parse(localStorage.getItem('projectsList'));
      if(Array.isArray(localProjectsList)) {
        localProjectsList.forEach((el)=> {
          this.readLocalFile(el.path[0])
            .then(() => {})
            .catch((err)=> {
              el.notExist = true
            })
        });
        this.projects = localProjectsList;
      }
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
            imgPath: './static/img/imageClassification.svg',
            template: basicTemplate1
          },
          {
            title: 'Timeseries Regression',
            imgPath: './static/img/timeSeriesRegression.svg',
            template: basicTemplate1
          },
          {
            title: 'Reinforcement Learning',
            imgPath: './static/img/reinforcementLearning.svg',
            template: basicTemplate1
          },
        ]
      }
    },
    computed: {
      appVersion() {
        return this.$store.state.globalView.appVersion
      },
      filteredProjects() {
        this.selectedProject = null;
        return this.projects.filter((project) => project.name.match(this.search))
      },
      networkIsNotEmpty(){
        return this.$store.getters['mod_workspace/GET_networkIsNotEmpty'];
      },
      hotKeyPressDelete() {
        return this.$store.state.mod_events.globalPressKey.del
      },
    },
    watch: {
      hotKeyPressDelete() {
        //console.log('hotKeyPressDelete');
        let indexCheckedProj = this.projects.findIndex((el)=> el.isChecked === true);
        if(indexCheckedProj >= 0) {
          let pathDelete = this.projects[indexCheckedProj].path[0];
          fs.unlink(pathDelete, ()=> {
            this.projects.splice(indexCheckedProj, 1);
            localStorage.setItem('projectsList', JSON.stringify(this.projects));
            this.$nextTick(()=> this.$store.dispatch('globalView/GP_infoPopup', "The project has been successfully deleted"))
          })
        }
      }
    },
    methods: {
      ...mapMutations({
        setTutorialMode:        'mod_tutorials/SET_isTutorialMode',
        setTutorialStoryBoard:  'mod_tutorials/SET_showTutorialStoryBoard',
      }),
      ...mapActions({
        openNetwork: 'mod_events/EVENT_openNetwork',
        loadNetwork: 'mod_events/EVENT_loadNetwork',
        beginTutorial: 'mod_tutorials/START_storyboard',
        addNetwork: 'mod_workspace/ADD_network'
      }),
      readLocalFile,
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
      goNextPage() {
        this.$router.push({name: 'app'});
      },
    }
  }
</script>
<style lang="scss" scoped>
  @import '../../scss/base';

  $section-indent: 5rem;

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
    padding: $section-indent 1rem 1rem 1rem;
    background: $col-txt2;
    h3 {
      margin: 2rem 0;
    }
  }
  .projects-sidebar_link {
    font-size: 1.6rem;
    display: block;
    width: 100%;
    margin-bottom: 4rem;
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
