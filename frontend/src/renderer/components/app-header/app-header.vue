<template lang="pug">
  header.app-header
    .app-header-section.app-header-left
      .app-header_logo
        img(src="./../../../../static/img/project-page/logo.svg" alt="PerceptiLabs logo")
      the-menu
    
    .app-header-section.app-header-mid
      div(v-if="isOnTestPage").test-menu-header
        router-link.test-menu-item(to="test-create") Create test
        router-link.test-menu-item(to='test-dashboard') Dashboard
      h4(v-else-if="projectName").page-title <span class="page-route-title">{{routeHeaderAlias}} </span>
      //- h4(v-if="projectName").page-title {{projectName}} / <span class="page-route-title">{{routeHeaderAlias}} </span>

    .app-header-section.app-header-right

      .help-button(
        @click="toggleHelp(!showHelpPanel)"
        @blur="toggleHelp(false)"
        tabindex="0"
        )
        svg(
          :data-tutorial-target="'tutorial-model-hub-question-mark'" width="25" height="25" viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg"
        )
          circle(cx="12.5" cy="12.5" r="12" stroke="#5E6F9F")
          path(d="M11.9053 15.4473C11.9053 14.7113 11.9966 14.1247 12.1792 13.6875C12.3618 13.2503 12.7215 12.7716 13.2583 12.2515C13.8006 11.7257 14.1437 11.3522 14.2876 11.1309C14.509 10.7933 14.6196 10.4281 14.6196 10.0352C14.6196 9.51497 14.4896 9.1193 14.2295 8.84814C13.9749 8.57145 13.5986 8.43311 13.1006 8.43311C12.6247 8.43311 12.2401 8.56868 11.9468 8.83984C11.659 9.10547 11.5151 9.46794 11.5151 9.92725H9.49805C9.50911 8.94775 9.84115 8.17301 10.4941 7.60303C11.1527 7.03304 12.0215 6.74805 13.1006 6.74805C14.2129 6.74805 15.0789 7.03027 15.6987 7.59473C16.3241 8.15918 16.6367 8.94775 16.6367 9.96045C16.6367 10.8625 16.2161 11.7507 15.375 12.625L14.354 13.6294C13.9888 14.0444 13.8006 14.6504 13.7896 15.4473H11.9053ZM11.7642 18.0288C11.7642 17.7023 11.8665 17.4395 12.0713 17.2402C12.276 17.0355 12.5527 16.9331 12.9014 16.9331C13.2555 16.9331 13.535 17.0382 13.7397 17.2485C13.9445 17.4533 14.0469 17.7134 14.0469 18.0288C14.0469 18.3332 13.9473 18.5877 13.748 18.7925C13.5488 18.9972 13.2666 19.0996 12.9014 19.0996C12.5361 19.0996 12.2539 18.9972 12.0547 18.7925C11.861 18.5877 11.7642 18.3332 11.7642 18.0288Z" fill="#B6C7FB")

        .help-button-panel(v-if="showHelpPanel")
          .help-button-panel-content
            .help-button-panel-content-item(@click="toggleTutorialTips") {{ hideTipsDisplayText }}
            .help-button-panel-content-item(@click="onActivateChecklist") Get started checklist
            .help-button-panel-content-item(@click="goToWhatsNew") What's new
            .help-button-panel-content-item(@click="openVideoTutorials") 
              span Video tutorials
              svg(width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M10.875 10.875H2.125V2.125H6.5V0.875H2.125C1.43125 0.875 0.875 1.4375 0.875 2.125V10.875C0.875 11.5625 1.43125 12.125 2.125 12.125H10.875C11.5625 12.125 12.125 11.5625 12.125 10.875V6.5H10.875V10.875ZM7.75 0.875V2.125H9.99375L3.85 8.26875L4.73125 9.15L10.875 3.00625V5.25H12.125V0.875H7.75Z" fill="white")
            .help-button-panel-content-item(@click="goToDocumentation") 
              span Documentation
              svg(width="13" height="13" viewBox="0 0 13 13" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M10.875 10.875H2.125V2.125H6.5V0.875H2.125C1.43125 0.875 0.875 1.4375 0.875 2.125V10.875C0.875 11.5625 1.43125 12.125 2.125 12.125H10.875C11.5625 12.125 12.125 11.5625 12.125 10.875V6.5H10.875V10.875ZM7.75 0.875V2.125H9.99375L3.85 8.26875L4.73125 9.15L10.875 3.00625V5.25H12.125V0.875H7.75Z" fill="white")

      button.btn.btn--dark.btn--toolbar-settings(
          type="button"
          @click="goToReport"
          :data-tutorial-target="'tutorial-model-hub-report-button'"
          data-testing-target="report-modal-btn"
        )
        img(v-if="isLoading" src="static/img/spinner.gif" width="12px" style="margin-right: 5px")
        span(v-if="!isLoading") Report
        i.icon.icon-bug-report(v-if="!isLoading")
      header-profile(v-if="showProfile")
</template>

<script>
  import TheMenu from '@/components/the-menu.vue'
  import HeaderProfile from "@/components/app-header/header-profile";
  import { mapGetters, mapActions } from 'vuex';
  import { MODAL_PAGE_WHATS_NEW, PERCEPTILABS_DOCUMENTATION_URL, PERCEPTILABS_VIDEO_TUTORIAL_URL } from "@/core/constants";
  import { fileserverAvailability } from '@/core/apiFileserver';

export default {
  name: "HeaderWin",
  components: {HeaderProfile, TheMenu},
  data: function() {
    return {
      showHelpPanel: false,
      showProfile: !process.env.NO_KC,
      MODAL_PAGE_WHATS_NEW,
      isLoading: false
    }
  },
  computed: {
    ...mapGetters({
      currentViewType: 'mod_workspace/GET_viewType',
      currentModel:    'mod_workspace/GET_currentNetwork',
      showTips:        'mod_tutorials/getShowTutorialTips',
    }),
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
    isOnTestPage() {
      return this.$route.name === 'test-create' || this.$route.name === 'test-dashboard';
    },
    routeHeaderAlias() {
      let theName = '';
      switch(this.$route.name) {
        case 'main-page': theName = 'Model Hub'; break;
        case 'projects': theName = 'Model Hub'; break;
        case 'settings': theName = 'Settings'; break;
        case 'app':  {
          if(this.currentViewType==='statistic') {
            theName = 'Statistics View';
          } else if(this.currentViewType==='model') {
            theName = 'Modeling Tool';
          } else {
            theName = 'Test View';
          }
        } break;
      }
      return theName;
    },
    hideTipsDisplayText() {
      if (this.showTips) {
        return 'Disable tips';
      } else {
        return 'Enable tips';
      }
    }
  },
  methods: {
    ...mapActions({
      setNextStep:          'mod_tutorials/setNextStep',
      setCurrentView:       'mod_tutorials/setCurrentView',
      activateChecklist:    'mod_tutorials/activateChecklist',
      setShowChecklist:     'mod_tutorials/setShowChecklist',
      setTips:              'mod_tutorials/setTutorialNotificationsState',
      trackHelpOption:      'mod_tracker/TRACK_helpOption',
      setActivePageAction:  'modal_pages/setActivePageAction',
      openErrorPopup:       'globalView/GP_infoPopup',
    }),
    setLoading(value) {
      this.isLoading = value;
    },
    toProjectPage() {
      if(this.$route.name === 'app') {
        this.setCurrentView('tutorial-model-hub-view');
        this.$router.push({name: 'projects'})
      }
    },
    goToReport() {
      this.setLoading(true);
      fileserverAvailability().then(response => {
        this.setLoading(false);
        if (response === "AVAILABLE") {
          this.$store.dispatch('globalView/SET_createIssuesPopup', true);
        } else {
          this.openErrorPopup("It seems PerceptiLabs Backend is not running so this feature can't be used. If you need support or want to manually report a bug you can visit <a style='color: #B6C7FB' href='https://forum.perceptilabs.com' target='_blank'>forum.perceptilabs.com</a>");
        }
      });
    },
    toggleHelp(value = null) {
      this.showHelpPanel = !!value;
    },
    toggleTutorialTips() {
      this.setTips(!this.showTips);
      this.trackHelpOption('Toggle tutorial tips');
    },
    onActivateChecklist() {
      this.setShowChecklist();
      this.activateChecklist();
      this.trackHelpOption('Activate checklist');
    },
    goToWhatsNew() {
      this.setActivePageAction(MODAL_PAGE_WHATS_NEW);
      this.trackHelpOption('Go to Whats New');
    },
    openVideoTutorials() {
      this.trackHelpOption('Go to Video Tutorials');
      window.open(PERCEPTILABS_VIDEO_TUTORIAL_URL, '_blank');
    },
    goToDocumentation() {
      this.trackHelpOption('Go to Documentation');
      window.open(PERCEPTILABS_DOCUMENTATION_URL, '_blank');
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .app-header {
    z-index: 101;
    position: relative;
    display: flex;
    height: $h-header-win;
    background: #363E50;
    // font-family: sans-serif;
    background: #141c31;
    border: 1px solid rgba(97, 133, 238, 0.4);
    box-sizing: border-box;
    border-radius: 0px;
  }

  .app-header-section {
    display: flex;
    flex: 1 1 100%;
    align-items: center;

    &.app-header-right {
      > *:first-child {
        margin-left: auto;
      }

      > *:last-child {
        margin-right: 4rem;
      }

      * + * {
        margin-left: 1rem;
      }
    }
  }

  .d-none {
    display: none;
  }
  .app-header_logo {
    margin: 0 12px 0 5px;
    // cursor: pointer;
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

  .btn--toolbar-settings {
    min-width: 0;
    color: $toolbar-button-border;
    background: #141c31;
    width: 81px;
    height: 30px;

    padding-right: 1rem;
    padding-left: 1rem;
    border: 1px solid $toolbar-separator-color;

    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 600;
    font-size: 12px;

    &.active {
      color: $color-1;
      border: 1px solid $color-1;

      & > .ring-icon {
        border: 2px solid $color-1;
      }
    }

  }

  .help-button {
    position: relative;

    .help-button-panel {
      // transform-origin: top right;
      position: absolute;
      top: 3rem;
      right: 0;

      background: #131B30;
      border: 1px solid #363E51;
      box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);
      border-radius: 2px;

      width: 16rem;

      margin-left: 0;

      .help-button-panel-content {
        
        height: 100%; 

        display: flex;
        flex-direction: column;
        justify-content: space-between;
        
        padding: 1.5rem 1rem;

        > .help-button-panel-content-item {
          margin: 0;
          font-family: Nunito Sans;
          font-style: normal;
          font-weight: normal;
          font-size: 14px;
          line-height: 19px;
          color: #FFFFFF;

          cursor: pointer;

        }

        > .help-button-panel-content-item + .help-button-panel-content-item {
          margin-top: 1rem;
        }
      }
    }
  }
  .test-menu-header {
    width: 100%;
    display: flex;
    justify-content: center;
  }
  .test-menu-item {
    margin: 0 15px;
    padding: 5px 0;
    font-size: 14px;
    font-weight: bold;
    color: #fff;
    
    position: relative;
    &.router-link-active {
      
      color: #B6C7FB;
      &:after {
        content: '';
        position: absolute;
        height: 1px;
        width: 100%;
        background-color: #B6C7FB;
        bottom: 0;
        left: 0;
      }
    }
  }
</style>
