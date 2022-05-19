<template lang="pug">
  .page(ref="layersbar")
    the-workspace.workspace
    // the-sidebar(v-if="getViewMode==='model' && getEmptyScreenMode===0")

</template>

<script>
  import { mapState, mapGetters, mapMutations, mapActions } from 'vuex';
  import { throttleEv } from '@/core/helpers.js'

  import TheSidebar         from '@/components/the-sidebar.vue'
  import TheWorkspace       from '@/components/workspace/the-workspace.vue'
  import { shouldHideSidebar, calculateSidebarScaleCoefficient } from "@/core/helpers";
  import { GITHUB_GET_TOKEN_BY_CODE_URL } from "@/core/constants";
  import axios from 'axios';

  export default {
    name: 'pageQuantum',
    components: { TheSidebar, TheWorkspace },

     beforeRouteEnter(to, from, next) {
        next((vm) => {
            vm.from = from;
        });
    },
    created() {
      if(this.$route.query.hasOwnProperty('code')) {
        const code = this.$route.query.code;
        const client_id = process.env.GITHUB_CLIENT_ID
        const data =  axios.get(`${GITHUB_GET_TOKEN_BY_CODE_URL}/${client_id}?code=${code}`, {
          headers: { 'Content-Type': 'application/json'}
        }).then(res => {
          let access_token = res.data.access_token;
          if(access_token) {
            this.$store.dispatch('mod_github/setGithubTokenAction', access_token);
            this.$store.dispatch('globalView/SET_exportNetworkToGithubPopup', true);
            this.$router.push({
              path: '/app',
              query: {}
            })
          }
          }).catch(err => console.log(err));
      }
    },
    mounted() {
      this.showPage = true;
      this.set_appIsOpen(true);
      window.addEventListener("resize",  this.resizeEv, false);
      window.addEventListener('beforeunload', this.beforeUnload);
      if(shouldHideSidebar()) {
        this.setSidebarStateAction(false);
      }
      calculateSidebarScaleCoefficient(); 
      if(localStorage.hasOwnProperty('isMiniMapNavigatorOpened')) {
        const mapValue = localStorage.getItem('isMiniMapNavigatorOpened') === 'true';
        this.setMiniMapNavigationMutation(mapValue);
      }
    },
    beforeDestroy() {
      window.removeEventListener("resize", this.resizeEv, false);
      window.removeEventListener('beforeunload', this.beforeUnload);
      this.set_appIsOpen(false);
    },
    data() {
      return {
        showPage: false,
        dragMeta: {
          dragged: null,
          outClassName: 'network-field',
        },
        resizeEv: throttleEv(this.eventResize),
        from: null,
      }
    },
    computed: {
      ...mapGetters({
        currentNetwork:   'mod_workspace/GET_currentNetwork',
        getEmptyScreenMode: 'mod_empty-navigation/getEmptyScreenMode',
        getViewMode:        'mod_workspace/GET_viewType',
        editIsOpen:         'mod_workspace/GET_networkIsOpen',
      }),
      ...mapState({
        workspaceContent: state=> state.mod_workspace.workspaceContent,
      }),
      networkMode() {
        return this.currentNetwork.networkMeta
          ? this.currentNetwork.networkMeta.netMode
          : 'edit'
      },
    },
    methods: {
      ...mapMutations({
        set_appIsOpen:                      'globalView/SET_appIsOpen',
        setGridValue:                       'globalView/setGridStateMutation',
        add_dragElement:                    'mod_workspace/ADD_dragElement',
        set_workspaceChangesInLocalStorage: 'mod_workspace-changes/set_workspaceChangesInLocalStorage',
        setMiniMapNavigationMutation:       'globalView/setMiniMapNavigationMutation',
      }),
      ...mapActions({
        eventResize:          'mod_events/EVENT_eventResize',
        ADD_network:          'mod_workspace/ADD_network',
        ADD_element:          'mod_workspace/ADD_element',
        SET_chartRequests:    'mod_workspace/SET_chartsRequestsIfNeeded',
        setSidebarStateAction:'globalView/hideSidebarAction',
        screenChange:         'mod_tracker/EVENT_screenChange',
      }),
      beforeUnload() {
        this.screenChange({ screenName: '' });
        this.set_workspaceChangesInLocalStorage();
      },
    }
  }
</script>

<style lang="scss" scoped>
  
  .page {
    background-color: $bg-window;

    display: flex;

    // border-radius: 15px 0 0 0;
    
    /deep/ .wrapper {
      position: static;
    }
  }
</style>
