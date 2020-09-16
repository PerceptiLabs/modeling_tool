<template lang="pug">

  //- .page(
  //-   v-if="showPage"
  //-   ref="layersbar"
  //-   )
  .page(ref="layersbar")
    the-workspace.workspace
    //- the-toolbar
    //- the-layersbar
    the-sidebar
    //- the-tutorial-storyboard(v-if="isShowTutorial")

</template>

<script>
  import { mapState, mapGetters, mapMutations, mapActions } from 'vuex';
  import { throttleEv } from '@/core/helpers.js'
  import { localStorageGridKey } from '@/core/constants.js'

  import TheToolbar         from '@/components/the-toolbar.vue'
  import TheLayersbar       from '@/components/the-layersbar.vue'
  import TheSidebar         from '@/components/the-sidebar.vue'
  import TheWorkspace       from '@/components/workspace/the-workspace.vue'
  import TheTutorialStoryboard from "@/components/tutorial/tutorial-storyboard.vue";
  import {shouldHideSidebar, calculateSidebarScaleCoefficient } from "../../core/helpers";
  import {isWeb} from "@/core/helpers";
  import { GITHUB_GET_TOKEN_BY_CODE_URL } from "@/core/constants";
  import axios from 'axios';

  export default {
    name: 'pageQuantum',
    components: { TheToolbar, TheLayersbar, TheSidebar, TheWorkspace, TheTutorialStoryboard },
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
      if(isWeb()) {
        // this.$store.dispatch('mod_webstorage/loadWorkspaces')
        //   .then(_ => {
        //     if(this.from.name === null) {
        //       this.$store.commit('mod_workspace/get_lastActiveTabFromLocalStorage');
        //     }
        //     if(!this.workspaceContent.length) { 
        //       this.$router.push({'name': 'projects'});
        //     }

        //     // request charts if the page has been refreshed, and
        //     // the current tab is the first one

        //     // this.SET_chartRequests(this.workspaceContent[0].networkID);
        //   });
      } else {
        if(!this.workspaceContent.length) this.ADD_network();
        this.DELETE_userWorkspace();
      }
    },
    mounted() {
      this.showPage = true;
      this.set_appIsOpen(true);
      window.addEventListener("resize",  this.resizeEv, false);
      if(isWeb()) {
        window.addEventListener('beforeunload', this.beforeUnload);
      }
      this.$nextTick(()=> {
        this.addDragListeners();
      });
      if(isWeb()) {
        if(shouldHideSidebar()) {
          this.setSidebarStateAction(false);
        }
        calculateSidebarScaleCoefficient(); 
      }
    },
    beforeDestroy() {
      window.removeEventListener("resize", this.resizeEv, false);
      if(isWeb()) {
        window.removeEventListener('beforeunload', this.beforeUnload);
      }
      this.removeDragListeners();
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
        editIsOpen:         'mod_workspace/GET_networkIsOpen',
        currentNetwork:     'mod_workspace/GET_currentNetwork',
        getLocalUserInfo:   'mod_user/GET_LOCAL_userInfo',
        getCurrentStepCode: 'mod_tutorials/getCurrentStepCode',
      }),
      ...mapState({
        isShowTutorial:   state=> state.mod_tutorials.showTutorialStoryBoard,
        workspaceContent: state=> state.mod_workspace.workspaceContent,
      }),
      networkMode() {
        return this.currentNetwork.networkMeta
          ? this.currentNetwork.networkMeta.netMode
          : 'edit'
      },
    },
    watch: {
      editIsOpen(newVal) {
        if(newVal) {
          this.$nextTick(function () {
            this.addDragListeners()
          })
        }
        else {
          this.removeDragListeners();
          this.offDragListener();
        }
      },
    },
    methods: {
      ...mapMutations({
        set_appIsOpen:                      'globalView/SET_appIsOpen',
        setGridValue:                       'globalView/setGridStateMutation',
        add_dragElement:                    'mod_workspace/ADD_dragElement',
        set_workspaceChangesInLocalStorage: 'mod_workspace-changes/set_workspaceChangesInLocalStorage',
      }),
      ...mapActions({
        eventResize:          'mod_events/EVENT_eventResize',
        ADD_network:          'mod_workspace/ADD_network',
        ADD_element:          'mod_workspace/ADD_element',
        SET_chartRequests:    'mod_workspace/SET_chartsRequestsIfNeeded',
        DELETE_userWorkspace: 'mod_user/DELETE_userWorkspace',
        setSidebarStateAction:'globalView/hideSidebarAction',
        updateWorkspaces:     'mod_webstorage/updateWorkspaces',
        layerAddedAction:     'mod_tutorials/tutorial-workspace-layer-added-setup',
      }),
      addDragListeners() {
        this.$refs.layersbar.addEventListener("dragstart", this.dragStart, false);
      },
      removeDragListeners() {
        this.$refs.layersbar.removeEventListener("dragstart", this.dragStart, false);
      },
      beforeUnload() {
        this.set_workspaceChangesInLocalStorage();
      },
      offDragListener() {
        this.$refs.layersbar.removeEventListener("dragend", this.dragEnd, false);
        this.$refs.layersbar.removeEventListener("dragover", this.dragOver, false);
        this.$refs.layersbar.removeEventListener("dragenter", this.dragEnter, false);
        this.$refs.layersbar.removeEventListener("dragleave", this.dragLeave, false);
        this.$refs.layersbar.removeEventListener("drop", this.dragDrop, false);
      },
      dragStart(event) {
        if(isWeb())
        event.dataTransfer.setData('text/plain', event.target.outerHTML);
        if ( event.target.draggable
          && this.editIsOpen
          && event.target.className.includes('btn--layersbar')
        ) {
          this.$refs.layersbar.addEventListener("dragend", this.dragEnd, false);
          this.$refs.layersbar.addEventListener("dragover", this.dragOver, false);
          this.$refs.layersbar.addEventListener("dragenter", this.dragEnter, false);
          this.$refs.layersbar.addEventListener("dragleave", this.dragLeave, false);
          this.$refs.layersbar.addEventListener("drop", this.dragDrop, false);

          this.dragMeta.dragged = event.target;
          this.add_dragElement(event);
          event.target.style.opacity = .75;
          if(isWeb())
          this.adjustDraggingForFireFox(event);
        }
      },
      dragEnd(event) {
        this.offDragListener();
        event.target.style.opacity = "";
      },
      dragOver(event) {
        event.preventDefault();
      },
      dragEnter(event) {},
      dragLeave(event) {},
      dragDrop(event) {
        event.preventDefault();

        if(event.target.classList[0] === this.dragMeta.outClassName) {
          this.ADD_element({event})
        }
      },
      adjustDraggingForFireFox(event) {
        event.dataTransfer.setDragImage(
          event.target, 
          event.target.clientWidth/2, 
          event.target.clientHeight/2);
      }
    }
  }
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .page {
    background-color: $bg-window;

    display: flex;
    max-width: calc(100vw - 46px);
    
    /deep/ .wrapper {
      position: static;
    }
  }
</style>
