<template lang="pug">
  header.app-header
    .app-header-section.app-header-left
      .app-header_logo
        img(src="./../../../../static/img/project-page/logo.svg" alt="PerceptiLabs logo")
      the-menu
    
    .app-header-section.app-header-mid
      h4(v-if="projectName").page-title <span class="page-route-title">{{routeHeaderAlias}} </span>
      //- h4(v-if="projectName").page-title {{projectName}} / <span class="page-route-title">{{routeHeaderAlias}} </span>

    .app-header-section.app-header-right

      .help-button(
        @click="toggleCommunity(!showCommunityPanel)"
        @blur="toggleCommunity(false)"
        tabindex="0"
        )        
          
        svg(width="22" height="22" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg")
          path(fill-rule="evenodd" clip-rule="evenodd" d="M10 20C15.5228 20 20 15.5228 20 10C20 4.47715 15.5228 0 10 0C4.47715 0 0 4.47715 0 10C0 15.5228 4.47715 20 10 20ZM4.43934 5.43934C4.15804 5.72064 4 6.10218 4 6.5V15.0948C4.00002 15.169 4.02204 15.2415 4.0633 15.3032C4.10455 15.3648 4.16318 15.4129 4.23175 15.4412C4.30032 15.4696 4.37577 15.4769 4.44853 15.4624C4.52129 15.4478 4.5881 15.412 4.6405 15.3595L6.78025 14.2198C6.92087 14.0791 7.1116 14 7.3105 14H14.5C14.8978 14 15.2794 13.842 15.5607 13.5607C15.842 13.2794 16 12.8978 16 12.5V6.5C16 6.10218 15.842 5.72064 15.5607 5.43934C15.2794 5.15804 14.8978 5 14.5 5H5.5C5.10218 5 4.72064 5.15804 4.43934 5.43934ZM6.35984 7.35984C6.43016 7.28951 6.52554 7.25 6.625 7.25H13.375C13.4745 7.25 13.5698 7.28951 13.6402 7.35984C13.7105 7.43016 13.75 7.52554 13.75 7.625C13.75 7.72446 13.7105 7.81984 13.6402 7.89017C13.5698 7.96049 13.4745 8 13.375 8H6.625C6.52554 8 6.43016 7.96049 6.35984 7.89017C6.28951 7.81984 6.25 7.72446 6.25 7.625C6.25 7.52554 6.28951 7.43016 6.35984 7.35984ZM6.35984 9.23483C6.43016 9.16451 6.52554 9.125 6.625 9.125H13.375C13.4745 9.125 13.5698 9.16451 13.6402 9.23483C13.7105 9.30516 13.75 9.40054 13.75 9.5C13.75 9.59946 13.7105 9.69484 13.6402 9.76517C13.5698 9.83549 13.4745 9.875 13.375 9.875H6.625C6.52554 9.875 6.43016 9.83549 6.35984 9.76517C6.28951 9.69484 6.25 9.59946 6.25 9.5C6.25 9.40054 6.28951 9.30516 6.35984 9.23483ZM6.35984 11.1098C6.43016 11.0395 6.52554 11 6.625 11H10.375C10.4745 11 10.5698 11.0395 10.6402 11.1098C10.7105 11.1802 10.75 11.2755 10.75 11.375C10.75 11.4745 10.7105 11.5698 10.6402 11.6402C10.5698 11.7105 10.4745 11.75 10.375 11.75H6.625C6.52554 11.75 6.43016 11.7105 6.35984 11.6402C6.28951 11.5698 6.25 11.4745 6.25 11.375C6.25 11.2755 6.28951 11.1802 6.35984 11.1098Z" fill="#B6C7FB")

        .help-button-panel(v-if="showCommunityPanel")
          .help-button-panel-content
            .help-button-panel-content-item(@click="onOpenYouTube") 
              span YouTube
            .help-button-panel-content-item(@click="onOpenSlack") 
              span Slack
            .help-button-panel-content-item(@click="onOpenForum") 
              span Forum
            .help-button-panel-content-item(@click="onOpenBlogs") 
              span Blogs

      .help-button(
          @click="goToReport"
          :data-tutorial-target="'tutorial-model-hub-report-button'"
          data-testing-target="report-modal-btn"
        )
        svg(width="22" height="22" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg")
          path(fill-rule="evenodd" clip-rule="evenodd" d="M10 20C15.5228 20 20 15.5228 20 10C20 4.47715 15.5228 0 10 0C4.47715 0 0 4.47715 0 10C0 15.5228 4.47715 20 10 20ZM7.35575 3.74812C7.34112 3.69087 7.31505 3.63718 7.2791 3.59029C7.24316 3.54339 7.19809 3.50427 7.14661 3.47527C7.09513 3.44626 7.03831 3.42799 6.97958 3.42155C6.92084 3.41511 6.86141 3.42063 6.80487 3.43778C6.74833 3.45493 6.69585 3.48336 6.65059 3.52135C6.60534 3.55933 6.56825 3.60609 6.54155 3.65881C6.51486 3.71152 6.49913 3.76909 6.49529 3.82806C6.49146 3.88702 6.49961 3.94614 6.51925 4.00187L6.878 5.18487C6.07368 6.00216 5.62354 7.1033 5.625 8.24999H14.375C14.3765 7.1033 13.9263 6.00216 13.122 5.18487L13.4807 4.00187C13.5004 3.94614 13.5085 3.88702 13.5047 3.82806C13.5009 3.76909 13.4851 3.71152 13.4584 3.65881C13.4318 3.60609 13.3947 3.55933 13.3494 3.52135C13.3042 3.48336 13.2517 3.45493 13.1951 3.43778C13.1386 3.42063 13.0792 3.41511 13.0204 3.42155C12.9617 3.42799 12.9049 3.44626 12.8534 3.47527C12.8019 3.50427 12.7568 3.54339 12.7209 3.59029C12.685 3.63718 12.6589 3.69087 12.6442 3.74812L12.3896 4.58462C11.6792 4.12033 10.8487 3.87369 10 3.87499C9.15134 3.87374 8.3208 4.12038 7.61037 4.58462L7.35662 3.74812H7.35575ZM14.375 8.25V9.125H10.4375V16.9781C11.5167 16.8697 12.517 16.3642 13.2446 15.5599C13.9722 14.7555 14.375 13.7096 14.375 12.625H14.8125C14.9285 12.625 15.0398 12.6711 15.1219 12.7531C15.2039 12.8352 15.25 12.9465 15.25 13.0625V13.5C15.25 13.616 15.2961 13.7273 15.3781 13.8094C15.4602 13.8914 15.5715 13.9375 15.6875 13.9375C15.8035 13.9375 15.9148 13.8914 15.9969 13.8094C16.0789 13.7273 16.125 13.616 16.125 13.5V13.0625C16.125 12.7144 15.9867 12.3806 15.7406 12.1344C15.4944 11.8883 15.1606 11.75 14.8125 11.75H14.375V10.875H15.6875C15.8035 10.875 15.9148 10.8289 15.9969 10.7469C16.0789 10.6648 16.125 10.5535 16.125 10.4375C16.125 10.3215 16.0789 10.2102 15.9969 10.1281C15.9148 10.0461 15.8035 10 15.6875 10H14.375V9.125H14.8125C15.1606 9.125 15.4944 8.98672 15.7406 8.74058C15.9867 8.49444 16.125 8.1606 16.125 7.8125V7.375C16.125 7.25897 16.0789 7.14769 15.9969 7.06564C15.9148 6.98359 15.8035 6.9375 15.6875 6.9375C15.5715 6.9375 15.4602 6.98359 15.3781 7.06564C15.2961 7.14769 15.25 7.25897 15.25 7.375V7.8125C15.25 7.92853 15.2039 8.03981 15.1219 8.12186C15.0398 8.20391 14.9285 8.25 14.8125 8.25H14.375ZM9.5625 16.9781V9.125H5.625V8.25H5.1875C5.07147 8.25 4.96019 8.20391 4.87814 8.12186C4.79609 8.03981 4.75 7.92853 4.75 7.8125V7.375C4.75 7.25897 4.70391 7.14769 4.62186 7.06564C4.53981 6.98359 4.42853 6.9375 4.3125 6.9375C4.19647 6.9375 4.08519 6.98359 4.00314 7.06564C3.92109 7.14769 3.875 7.25897 3.875 7.375V7.8125C3.875 8.1606 4.01328 8.49444 4.25942 8.74058C4.50556 8.98672 4.8394 9.125 5.1875 9.125H5.625V10H4.3125C4.19647 10 4.08519 10.0461 4.00314 10.1281C3.92109 10.2102 3.875 10.3215 3.875 10.4375C3.875 10.5535 3.92109 10.6648 4.00314 10.7469C4.08519 10.8289 4.19647 10.875 4.3125 10.875H5.625V11.75H5.1875C4.8394 11.75 4.50556 11.8883 4.25942 12.1344C4.01328 12.3806 3.875 12.7144 3.875 13.0625V13.5C3.875 13.616 3.92109 13.7273 4.00314 13.8094C4.08519 13.8914 4.19647 13.9375 4.3125 13.9375C4.42853 13.9375 4.53981 13.8914 4.62186 13.8094C4.70391 13.7273 4.75 13.616 4.75 13.5V13.0625C4.75 12.9465 4.79609 12.8352 4.87814 12.7531C4.96019 12.6711 5.07147 12.625 5.1875 12.625H5.625C5.62499 13.7096 6.02784 14.7555 6.75539 15.5599C7.48295 16.3642 8.48335 16.8697 9.5625 16.9781Z" fill="#B6C7FB")

      .help-button(
        @click="toggleHelp(!showHelpPanel)"
        @blur="toggleHelp(false)"
        tabindex="0"
        )
        svg(
          :data-tutorial-target="'tutorial-model-hub-question-mark'" width="22" height="22" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"
        )
          path(fill-rule="evenodd" clip-rule="evenodd" d="M20 10C20 12.6522 18.9464 15.1957 17.0711 17.0711C15.1957 18.9464 12.6522 20 10 20C7.34784 20 4.8043 18.9464 2.92893 17.0711C1.05357 15.1957 0 12.6522 0 10C0 7.34784 1.05357 4.8043 2.92893 2.92893C4.8043 1.05357 7.34784 0 10 0C12.6522 0 15.1957 1.05357 17.0711 2.92893C18.9464 4.8043 20 7.34784 20 10ZM6.87 7.54125C6.82971 7.5418 6.78973 7.53412 6.7525 7.51868C6.71528 7.50324 6.6816 7.48038 6.65352 7.45148C6.62543 7.42257 6.60354 7.38825 6.58918 7.3506C6.57482 7.31295 6.5683 7.27276 6.57 7.2325C6.6875 5.11375 8.42125 4.375 10.0063 4.375C11.7513 4.375 13.3463 5.2875 13.3463 7.175C13.3463 8.525 12.5525 9.1675 11.7912 9.74625C10.87 10.445 10.5288 10.7063 10.5288 11.6038V11.735C10.5288 11.8179 10.4958 11.8974 10.4372 11.956C10.3786 12.0146 10.2991 12.0475 10.2163 12.0475H9.20375C9.12173 12.0475 9.04299 12.0153 8.98453 11.9577C8.92606 11.9002 8.89256 11.822 8.89125 11.74L8.88625 11.4688C8.83875 10.31 9.505 9.59625 10.3463 8.985C11.0838 8.43 11.5525 8.065 11.5525 7.27125C11.5525 6.24 10.7675 5.81125 9.91 5.81125C8.90625 5.81125 8.34375 6.40875 8.2325 7.22875C8.21 7.4 8.0725 7.54125 7.9 7.54125H6.86875H6.87ZM9.77625 15.595C9.04625 15.595 8.515 15.1025 8.515 14.4362C8.515 13.7463 9.04625 13.2613 9.7775 13.2613C10.5387 13.2613 11.0625 13.7463 11.0625 14.4362C11.0625 15.1025 10.5375 15.595 9.77625 15.595Z" fill="#B6C7FB")

        .help-button-panel(v-if="showHelpPanel")
          .help-button-panel-content
            .help-button-panel-content-item(@click="startUserFlow") Get Started
            //.help-button-panel-content-item(@click="toggleTutorialTips") {{ hideTipsDisplayText }}
            //.help-button-panel-content-item(@click="onActivateChecklist") Get started checklist
            //- .help-button-panel-content-item(@click="goToWhatsNew") What's new
            hr.help-button-panel-content-item
            .help-button-panel-content-item(@click="openVideoTutorials") 
              svg(width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M11.3995 1.0009C11.3995 0.724753 11.1756 0.500896 10.8995 0.500896L6.39949 0.500896C6.12335 0.500896 5.89949 0.724754 5.89949 1.0009C5.8995 1.27704 6.12335 1.5009 6.39949 1.5009L10.3995 1.5009L10.3995 5.5009C10.3995 5.77704 10.6234 6.0009 10.8995 6.0009C11.1756 6.0009 11.3995 5.77704 11.3995 5.5009L11.3995 1.0009ZM1.35355 11.2539L11.253 1.35445L10.5459 0.647342L0.646447 10.5468L1.35355 11.2539Z" fill="white")
              span Tutorials
            .help-button-panel-content-item(@click="goToDocumentation") 
              svg(width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M11.3995 1.0009C11.3995 0.724753 11.1756 0.500896 10.8995 0.500896L6.39949 0.500896C6.12335 0.500896 5.89949 0.724754 5.89949 1.0009C5.8995 1.27704 6.12335 1.5009 6.39949 1.5009L10.3995 1.5009L10.3995 5.5009C10.3995 5.77704 10.6234 6.0009 10.8995 6.0009C11.1756 6.0009 11.3995 5.77704 11.3995 5.5009L11.3995 1.0009ZM1.35355 11.2539L11.253 1.35445L10.5459 0.647342L0.646447 10.5468L1.35355 11.2539Z" fill="white")
              span Documentation
            .help-button-panel-content-item#intercom-launcher(@click="onToggleIntercom") 
              svg(width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg")
                path(d="M1.75 0.875C1.51794 0.875 1.29538 0.967187 1.13128 1.13128C0.967187 1.29538 0.875 1.51794 0.875 1.75V8.75C0.875 8.98207 0.967187 9.20462 1.13128 9.36872C1.29538 9.53281 1.51794 9.625 1.75 9.625H10.1378C10.6018 9.6251 11.0469 9.80954 11.375 10.1378L13.125 11.8878V1.75C13.125 1.51794 13.0328 1.29538 12.8687 1.13128C12.7046 0.967187 12.4821 0.875 12.25 0.875H1.75ZM12.25 0C12.7141 0 13.1592 0.184375 13.4874 0.512563C13.8156 0.840752 14 1.28587 14 1.75V12.9439C14 13.0304 13.9743 13.1151 13.9262 13.187C13.878 13.259 13.8096 13.315 13.7296 13.3481C13.6496 13.3812 13.5616 13.3898 13.4767 13.3728C13.3918 13.3558 13.3139 13.314 13.2528 13.2528L10.7564 10.7564C10.5923 10.5923 10.3698 10.5001 10.1378 10.5H1.75C1.28587 10.5 0.840752 10.3156 0.512563 9.98744C0.184374 9.65925 0 9.21413 0 8.75V1.75C0 1.28587 0.184374 0.840752 0.512563 0.512563C0.840752 0.184375 1.28587 0 1.75 0L12.25 0Z" fill="white")
                path(d="M4.375 5.25C4.375 5.48206 4.28281 5.70462 4.11872 5.86872C3.95462 6.03281 3.73206 6.125 3.5 6.125C3.26794 6.125 3.04538 6.03281 2.88128 5.86872C2.71719 5.70462 2.625 5.48206 2.625 5.25C2.625 5.01794 2.71719 4.79538 2.88128 4.63128C3.04538 4.46719 3.26794 4.375 3.5 4.375C3.73206 4.375 3.95462 4.46719 4.11872 4.63128C4.28281 4.79538 4.375 5.01794 4.375 5.25ZM7.875 5.25C7.875 5.48206 7.78281 5.70462 7.61872 5.86872C7.45462 6.03281 7.23206 6.125 7 6.125C6.76794 6.125 6.54538 6.03281 6.38128 5.86872C6.21719 5.70462 6.125 5.48206 6.125 5.25C6.125 5.01794 6.21719 4.79538 6.38128 4.63128C6.54538 4.46719 6.76794 4.375 7 4.375C7.23206 4.375 7.45462 4.46719 7.61872 4.63128C7.78281 4.79538 7.875 5.01794 7.875 5.25ZM11.375 5.25C11.375 5.48206 11.2828 5.70462 11.1187 5.86872C10.9546 6.03281 10.7321 6.125 10.5 6.125C10.2679 6.125 10.0454 6.03281 9.88128 5.86872C9.71719 5.70462 9.625 5.48206 9.625 5.25C9.625 5.01794 9.71719 4.79538 9.88128 4.63128C10.0454 4.46719 10.2679 4.375 10.5 4.375C10.7321 4.375 10.9546 4.46719 11.1187 4.63128C11.2828 4.79538 11.375 5.01794 11.375 5.25Z" fill="white")
              span Chat with us

      header-profile(v-if="showProfile")
</template>

<script>
  import TheMenu from '@/components/the-menu.vue'
  import HeaderProfile from "@/components/app-header/header-profile";
  import { mapGetters, mapActions } from 'vuex';
  import { PERCEPTILABS_DOCUMENTATION_URL, PERCEPTILABS_YOUTUBE_VIDEO_TUTORIAL_URL, PERCEPTILABS_YOUTUBE_URL, PERCEPTILABS_SLACK_URL, PERCEPTILABS_FORUM_URL, PERCEPTILABS_BLOGS_URL, USER_FLOW_CONTENT_ID } from "@/core/constants";
  import userflow from "userflow.js";
export default {
  name: "HeaderWin",
  components: {HeaderProfile, TheMenu},
  data: function() {
    return {
      showHelpPanel: false,
      showCommunityPanel: false,
      showProfile: !process.env.NO_KC,
      // MODAL_PAGE_WHATS_NEW,
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
    },
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
      trackQuestionMark:    'mod_tracker/TRACK_questionMark',
      trackIntercom:        'mod_tracker/TRACK_toggleIntercom',
    }),
    toProjectPage() {
      if(this.$route.name === 'app') {
        this.$router.push({name: 'projects'})
      }
    },
    goToReport() {
      window.open(PERCEPTILABS_FORUM_URL);
    },
    toggleHelp(value = null) {
      this.showHelpPanel = !!value;
      if (value) {
        this.trackQuestionMark()
      }
    },
    toggleCommunity(value = null) {
      this.showCommunityPanel = !!value;
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
      // this.setActivePageAction(MODAL_PAGE_WHATS_NEW);
      // this.trackHelpOption('Go to Whats New');
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
        display: flex;
        align-items: center;
      }

      > *:last-child {
        margin-right: 4rem;
      }

      * + * {
        margin-left: 2rem;
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
</style>
