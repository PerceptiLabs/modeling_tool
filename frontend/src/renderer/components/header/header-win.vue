<template lang="pug">
  header.app-header
    .app-header_logo
      a(@click="toProjectPage")
        //-img(src="./../../../../static/img/PerceptiLabs_Logo-web-white_beta-01.svg" alt="PerceptiLabs logo")
        img(src="./../../../../static/img/project-page/logo.svg" alt="PerceptiLabs logo")
    the-menu
    
    h4(v-if="projectName").page-title {{projectName}} / <span class="page-route-title">{{routeHeaderAlias}} </span>
    header-profile
    ul(v-if="!isWeb").app-header_actions
      button.btn.btn--app-minify(type="button" @click="appMinimize()").i.icon.icon-app-minimize
      button.btn.btn--app-full(type="button"
        @click="appMaximize"
        :class="{'icon-app-restore-down': showRestoreIcon, 'icon-app-resize': !showRestoreIcon}").i.icon
      button.btn.btn--app-close(type="button" @click="appClose()").i.icon.icon-app-close
</template>

<script>
  import TheMenu from '@/components/the-menu.vue'
  import {isWeb} from "@/core/helpers";
  import HeaderProfile from "@/components/header/header-profile";


export default {
  name: "HeaderWin",
  components: {HeaderProfile, TheMenu},
  data: function() {
    return {
      isWeb: isWeb(),
    }
  },
  computed: {
    showRestoreIcon() {
      return this.$store.state.globalView.appIsFullView
    },
    pageTitle() {
      return this.$store.state.globalView.pageTitle;
    },
    currentProject() {
      return this.$store.state.mod_project.currentProject;
    },
    projectsList() {
      return this.$store.state.mod_project.projectsList;
    },
    projectName() {
      const { currentProject, projectsList } = this;
      if(!currentProject) return '';
      let project = projectsList.filter(project => project.project_id === currentProject)[0];
      return project ? project.name : ''
    },
    routeHeaderAlias() {
      let theName = '';
      switch(this.$route.name) {
        case 'projects': theName = 'ModelHub'; break;
        case 'app': theName = 'Modeling Tool'; break;
      }
      return theName;
    }
  },
  methods: {
    appClose() {
      this.$emit('app-closed')
    },
    appMinimize() {
      this.$emit('app-minimized')
    },
    appMaximize() {
      this.$emit('app-maximized')
    },
    toProjectPage() {
      if(this.$route.name === 'app') {
        this.$router.push({name: 'projects'})
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .app-header {
    position: relative;
    display: flex;
    align-items: center;
    height: $h-header-win;
    background: #363E50;
    font-family: sans-serif;
    background: rgba(97, 133, 238, 0.2);
    border: 1px solid rgba(97, 133, 238, 0.4);
    box-sizing: border-box;
    border-radius: 0px;
  }
  .d-none {
    display: none;
  }
  .app-header_logo {
    margin: 0 12px 0 5px;
    cursor: pointer;
    a {
      display: block;
      -webkit-app-region: no-drag;
    }
  }
  .page-title {
    @include absolute-center();
    color: #C4C4C4;
    font-family: 'Nunito Sans';
    font-style: normal;
    font-weight: normal;
    font-size: 16px;
    line-height: 22px;
    color: #CDD8F8;
    span {
      // color: #fff;
    }
  }
  .page-route-title {
    color: #B6C7FB ;
    font-weight: bold;
  }

  .app-header_actions {
    display: flex;
    margin-left: auto;
    .btn {
      font-size: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 46px;
      height: $h-header-win;
      border-radius: 0;
      &:hover {
        background: #545353;
      }
    }
    .btn--app-close {
      &:hover {
        background: #e94040;
      }
    }
  }
</style>
