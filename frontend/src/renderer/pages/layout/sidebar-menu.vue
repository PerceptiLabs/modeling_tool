<template lang="pug">
  div.wrapper.project-sidebar
    div.nav-link(
      :class="{'is-active': this.$route.name === 'projects' || this.$route.name === 'main-page'}"
      @click="toProjects"
      )
      svg(xmlns='http://www.w3.org/2000/svg' width='21' height='12' viewbox='0 0 21 12' fill='none')
        path(fill-rule='evenodd' clip-rule='evenodd' d='M9.04773 0H19.0478C19.6001 0 20.0478 0.447715 20.0478 1V3.79031C20.0478 4.3426 19.6001 4.79031 19.0478 4.79031H9.04773C8.49544 4.79031 8.04773 4.3426 8.04773 3.79031V3.61304H3.73244C3.38663 4.21084 2.74028 4.61304 2 4.61304C0.89543 4.61304 0 3.71761 0 2.61304C0 1.50847 0.89543 0.613037 2 0.613037C2.74028 0.613037 3.38663 1.01524 3.73244 1.61304H8.04773V1C8.04773 0.447715 8.49544 0 9.04773 0ZM3.73244 10.613H8H8.04773V10.976C8.04773 11.5283 8.49544 11.976 9.04773 11.976H19.0478C19.6001 11.976 20.0478 11.5283 20.0478 10.976V8.18567C20.0478 7.63338 19.6001 7.18567 19.0478 7.18567H9.04773C8.49544 7.18567 8.04773 7.63338 8.04773 8.18567V8.61304H8H3.73244C3.38663 8.01524 2.74028 7.61304 2 7.61304C0.89543 7.61304 0 8.50847 0 9.61304C0 10.7176 0.89543 11.613 2 11.613C2.74028 11.613 3.38663 11.2108 3.73244 10.613Z' fill='#C4C4C4')
      div Overview
    div.nav-link(
      :class="{'is-active': isOnModelToolPage() && (GET_viewType==='model')}"
      @click="toModelingTool()"
      )
      svg(xmlns='http://www.w3.org/2000/svg' width='20' height='21' viewbox='0 0 20 21' fill='none')
        path(d='M20 7.65595V13.2904C20 13.8065 19.5699 14.2366 19.0538 14.2366H13.4194C12.9033 14.1936 12.4731 13.7635 12.4731 13.2473V7.65595C12.4731 7.13982 12.9033 6.70972 13.4194 6.70972H19.0538C19.5699 6.70972 20 7.13982 20 7.65595Z' fill='#C4C4C4')
        path(d='M4.68813 7.2688H2.79565V13.2903H4.68813V7.2688Z' fill='#C4C4C4')
        path(d='M16.258 2.79565H7.2688V4.51608C7.2688 4.5591 7.2688 4.64512 7.2688 4.68813H15.3118V10.4516C15.3118 10.9677 15.7419 11.3978 16.258 11.3978C16.7742 11.3978 17.2043 10.9677 17.2043 10.4516V3.74189C17.1613 3.22576 16.7742 2.79565 16.258 2.79565Z' fill='#C4C4C4')
        path(d='M6.53763 7.44086H0.903226C0.387097 7.44086 0 7.05376 0 6.53763V0.903226C0 0.387097 0.387097 0 0.903226 0H6.53763C7.05376 0 7.44086 0.387097 7.44086 0.903226V6.53763C7.44086 7.05376 7.05376 7.44086 6.53763 7.44086ZM0.903226 0.860215C0.860215 0.860215 0.860215 0.860215 0.860215 0.903226V6.53763C0.860215 6.58065 0.860215 6.58065 0.903226 6.58065H6.53763C6.58065 6.58065 6.58065 6.58065 6.58065 6.53763V0.903226C6.58065 0.860215 6.58065 0.860215 6.53763 0.860215H0.903226Z' fill='#C4C4C4')
        path(d='M6.53763 20.5163H0.903226C0.387097 20.5163 0 20.192 0 19.6131V13.9787C0 13.4625 0.387097 13.0754 0.903226 13.0754H6.53763C7.05376 13.0754 7.44086 13.4625 7.44086 13.9787V19.6131C7.44086 20.1292 7.05376 20.5163 6.53763 20.5163ZM0.903226 13.9357C0.860215 13.9357 0.860215 13.9357 0.860215 13.9787V19.6131C0.860215 19.6561 0.860215 19.6561 0.903226 19.6561H6.53763C6.58065 19.6561 6.58065 19.6561 6.58065 19.6131V13.9787C6.58065 13.9357 6.58065 13.9357 6.53763 13.9357H0.903226Z' fill='#C4C4C4')
      div Model
    div.nav-link(:class="{'is-active': (GET_viewType==='statistic') && isOnModelToolPage()}"
      @click="toModelStatistic()"
      )
      svg(xmlns='http://www.w3.org/2000/svg' width='20' height='24' viewbox='0 0 20 24' fill='none')
        path(d='M12.1292 7.01069V9.37628C12.1292 9.89241 11.6991 10.3225 11.1829 10.3225H8.81733C8.3012 10.3225 7.87109 9.89241 7.87109 9.37628V7.01069C7.87109 6.49456 8.3012 6.06445 8.81733 6.06445H11.1829C11.6991 6.06445 12.1292 6.49456 12.1292 7.01069Z' fill='#C4C4C4')
        path(d='M3.6129 17.4623H1.76344C0.817204 17.4623 0 16.6881 0 15.6988V13.8494C0 12.8601 0.774194 12.0859 1.76344 12.0859H3.6129C4.60215 12.0859 5.37634 12.8601 5.37634 13.8494V15.6988C5.33333 16.6881 4.55914 17.4623 3.6129 17.4623ZM1.76344 13.2472C1.41935 13.2472 1.11828 13.5483 1.11828 13.8924V15.7419C1.11828 16.0859 1.41935 16.387 1.76344 16.387H3.6129C3.95699 16.387 4.25806 16.0859 4.25806 15.7419V13.8924C4.25806 13.5483 3.95699 13.2472 3.6129 13.2472H1.76344Z' fill='#C4C4C4')
        path(d='M19.4409 7.01069V9.37628C19.4409 9.89241 19.0108 10.3225 18.4947 10.3225H16.1291C15.613 10.3225 15.1829 9.89241 15.1829 9.37628V7.01069C15.1829 6.49456 15.613 6.06445 16.1291 6.06445H18.4947C19.0108 6.06445 19.4409 6.49456 19.4409 7.01069Z' fill='#C4C4C4')
        path(d='M19.4409 0.946237V3.31183C19.4409 3.82796 19.0108 4.25806 18.4947 4.25806H16.1291C15.613 4.25806 15.1829 3.82796 15.1829 3.31183V0.946237C15.1829 0.430108 15.613 0 16.1291 0H18.4947C19.0108 0 19.4409 0.430108 19.4409 0.946237Z' fill='#C4C4C4')
        path(d='M10.8817 20.473H9.03224C8.04299 20.473 7.2688 19.6988 7.2688 18.7096V13.8923C7.2688 12.9031 8.04299 12.1289 9.03224 12.1289H10.8817C11.8709 12.1289 12.6451 12.9031 12.6451 13.8923V18.7096C12.6451 19.6988 11.8709 20.473 10.8817 20.473ZM9.07525 13.2472C8.73116 13.2472 8.43009 13.5483 8.43009 13.8923V18.7096C8.43009 19.0536 8.73116 19.3547 9.07525 19.3547H10.9247C11.2688 19.3547 11.5699 19.0536 11.5699 18.7096V13.8923C11.5699 13.5483 11.2688 13.2472 10.9247 13.2472H9.07525Z' fill='#C4C4C4')
        path(d='M18.2366 23.7418H16.3871C15.4409 23.7418 14.6237 22.9676 14.6237 21.9784V13.8923C14.6237 12.9031 15.3979 12.1289 16.3871 12.1289H18.2366C19.2258 12.1289 20 12.9031 20 13.8923V21.9784C20 22.9246 19.2258 23.7418 18.2366 23.7418ZM16.3871 13.2472C16.043 13.2472 15.7419 13.5483 15.7419 13.8923V21.9784C15.7419 22.3225 16.043 22.6235 16.3871 22.6235H18.2366C18.5806 22.6235 18.8817 22.3225 18.8817 21.9784V13.8923C18.8817 13.5483 18.5806 13.2472 18.2366 13.2472H16.3871Z' fill='#C4C4C4')
      div Training
    router-link.nav-link(:class="{'is-active': isOnTestPage()}"
      :to="{name: 'test'}"
      )

      svg(xmlns="http://www.w3.org/2000/svg" width="17" height="20" viewBox="0 0 17 20" fill="none")
        path(class="test-fill" d="M16.2237 16.957L10.7205 8.06791V1.31603H11.2051C11.5495 1.31603 11.8288 1.03674 11.8288 0.69228V0.623755C11.8288 0.279203 11.5495 0 11.2051 0H5.31402C4.96957 0 4.69027 0.279299 4.69027 0.623755V0.69228C4.69027 1.03674 4.96957 1.31603 5.31402 1.31603H5.79861V8.06791L0.295401 16.957C-0.0810075 17.5648 -0.0987162 18.2996 0.248146 18.9221C0.618491 19.5869 1.34099 19.9999 2.13375 19.9999H14.3855C15.1781 19.9999 15.9007 19.5869 16.2711 18.9221C16.6178 18.2996 16.6001 17.5649 16.2237 16.957ZM6.76105 8.34172V1.79725H9.75817V8.34172L11.7146 11.5019H4.80451L6.76105 8.34172Z" stroke="none")
      div Evaluate

    router-link.nav-link(:class="{'is-active': isExportPageOpened}"
      :to="{name: 'export'}"
    )
      svg(width="22" height="16" viewBox="0 0 22 16" fill="none" xmlns="http://www.w3.org/2000/svg")
        path(class="test-fill" d="M22 8L18 4V7H9V9H18V12L22 8ZM0 14V2C0 0.89 0.9 0 2 0H14C14.5304 0 15.0391 0.210714 15.4142 0.585786C15.7893 0.960859 16 1.46957 16 2V5H14V2H2V14H14V11H16V14C16 14.5304 15.7893 15.0391 15.4142 15.4142C15.0391 15.7893 14.5304 16 14 16H2C1.46957 16 0.960859 15.7893 0.585786 15.4142C0.210714 15.0391 0 14.5304 0 14Z" fill="none")
      div Export
    
    //- div.nav-link(
    //-   :class="{'is-active': this.$route.name === 'settings'}"
    //-   @click="toSettings"
    //-   )
    //-   svg(xmlns='http://www.w3.org/2000/svg' width='19' height='20' viewbox='0 0 19 20' fill='none')
    //-     path(d='M16.4657 10.3828C16.4657 10.0828 16.5657 9.78284 16.5657 9.48284C16.5657 9.18284 16.5657 8.88284 16.4657 8.58284L18.4657 6.98284C18.6657 6.88284 18.6657 6.58284 18.5657 6.38284L16.6657 3.08284C16.5657 2.88284 16.2657 2.78284 16.0657 2.88284L13.6657 3.88284C13.1657 3.48284 12.6657 3.18284 12.0657 2.98284L11.6657 0.482843C11.6657 0.282843 11.4657 0.0828427 11.1657 0.0828427H7.36569C7.16569 -0.117157 6.96569 0.0828427 6.86569 0.282843L6.56569 2.88284C5.96569 3.08284 5.46569 3.38284 4.96569 3.78284L2.56569 2.78284C2.36569 2.78284 2.06569 2.78284 1.96569 2.98284L0.0656854 6.38284C-0.0343146 6.58284 -0.0343146 6.78284 0.165685 6.98284L2.16569 8.58284C2.16569 8.88284 2.06569 9.18284 2.06569 9.48284C2.06569 9.78284 2.06569 10.0828 2.16569 10.3828L0.165685 11.9828C-0.0343146 12.0828 -0.0343146 12.3828 0.0656854 12.5828L1.96569 15.8828C2.06569 16.0828 2.36569 16.1828 2.56569 16.0828L4.96569 15.0828C5.46569 15.4828 5.96569 15.7828 6.56569 15.9828L6.96569 18.4828C6.96569 18.8828 7.16569 19.0828 7.36569 19.0828H11.1657C11.3657 19.0828 11.5657 18.8828 11.6657 18.6828L12.0657 16.1828C12.6657 15.9828 13.1657 15.5828 13.6657 15.2828L16.0657 16.2828C16.2657 16.3828 16.5657 16.2828 16.6657 16.0828L18.5657 12.7828C18.6657 12.5828 18.6657 12.2828 18.4657 12.1828L16.4657 10.3828ZM9.26569 13.0828C7.26569 13.0828 5.66569 11.4828 5.66569 9.48284C5.66569 7.48284 7.36569 5.88284 9.26569 5.88284C11.1657 5.88284 12.8657 7.48284 12.8657 9.48284C12.8657 11.4828 11.2657 13.0828 9.26569 13.0828Z' fill='#C4C4C4')

    //-   div Settings
</template>

<script>
  import { mapState, mapActions, mapGetters, mapMutations }  from 'vuex';
  import { 
    LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY,
    TRACKER_SCREENNAME_WORKSPACE,
    TRACKER_SCREENNAME_WORKSPACE_TRAINING,
    TRACKER_SCREENNAME_STATISTICS,
    TRACKER_SCREENNAME_STATISTICS_TRAINING,
    TRACKER_SCREENNAME_TEST,
    TRACKER_SCREENNAME_TEST_TRAINING,
    TRACKER_SCREENNAME_PROJECTS,
    TRACKER_SCREENNAME_PROJECTS_TRAINING
  } from "@/core/constants";

  export default {
    name: 'SidebarMnu',
    data() {
      return {
        haveAtLeastOneItemStatistic: false,
        statisticItemIndex: null,

        haveAtLeastOneTestItem: false,
        testItemIndex: null,
      }
    },
    created(){
      this.handleStatisticState(this.workspaceModels);
      this.handleTestState(this.workspaceModels);
    },
    mounted() {
    },
    computed: {
      ...mapState({
        workspaceModels:    state => state.mod_workspace.workspaceContent,
        showNewModelPopup:  state => state.globalView.globalPopup.showNewModelPopup
      }),
      ...mapGetters({
        testIsOpen:             'mod_workspace/GET_testIsOpen',
        currentNetwork:         'mod_workspace/GET_currentNetwork',
        currentNetworkIndex:    'mod_workspace/GET_currentNetworkIndex',
        networkIsNotEmpty:      'mod_workspace/GET_networkIsNotEmpty',
        anyNetworkIsTraining:   'mod_workspace/GET_anyNetworkIsTraining',
        GET_viewType:           'mod_workspace/GET_viewType',
        GET_currentModelIndex:  'mod_workspace/GET_currentModelIndex',
        GET_currentStatsIndex:  'mod_workspace/GET_currentStatsIndex',
        GET_currentTestIndex:   'mod_workspace/GET_currentTestIndex',
      }),
      statusLocalCore() {
        return this.$store.state.mod_api.statusLocalCore;
      },
      isExportPageOpened() {
        return this.$route.name === 'export';
      },
      isStatisticsOrTestOpened() {
        const currentItemNetwork = this.$store.getters['mod_workspace/GET_currentNetwork'];
        if(!currentItemNetwork.hasOwnProperty('networkMeta')) return false;
        return currentItemNetwork.networkMeta.openStatistics === true || currentItemNetwork.networkMeta.openTest === true;
      },
      firstItemWithTextIndex() {
        return this.workspaceModels.findIndex(model => model.networkMeta.openTest !== null && model.networkMeta.coreStatus.Status === 'Finished');
      },
      hasStatistics() {
        return this.workspaceModels.some(model => model.networkMeta.openStatistics !== null);
      },
      hasTest() {
        return this.workspaceModels.some(model => model.networkMeta.openTest !== null && model.networkMeta.coreStatus.Status === 'Finished');
      },
      currentOrFirstStatisticsIdx() {
        const idx = this.workspaceModels.findIndex(model => model.networkMeta.openStatistics !== null);
        return idx;
      },
      currentOrFirstTestIdx() {

        let idx = -1;

        if (typeof this.testIsOpen === 'boolean') {
          idx = this.currentNetworkIndex;
        } else {
          idx = this.workspaceModels.findIndex(model => model.networkMeta.openTest !== null && model.networkMeta.coreStatus.Status === 'Finished');
        }

        return idx;
      },
      modelCount() {
        return this.workspaceModels.length;
      },
      screenName() {
        if (this.$route.name === 'projects')   {
          return this.anyNetworkIsTraining ? 
            TRACKER_SCREENNAME_PROJECTS_TRAINING : 
            TRACKER_SCREENNAME_PROJECTS
        } else if (this.GET_viewType === 'statistic') {
          return this.anyNetworkIsTraining ? 
            TRACKER_SCREENNAME_STATISTICS_TRAINING :
            TRACKER_SCREENNAME_STATISTICS;
        } else if (this.GET_viewType === 'test') {
          return this.anyNetworkIsTraining ? 
            TRACKER_SCREENNAME_TEST_TRAINING :
            TRACKER_SCREENNAME_TEST;
        } else if (this.GET_viewType === 'model') {
          return this.anyNetworkIsTraining ? 
            TRACKER_SCREENNAME_WORKSPACE_TRAINING :
            TRACKER_SCREENNAME_WORKSPACE;
        } 
      }
    },
    watch: {
      modelCount: {
        handler(newValue, oldValue) {
          if (newValue - oldValue === 1 && oldValue != 0 ) return;
         
          const selectedTab = localStorage.getItem(LOCAL_STORAGE_WORKSPACE_VIEW_TYPE_KEY);
          
          const modelCandidate = this.workspaceModels.findIndex(item => item.networkMeta.hideModel!==true);
          this.$store.dispatch('mod_workspace/SET_currentModelIndex', modelCandidate);

          const testCandidate = this.workspaceModels.findIndex(item => typeof item.networkMeta.openTest === 'boolean' && item.networkMeta.hideTest!==true);
          this.$store.dispatch('mod_workspace/SET_currentTestIndex', testCandidate);

          const statsCandidate = this.workspaceModels.findIndex(item => typeof item.networkMeta.openStatistics === 'boolean' && item.networkMeta.hideStatistics!==true);
          this.$store.dispatch('mod_workspace/SET_currentStatsIndex', statsCandidate);     

          if (selectedTab === 'model') {
            this.$store.dispatch("mod_workspace/setViewType", 'model');
            if (modelCandidate >= 0) {
              // this.$store.dispatch("mod_workspace/SET_currentNetwork", modelCandidate);
              this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);
            } else {
              this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 1);
            }
          } else {
            this.$store.dispatch("mod_workspace/setViewType", 'statistic');
            if (statsCandidate >= 0) {
              this.$store.dispatch("mod_workspace/SET_currentNetwork", statsCandidate);
              this.$store.dispatch("mod_workspace/SET_openStatistics", true);
              this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);
            } else {
              this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 2);
            }
          }


        }
      },
      workspaceModels: {
        deep: true,
        immediate: true,
        handler(models) {
          this.resetModelIndexes();
          this.handelModelIndexes(models);
        }
      },
      screenName: {
        handler(newVal, oldVal) {
          this.$store.dispatch('mod_tracker/EVENT_screenChange', { 
            screenName: newVal
          });
        },
        immediate: true
      },
    },
    methods: {
      ...mapActions({
        SET_currentNetwork: 'mod_workspace/SET_currentNetwork',
        SET_openStatistics: 'mod_workspace/SET_openStatistics',
        SET_openTest:       'mod_workspace/SET_openTest',
        set_chartRequests:  'mod_workspace/SET_chartsRequestsIfNeeded',
        setStatisticsAvailability:'mod_workspace/setStatisticsAvailability',
        setCheckpointAvailability:'mod_workspace/setCheckpointAvailability',
        closeStatsTestViews:  'mod_workspace/SET_statisticsAndTestToClosed',
        setCurrentView:     'mod_tutorials/setCurrentView',
        showInfoPopup:       'globalView/GP_infoPopup',
      }),
      resetModelIndexes() {
        this.resetStatistic();
        this.resetTest();
      },
      resetStatistic(){
        this.statisticItemIndex = null;
        this.haveAtLeastOneItemStatistic = false;
      },
      resetTest() {
        this.testItemIndex = null;
        this.haveAtLeastOneTestItem = false;
      },
      handelModelIndexes(models){
        this.handleStatisticState(models);
        this.handleTestState(models);
      },
      handleStatisticState(models) {
        const firstItemWithStatistcsIndex = models.findIndex(model => model.networkMeta.openStatistics !== null);
        // console.log('handleStatisticState', firstItemWithStatistcsIndex);

        if(firstItemWithStatistcsIndex !== -1) {
           this.haveAtLeastOneItemStatistic = true;
           this.statisticItemIndex = firstItemWithStatistcsIndex;
        } else {
          this.haveAtLeastOneItemStatistic = false;
          this.statisticItemIndex = null;
        }
      },
      handleTestState(models) {
        const firstItemWithTextIndex = models.findIndex(model => model.networkMeta.openTest !== null && model.networkMeta.coreStatus.Status !== 'Finished');
        // console.log('handleTestState', firstItemWithTextIndex);

        if(firstItemWithTextIndex !== -1) {
          this.haveAtLeastOneTestItem = true;
          this.testItemIndex = firstItemWithTextIndex;
        } else {
          this.haveAtLeastOneTestItem = false;
          this.testItemIndex = null;
        }

      },
      isOnModelToolPage(){
        return this.$route.name === 'app';
      },
      doesCurrentNetworkHaveTest() {
        return this.currentNetwork.networkMeta.openTest !== null;
      },
      isModelPageAndNetworkHasStatistic() {
        return this.$route.name === 'app' && this.currentNetwork.networkMeta.openStatistics !== null
      },
      toProjects() {
        this.$router.push({name: 'projects'});
      },
      toSettings() {
        this.$router.push({name: 'settings'});

        this.$nextTick(() => {
          this.setCurrentView('');
        });
      },
      toModelStatistic() {
        // setStatisticsAvailability calls isTrained for each networks
        // The result determines if the kernel has info about the stats views
        // In other words, "false" sets openStatistics to null
        this.setStatisticsAvailability()
        .then(_ => {
          this.$nextTick(() => {
            this.goToStatisticsView();
          });
        });
      },
      goToStatisticsView() { 
        //$route.name === 'app' && currnetNetwork.networkMeta.openStatistics !== null
        // console.group('---------- STATS SIDEBUTTON CLICKED ----------');
        // console.log("ModelingIndex", this.GET_currentModelIndex);
        // console.log("StatsIndex", this.GET_currentStatsIndex);
        // console.log("TestsIndex", this.GET_currentTestIndex);
        // console.groupEnd();

        const item = this.workspaceModels[this.GET_currentStatsIndex];
        if (item && typeof item.networkMeta.openStatistics !== 'boolean') {
          // This block is triggered when there is a crash
          // The GET_currentStatsIndex could be pointing to a network that
          // doesn't have valid training data/visualization.
          // So we must recalc a new candidate

          const statsCandidate = this.workspaceModels.findIndex(item => typeof item.networkMeta.openStatistics === 'boolean' && item.networkMeta.hideStatistics!==true);
          this.$store.commit('mod_workspace/set_currentStatsIndex', statsCandidate);
        }

        if(this.GET_currentStatsIndex==-1) {
          this.$store.dispatch("mod_workspace/setViewType", 'statistic');
          this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 2);
          if(!this.isOnModelToolPage()) {this.$router.push({name: 'app'});}
          return;
        }

        this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);

        this.$store.dispatch("mod_workspace/setViewType", 'statistic');
        if(!this.isOnModelingToolPage()){
          this.$router.push({name: 'app'});
        } 

        this.SET_currentNetwork(this.GET_currentStatsIndex)
          .then(() => { 
            this.$store.dispatch("mod_workspace/EVENT_onceDoRequest");
            this.SET_openStatistics(true);
            this.set_chartRequests(item.networkID);
          });

        this.$nextTick(() => {
          if (!this.showNewModelPopup) {
            this.setCurrentView('tutorial-statistics-view');
          }
        });
      },
      isOnStatisticsView() {
        return this.currentNetwork.networkMeta.openStatistics === true
      },
      isOnTestView() {
        return this.currentNetwork.networkMeta.openTest === true
      },
      haveCurrentModelStatistics() {
        return this.currentNetwork.networkMeta.openStatistics !== null
      },
      haveCurrentModelTest() {
        return this.currentNetwork.networkMeta.openTest !== null
      },
      isOnModelingToolPage() {
        return this.$route.name === 'app';
      },
      toModelingTool() {
        // console.group('---------- MODEL SIDEBUTTON CLICKED ----------');
        // console.log("ModelingIndex", this.GET_currentModelIndex);
        // console.log("StatsIndex", this.GET_currentStatsIndex);
        // console.log("TestsIndex", this.GET_currentTestIndex);
        // console.groupEnd();

        if(this.GET_currentModelIndex==-1) {
          this.$store.dispatch("mod_workspace/setViewType", 'model');
          this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 1);

          if (this.currentNetwork) { 
            this.closeStatsTestViews({ networkId: this.currentNetwork.networkID });
          }

          if(!this.isOnModelToolPage()) {this.$router.push({name: 'app'});}
          return;
        }

        this.$store.commit('mod_empty-navigation/set_emptyScreenMode', 0);
        this.$store.dispatch("mod_workspace/setViewType", 'model');

        if(!this.isOnModelingToolPage()){
          this.$router.push({name: 'app'});
        } 

        this.SET_currentNetwork(this.GET_currentModelIndex);

        this.closeStatsTestViews({ networkId: this.currentNetwork.networkID });

        this.$nextTick(() => {
          if (!this.showNewModelPopup) {
            this.setCurrentView('tutorial-workspace-view');
          }
        });
      },
      isOnTestPage() {
        return this.$route.name === 'test';
      }
    },
  }

</script>
// 1px solid rgba(97, 133, 238, 0.4)
<style lang="scss" scoped>
  
  .project-sidebar {
    display: flex;
    flex-direction: column;    
  }
  .wrapper {
    width: $w-sidemenu;
    height: 100%;
    background: $bg-window;
    z-index: 10;
    // border-right: 1px solid rgba(97, 133, 238, 0.4);
    // box-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);
  }
  .logo-link {
    display: block;
    padding-top: 10px;
    margin-left: 1px;
    margin-bottom: 5px;
  }
  .nav-link {
    cursor: pointer;
    margin-top: 24px;
    position: relative;
    display: flex;
    height: 30px;
    width: $w-sidemenu;
    justify-content: left;
    align-items: center;
    color: theme-var($neutral-1);
    box-sizing: border-box;
    padding-left: 12px;
    border-radius: 0px 4px 4px 0px;
    font-size: 16px;
    font-weight: 700;

    &:not(.nav-stroke) {
      svg, path {
        margin-right: 12px;
        fill: $color-bold;
      }
    }  

    &.nav-stroke {
      svg, path {
        margin-right: 12px;
        stroke: $color-bold;
      }
    }

    &:hover,
    &.is-active {
      color: $color-6;
      
      svg, path {
        fill: $color-6;
      }
      // border-radius: 10px 0px 0px 10px;

      
    
      &:after {
        // content: '';
        // position: absolute;
        // left: 0;
        // top: 0;
        // background-color: #fff;
        // width: 2px;
        // height: 100%;
      }
    }

    &.is-active {
      &::after {
        content: '';
        position: absolute;
        top: 0px;
        left: 0px;
        background: $color-6;
        border-radius: 0px 4px 4px 0px;
        width: 4px;
        height: 100%;
      }
    }
  }
  .disabled {
    cursor: default;
    opacity: 0.3;
  }

  .switch-theme {
    margin-top: auto;
    margin-bottom: auto;
    margin-left: 12px;
  }
</style>
