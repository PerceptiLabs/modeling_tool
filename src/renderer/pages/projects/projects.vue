<template lang="pug">
  .page-projects
    aside.page-projects_sidebar
      include ./sidebar/sidebar.pug
    .page-projects_basic-templates
      include ./basic-templates/basic-templates.pug
    main.page-projects_recent-files
      include ./recent-files/recent-files.pug

</template>
<script>
  import {loadNetwork} from '@/core/helpers.js'

  export default {
    name: 'PageProjects',
    data() {
      return {
        source: 'computer',
        service: '',
        search: '',
        basicTemplats: [
          {
            title: 'Image Classification',
            imgPath: './static/imgs/imageClassification.svg',
            netPath: ['.\\src\\renderer\\pages\\projects\\test02.json']
          },
          {
            title: 'Timeseries Regression',
            imgPath: './static/imgs/timeSeriesRegression.svg',
            netPath: ['.\\src\\renderer\\pages\\projects\\test02.json']
          },
          {
            title: 'Reinforcement Learning',
            imgPath: './static/imgs/reinforcementLearning.svg',
            netPath: ['.\\src\\renderer\\pages\\projects\\test02.json']
          },
        ],
        projects: [
          {
            id: 1,
            name: 'Quantum net (Project_1)',
            icon: 'icon-cloud', //icon-computer
            trained: true, //true
            time: '25.12.2018 20:24',
            scheme: ''
          },
        ],
      }
    },
    computed: {
      appVersion() {
        return this.$store.state.globalView.appVersion
      },
      filteredProjects() {
        return this.projects.filter((project) => {
          return project.name.match(this.search);
        })
      }
    },
    methods: {
      loadNetwork,
      openProject() {
        this.$router.push({name: 'app'});
      },
      addProject() {
        this.$router.push({name: 'app'});
      },
      openTemplateModel(path) {
        this.$router.push({name: 'app'});
        this.loadNetwork(path);
      }
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
    grid-template-areas: "sidebar basic-templates" "sidebar recent-files";
  }

  .page-projects_sidebar {
    grid-area: sidebar;
    padding: $section-indent 1rem 1rem 1rem;
    background: $col-txt2;
    h3 {
      margin: 2rem 0;
    }
  }

  .page-projects_basic-templates {
    grid-area: basic-templates;
    display: flex;
    border-bottom: 1px solid $colorGrey;
    margin: 0 $section-indent;
    padding: $section-indent 0;
  }

  .page-projects_recent-files {
    grid-area: recent-files;
    padding: $section-indent;
    overflow: auto;
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

</style>


