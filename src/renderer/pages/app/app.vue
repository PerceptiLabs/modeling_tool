<template lang="pug">
  .page(
    v-if="showPage"
    ref="layersbar"
    )
    the-workspace
    the-toolbar
    the-layersbar
    the-sidebar
    tutorial-storyboard

</template>

<script>
  import { mapGetters, mapActions } from 'vuex';
  import { throttleEv } from '@/core/helpers.js'

  import TheToolbar         from '@/components/the-toolbar.vue'
  import TheLayersbar       from '@/components/the-layersbar.vue'
  import TheSidebar         from '@/components/the-sidebar.vue'
  import TheWorkspace       from '@/components/workspace/the-workspace.vue'
  import TutorialStoryboard from "@/components/tutorial/tutorial-storyboard.vue";

  export default {
    name: 'pageQuantum',
    components: {
      TheToolbar,
      TheLayersbar,
      TheSidebar,
      TheWorkspace,
      TutorialStoryboard
    },
    created() {
      if(!this.workspaceContent.length) {
        this.$store.dispatch('mod_workspace/ADD_network');
      }
    },
    mounted() {
      this.showPage = true;
      this.$store.commit('globalView/SET_appIsOpen', true);
      window.addEventListener("resize",  this.resizeEv, false);
      this.$nextTick(()=> this.addListeners())
    },
    beforeDestroy() {
      window.removeEventListener("resize", this.resizeEv, false);
      this.removeListeners();
      this.$store.commit('globalView/SET_appIsOpen', false);
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
        activeAction:   'mod_tutorials/getActiveAction',
        editIsOpen:           'mod_workspace/GET_networkIsOpen',
        currentNetwork: 'mod_workspace/GET_currentNetwork'
      }),
      workspaceContent() {
        return this.$store.state.mod_workspace.workspaceContent
      },
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
            this.addListeners()
          })
        }
        else {
          this.removeListeners();
          this.offDragListener();
        }
      },
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:  'mod_tutorials/pointActivate',
        eventResize:            'mod_events/EVENT_eventResize'
      }),
      //throttleEv,
      addListeners() {
        this.$refs.layersbar.addEventListener("dragstart", this.dragStart, false);
      },
      removeListeners() {
        this.$refs.layersbar.removeEventListener("dragstart", this.dragStart, false);
      },
      offDragListener() {
        this.$refs.layersbar.removeEventListener("dragend", this.dragEnd, false);
        this.$refs.layersbar.removeEventListener("dragover", this.dragOver, false);
        this.$refs.layersbar.removeEventListener("dragenter", this.dragEnter, false);
        this.$refs.layersbar.removeEventListener("dragleave", this.dragLeave, false);
        this.$refs.layersbar.removeEventListener("drop", this.dragDrop, false);
      },
      dragStart(event) {
        if ( event.target.draggable && this.editIsOpen && event.target.className.includes('btn--layersbar')) {
          this.$refs.layersbar.addEventListener("dragend", this.dragEnd, false);
          this.$refs.layersbar.addEventListener("dragover", this.dragOver, false);
          this.$refs.layersbar.addEventListener("dragenter", this.dragEnter, false);
          this.$refs.layersbar.addEventListener("dragleave", this.dragLeave, false);
          this.$refs.layersbar.addEventListener("drop", this.dragDrop, false);

          this.dragMeta.dragged = event.target;
          this.$store.commit('mod_workspace/ADD_dragElement', event);
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
        if ( event.target.classList[0] === this.dragMeta.outClassName) {
          this.$store.dispatch('mod_workspace/ADD_element', event)
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
