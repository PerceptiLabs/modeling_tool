<template lang="pug">
  .page(
    v-if="showPage"
    ref="layersbar"
    )
    the-workspace
    the-toolbar
    the-layersbar
    the-sidebar
    the-tutorial-storyboard(v-if="isShowTutorial")

</template>

<script>
  import { mapState, mapGetters, mapMutations, mapActions } from 'vuex';
  import { throttleEv } from '@/core/helpers.js'

  import TheToolbar         from '@/components/the-toolbar.vue'
  import TheLayersbar       from '@/components/the-layersbar.vue'
  import TheSidebar         from '@/components/the-sidebar.vue'
  import TheWorkspace       from '@/components/workspace/the-workspace.vue'
  import TheTutorialStoryboard from "@/components/tutorial/tutorial-storyboard.vue";

  export default {
    name: 'pageQuantum',
    components: { TheToolbar, TheLayersbar, TheSidebar, TheWorkspace, TheTutorialStoryboard },
    created() {

      this.$store.dispatch('mod_workspace/GET_workspacesFromLocalStorage')
        .then(_ => {
          if(!this.workspaceContent.length) this.ADD_network();
        });
      //this.DELETE_userWorkspace();
    },
    mounted() {
      this.showPage = true;
      this.set_appIsOpen(true);
      window.addEventListener("resize",  this.resizeEv, false);
      window.addEventListener('beforeunload', this.saveWorkspaces);
      this.$nextTick(()=> {
        this.addDragListeners();
        if(this.getLocalUserInfo.showFirstAppTutorial) this.setShowStoryboard(true)
      })
    },
    beforeDestroy() {
      window.removeEventListener("resize", this.resizeEv, false);
      window.removeEventListener('beforeunload', this.saveWorkspaces);
      this.removeDragListeners();
      this.set_appIsOpen(false);
    },
    data() {
      return {
        showPage: false,
        dragMeta: {
          dragged: null,
          outClassName: 'svg-arrow',
        },
        resizeEv: throttleEv(this.eventResize)
      }
    },
    computed: {
      ...mapGetters({
        activeAction:     'mod_tutorials/getActiveAction',
        editIsOpen:       'mod_workspace/GET_networkIsOpen',
        currentNetwork:   'mod_workspace/GET_currentNetwork',
        getLocalUserInfo: 'mod_user/GET_LOCAL_userInfo',
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
        setShowStoryboard:            'mod_tutorials/SET_showTutorialStoryBoard',
        set_appIsOpen:                'globalView/SET_appIsOpen',
        add_dragElement:              'mod_workspace/ADD_dragElement',
        set_workspacesInLocalStorage: 'mod_workspace/set_workspacesInLocalStorage',
      }),
      ...mapActions({
        tutorialPointActivate:'mod_tutorials/pointActivate',
        eventResize:          'mod_events/EVENT_eventResize',
        ADD_network:          'mod_workspace/ADD_network',
        ADD_element:          'mod_workspace/ADD_element',
        DELETE_userWorkspace: 'mod_user/DELETE_userWorkspace'
      }),
      addDragListeners() {
        this.$refs.layersbar.addEventListener("dragstart", this.dragStart, false);
      },
      removeDragListeners() {
        this.$refs.layersbar.removeEventListener("dragstart", this.dragStart, false);
      },
      saveWorkspaces() {
        this.set_workspacesInLocalStorage();
      },
      offDragListener() {
        this.$refs.layersbar.removeEventListener("dragend", this.dragEnd, false);
        this.$refs.layersbar.removeEventListener("dragover", this.dragOver, false);
        this.$refs.layersbar.removeEventListener("dragenter", this.dragEnter, false);
        this.$refs.layersbar.removeEventListener("dragleave", this.dragLeave, false);
        this.$refs.layersbar.removeEventListener("drop", this.dragDrop, false);
      },
      dragStart(event) {
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
        }
      },
      dragEnd(event) {
        this.offDragListener();
        event.target.style.opacity = "";
        this.tutorialPointActivate({way: 'next', validation: this.activeAction.id})
      },
      dragOver(event) {
        event.preventDefault();
      },
      dragEnter(event) {},
      dragLeave(event) {},
      dragDrop(event) {
        event.preventDefault();
        if(event.target.classList[0] === this.dragMeta.outClassName) {
          this.ADD_element(event)
        }
      },
    }
  }
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .page {
    display: grid;
    background-color: $bg-window;
    grid-template-areas:  'toolbar   toolbar    sidebar'
                          'layersbar  workspace sidebar';
    grid-template-rows: auto 1fr;
    grid-template-columns: auto 1fr auto;
  }
</style>
