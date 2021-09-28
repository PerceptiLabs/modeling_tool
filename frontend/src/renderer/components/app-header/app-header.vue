<template lang="pug">
  header.app-header
    .app-header-section.app-header-left
      .app-header_logo
        img(src="./../../../../static/img/project-page/logo.svg" alt="PerceptiLabs logo")
      div.app-title.bold PerceptiLabs

    
    .app-header-section.app-header-mid
      //- h4(v-if="projectName").page-title <span class="page-route-title">{{routeHeaderAlias}} </span>
      //- h4(v-if="projectName").page-title {{projectName}} / <span class="page-route-title">{{routeHeaderAlias}} </span>
      the-menu(v-show="false")
    .app-header-section.app-header-right
      .help-button        
        base-switch-theme.switch-theme(:value="isThemeLight" :onClick="toggleTheme")
      .help-button(
        @click="onToggleIntercom"
        tabindex="0"
        )        

        svg(width="20" height="18" viewBox="0 0 20 18" fill="none" xmlns="http://www.w3.org/2000/svg")
          path(fill-rule="evenodd" clip-rule="evenodd" d="M0 2.52157C0 1.85281 0.263392 1.21144 0.732233 0.738551C1.20107 0.265665 1.83696 0 2.5 0H17.5C18.163 0 18.7989 0.265665 19.2678 0.738551C19.7366 1.21144 20 1.85281 20 2.52157V12.6078C20 13.2766 19.7366 13.918 19.2678 14.3909C18.7989 14.8638 18.163 15.1294 17.5 15.1294H5.5175C5.18601 15.1295 4.86812 15.2624 4.63375 15.4988L1.0675 17.4148C0.980163 17.5031 0.868814 17.5633 0.747545 17.5878C0.626276 17.6122 0.50054 17.5998 0.386249 17.5522C0.271959 17.5045 0.174252 17.4238 0.105497 17.3201C0.0367407 17.2164 2.62686e-05 17.0945 0 16.9697V2.52157ZM4.375 3.78235C4.20924 3.78235 4.05027 3.84877 3.93306 3.96699C3.81585 4.08521 3.75 4.24556 3.75 4.41275C3.75 4.57994 3.81585 4.74028 3.93306 4.8585C4.05027 4.97672 4.20924 5.04314 4.375 5.04314H15.625C15.7908 5.04314 15.9497 4.97672 16.0669 4.8585C16.1842 4.74028 16.25 4.57994 16.25 4.41275C16.25 4.24556 16.1842 4.08521 16.0669 3.96699C15.9497 3.84877 15.7908 3.78235 15.625 3.78235H4.375ZM4.375 6.93432C4.20924 6.93432 4.05027 7.00073 3.93306 7.11895C3.81585 7.23717 3.75 7.39752 3.75 7.56471C3.75 7.7319 3.81585 7.89224 3.93306 8.01046C4.05027 8.12868 4.20924 8.1951 4.375 8.1951H15.625C15.7908 8.1951 15.9497 8.12868 16.0669 8.01046C16.1842 7.89224 16.25 7.7319 16.25 7.56471C16.25 7.39752 16.1842 7.23717 16.0669 7.11895C15.9497 7.00073 15.7908 6.93432 15.625 6.93432H4.375ZM4.375 10.0863C4.20924 10.0863 4.05027 10.1527 3.93306 10.2709C3.81585 10.3891 3.75 10.5495 3.75 10.7167C3.75 10.8839 3.81585 11.0442 3.93306 11.1624C4.05027 11.2806 4.20924 11.3471 4.375 11.3471H10.625C10.7908 11.3471 10.9497 11.2806 11.0669 11.1624C11.1842 11.0442 11.25 10.8839 11.25 10.7167C11.25 10.5495 11.1842 10.3891 11.0669 10.2709C10.9497 10.1527 10.7908 10.0863 10.625 10.0863H4.375Z" )

      .help-button(
          @click="goToReport"
          :data-tutorial-target="'tutorial-model-hub-report-button'"
          data-testing-target="report-modal-btn"
        )
        svg(width="15" height="21" viewBox="0 0 15 21" fill="none" xmlns="http://www.w3.org/2000/svg")
          path(d="M4.17847 0.486172C4.16091 0.401624 4.12962 0.322328 4.08649 0.253069C4.04336 0.183809 3.98927 0.12602 3.9275 0.0831879C3.86572 0.0403558 3.79754 0.0133682 3.72706 0.00385281C3.65658 -0.00566256 3.58526 0.00249161 3.51741 0.0278234C3.44956 0.0531551 3.38658 0.0951395 3.33228 0.151244C3.27797 0.207349 3.23346 0.276411 3.20143 0.354265C3.1694 0.432118 3.15052 0.51715 3.14592 0.604232C3.14132 0.691313 3.1511 0.778638 3.17467 0.860941L3.60517 2.60814C2.63998 3.81522 2.09981 5.44152 2.10157 7.1351H12.6016C12.6033 5.44152 12.0631 3.81522 11.098 2.60814L11.5285 0.860941C11.552 0.778638 11.5618 0.691313 11.5572 0.604232C11.5526 0.51715 11.5337 0.432118 11.5017 0.354265C11.4697 0.276411 11.4252 0.207349 11.3708 0.151244C11.3165 0.0951395 11.2536 0.0531551 11.1857 0.0278234C11.1179 0.00249161 11.0465 -0.00566256 10.9761 0.00385281C10.9056 0.0133682 10.8374 0.0403558 10.7756 0.0831879C10.7139 0.12602 10.6598 0.183809 10.6166 0.253069C10.5735 0.322328 10.5422 0.401624 10.5247 0.486172L10.2191 1.72162C9.36663 1.0359 8.36996 0.671631 7.35156 0.673557C6.33318 0.671706 5.33652 1.03597 4.48401 1.72162L4.17952 0.486172H4.17847Z")
          path(d="M12.6 7.1367V8.42901H7.875V20.0275C9.16998 19.8673 10.3705 19.1208 11.2435 17.9328C12.1166 16.7449 12.6 15.2001 12.6 13.5982H13.125C13.2642 13.5982 13.3978 13.6663 13.4962 13.7875C13.5947 13.9087 13.65 14.073 13.65 14.2444V14.8906C13.65 15.0619 13.7053 15.2263 13.8038 15.3475C13.9022 15.4686 14.0358 15.5367 14.175 15.5367C14.3142 15.5367 14.4478 15.4686 14.5462 15.3475C14.6447 15.2263 14.7 15.0619 14.7 14.8906V14.2444C14.7 13.7303 14.5341 13.2372 14.2387 12.8737C13.9433 12.5102 13.5427 12.3059 13.125 12.3059H12.6V11.0136H14.175C14.3142 11.0136 14.4478 10.9456 14.5462 10.8244C14.6447 10.7032 14.7 10.5388 14.7 10.3675C14.7 10.1961 14.6447 10.0318 14.5462 9.91057C14.4478 9.7894 14.3142 9.72132 14.175 9.72132H12.6V8.42901H13.125C13.5427 8.42901 13.9433 8.22478 14.2387 7.86125C14.5341 7.49772 14.7 7.00466 14.7 6.49055V5.8444C14.7 5.67303 14.6447 5.50867 14.5462 5.3875C14.4478 5.26632 14.3142 5.19824 14.175 5.19824C14.0358 5.19824 13.9022 5.26632 13.8038 5.3875C13.7053 5.50867 13.65 5.67303 13.65 5.8444V6.49055C13.65 6.66192 13.5947 6.82627 13.4962 6.94745C13.3978 7.06863 13.2642 7.1367 13.125 7.1367H12.6ZM6.825 20.0275V8.42901H2.1V7.1367H1.575C1.43576 7.1367 1.30223 7.06863 1.20377 6.94745C1.10531 6.82627 1.05 6.66192 1.05 6.49055V5.8444C1.05 5.67303 0.994688 5.50867 0.896231 5.3875C0.797774 5.26632 0.664239 5.19824 0.525 5.19824C0.385761 5.19824 0.252225 5.26632 0.153769 5.3875C0.0553123 5.50867 0 5.67303 0 5.8444V6.49055C0 7.00466 0.165937 7.49772 0.461307 7.86125C0.756677 8.22478 1.15728 8.42901 1.575 8.42901H2.1V9.72132H0.525C0.385761 9.72132 0.252225 9.7894 0.153769 9.91057C0.0553123 10.0318 0 10.1961 0 10.3675C0 10.5388 0.0553123 10.7032 0.153769 10.8244C0.252225 10.9456 0.385761 11.0136 0.525 11.0136H2.1V12.3059H1.575C1.15728 12.3059 0.756677 12.5102 0.461307 12.8737C0.165937 13.2372 0 13.7303 0 14.2444V14.8906C0 15.0619 0.0553123 15.2263 0.153769 15.3475C0.252225 15.4686 0.385761 15.5367 0.525 15.5367C0.664239 15.5367 0.797774 15.4686 0.896231 15.3475C0.994688 15.2263 1.05 15.0619 1.05 14.8906V14.2444C1.05 14.073 1.10531 13.9087 1.20377 13.7875C1.30223 13.6663 1.43576 13.5982 1.575 13.5982H2.1C2.09998 15.2001 2.5834 16.7449 3.45647 17.9328C4.32954 19.1208 5.53002 19.8673 6.825 20.0275Z")

      .help-button(
        @click="toggleHelp(!showHelpPanel)"
        @blur="toggleHelp(false)"
        tabindex="0"
        )
        svg(width="21" height="20" viewBox="0 0 21 20" fill="none" xmlns="http://www.w3.org/2000/svg")
          path(fill-rule="evenodd" clip-rule="evenodd" d="M20.7002 10C20.7002 12.6522 19.6466 15.1957 17.7713 17.0711C15.8959 18.9464 13.3524 20 10.7002 20C8.04803 20 5.50449 18.9464 3.62913 17.0711C1.75376 15.1957 0.700195 12.6522 0.700195 10C0.700195 7.34784 1.75376 4.8043 3.62913 2.92893C5.50449 1.05357 8.04803 0 10.7002 0C13.3524 0 15.8959 1.05357 17.7713 2.92893C19.6466 4.8043 20.7002 7.34784 20.7002 10ZM7.5702 7.54125C7.5299 7.5418 7.48992 7.53412 7.4527 7.51868C7.41548 7.50324 7.38179 7.48038 7.35371 7.45148C7.32563 7.42257 7.30374 7.38825 7.28938 7.3506C7.27502 7.31295 7.26849 7.27276 7.2702 7.2325C7.3877 5.11375 9.12145 4.375 10.7064 4.375C12.4514 4.375 14.0464 5.2875 14.0464 7.175C14.0464 8.525 13.2527 9.1675 12.4914 9.74625C11.5702 10.445 11.2289 10.7063 11.2289 11.6038V11.735C11.2289 11.8179 11.196 11.8974 11.1374 11.956C11.0788 12.0146 10.9993 12.0475 10.9164 12.0475H9.90394C9.82192 12.0475 9.74319 12.0153 9.68472 11.9577C9.62626 11.9002 9.59276 11.822 9.59144 11.74L9.58645 11.4688C9.53895 10.31 10.2052 9.59625 11.0464 8.985C11.7839 8.43 12.2527 8.065 12.2527 7.27125C12.2527 6.24 11.4677 5.81125 10.6102 5.81125C9.60645 5.81125 9.04395 6.40875 8.9327 7.22875C8.9102 7.4 8.7727 7.54125 8.6002 7.54125H7.56894H7.5702ZM10.4764 15.595C9.74645 15.595 9.21519 15.1025 9.21519 14.4362C9.21519 13.7463 9.74645 13.2613 10.4777 13.2613C11.2389 13.2613 11.7627 13.7463 11.7627 14.4362C11.7627 15.1025 11.2377 15.595 10.4764 15.595Z")


        .help-button-panel(v-if="showHelpPanel")
          .help-button-panel-content
            .help-button-panel-content-item(@click="startUserFlow") Get Started
            app-header-link(
              name="Tutorials"
              @handleClick="openVideoTutorials"
            )
            app-header-link(
              name="Documentation"
              @handleClick="goToDocumentation"
            )
            hr.help-button-panel-content-item
            .help-button-panel-content-item.cursor-default External resources
            app-header-link(
              name="YouTube"
              @handleClick="onOpenYouTube"
            )
            app-header-link(
              name="Slack"
              @handleClick="onOpenSlack"
            )
            app-header-link(
              name="Forum"
              @handleClick="onOpenForum"
            )
            app-header-link(
              name="Blog"
              @handleClick="onOpenBlogs"
            )

      header-profile(v-if="showProfile")
</template>

<script>
import TheMenu from '@/components/the-menu.vue';
import HeaderProfile from "@/components/app-header/header-profile.vue";
import AppHeaderLink from '@/components/app-header/app-header-link.vue';
import BaseSwitchTheme from '@/components/base/switch-theme.vue';
import userflow from "userflow.js";
import { mapGetters, mapActions, mapState, mapMutations } from 'vuex';
import {
  PERCEPTILABS_DOCUMENTATION_URL,
  PERCEPTILABS_YOUTUBE_VIDEO_TUTORIAL_URL,
  PERCEPTILABS_YOUTUBE_URL,
  PERCEPTILABS_SLACK_URL,
  PERCEPTILABS_FORUM_URL,
  PERCEPTILABS_BLOGS_URL,
  USER_FLOW_CONTENT_ID,
  THEME_LIGHT, 
  THEME_DARK
} from "@/core/constants";export default {
  name: "HeaderWin",
  components: {
    HeaderProfile,
    TheMenu,
    AppHeaderLink,
    BaseSwitchTheme
  },  data: function() {
    return {
      showHelpPanel: false,
      showProfile: !process.env.NO_KC,
    }
  },
  computed: {
    ...mapState({
      theme:              state => state.globalView.theme
    }),
    ...mapGetters({
      currentViewType: 'mod_workspace/GET_viewType',
    }),
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
        case 'main-page': theName = 'Model Hub'; break;
        case 'projects': theName = 'Model Hub'; break;
        case 'settings': theName = 'Settings'; break;
        case 'export': theName = 'Export'; break;
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
    isThemeLight() {
      return this.theme === THEME_LIGHT;
    }
  },
  methods: {
    ...mapMutations({
      set_theme: 'globalView/set_theme',
    }),
    ...mapActions({
      trackHelpOption: 'mod_tracker/TRACK_helpOption',
      trackQuestionMark: 'mod_tracker/TRACK_questionMark',
      trackIntercom: 'mod_tracker/TRACK_toggleIntercom',
    }),
    goToReport() {
      window.open(PERCEPTILABS_FORUM_URL);
    },
    toggleHelp(value = null) {
      this.showHelpPanel = !!value;
      if (value) {
        this.trackQuestionMark()
      }
    },
    openVideoTutorials() {
      this.trackHelpOption('Go to Video Tutorials');
      window.open(PERCEPTILABS_YOUTUBE_VIDEO_TUTORIAL_URL, '_blank');
    },
    goToDocumentation() {
      this.trackHelpOption('Go to Documentation');
      window.open(PERCEPTILABS_DOCUMENTATION_URL, '_blank');
    },
    onToggleIntercom() {
      if (this.$intercom.visible) {
        this.trackIntercom({action: 'hide'});
        this.$intercom.hide();
      } else {
        this.trackIntercom({action: 'show'});
        this.$intercom.show();
      }
    },
    onOpenYouTube() {
      window.open(PERCEPTILABS_YOUTUBE_URL, '_blank');
    },
    onOpenSlack() {
      window.open(PERCEPTILABS_SLACK_URL, '_blank');
    },
    onOpenForum() {
      window.open(PERCEPTILABS_FORUM_URL, '_blank');
    },
    onOpenBlogs() {
      window.open(PERCEPTILABS_BLOGS_URL, '_blank');
    },
    startUserFlow(){
      userflow.start(USER_FLOW_CONTENT_ID);
    },
    toggleTheme() {
      this.set_theme(this.theme === THEME_LIGHT ? THEME_DARK : THEME_LIGHT)
    }
  }
}
</script>

<style lang="scss" scoped>
  .app-header {
    z-index: 101;
    position: relative;
    display: flex;
    height: $h-header-win;
    // font-family: sans-serif;
    background: $bg-window;
    box-sizing: border-box;
    border-radius: 0px;
    padding: 0 20px;
  }

  .app-header-section {
    display: flex;
    flex: 1 1 100%;
    align-items: center;

    &.app-header-right {
      > *:first-child {
        margin-left: auto;
        display: flex;
        align-items: center;
      }

      > *:last-child {
        margin-right: 4rem;
      }

      > * {
        margin-left: 3.5rem;
      }
    }
  }

  .d-none {
    display: none;
  }
  .app-header_logo {
    margin: 0 12px 0 0px;
    // cursor: pointer;
    a {
      display: block;
      -webkit-app-region: no-drag;
    }
  }
  .app-title {
    font-size: 20px;
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
    display: flex;
    align-items: center;

    position: relative;
    cursor: pointer;

    & > svg {
      & > path {
        fill: $color-bold;
      }

      &:hover > path {
        fill: $color-6;
      }
    }
  }
  
  .dropdown-help {
    position: absolute;
    right: -30px;
    top: 38px;
    box-shadow: 0px 4px 4px rgba(122, 122, 122, 0.36);

    & span {
      margin-left: 8px;
      margin-right: 8px;
    }
  }
  .help-button {
    display: flex;
    align-items: center;

    position: relative;

    & > svg:hover > path {
      fill: #5E6F9F;
    }

    .help-button-panel {
      // transform-origin: top right;
      position: absolute;
      top: 3rem;
      right: 0;

      background: #131B30;
      border: 1px solid #363E51;
      box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.3);
      border-radius: 2px;

      // width: 16rem;

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

          display: flex;
          align-items: center;
          white-space: nowrap;

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

  .btn--circle {
    width: 25px;
    height: 25px;
    border: 1px solid #5E6F9F;
    border-radius: 50%;
  }
  
  .cursor-default {
    cursor: default !important;
  }
</style>
