<template lang="pug">
  .page(
    v-if="showPage"
    ref="layersbar"
    )
    the-workspace
    the-toolbar
    the-layersbar
    the-sidebar
    the-info-popup(
      v-if="infoText"
      :info-text="infoText"
    )
    tutorial-storyboard

</template>

<script>
  import { mapGetters, mapActions } from 'vuex';

  import TheToolbar         from '@/components/the-toolbar.vue'
  import TheLayersbar       from '@/components/the-layersbar.vue'
  import TheSidebar         from '@/components/the-sidebar.vue'
  import TheWorkspace       from '@/components/workspace/the-workspace.vue'
  import TheInfoPopup       from "@/components/global-popups/the-info-popup.vue";
  import TutorialStoryboard from "@/components/tutorial/tutorial-storyboard.vue";

  export default {
    name: 'pageQuantum',
    components: {
      TheToolbar,
      TheLayersbar,
      TheSidebar,
      TheWorkspace,
      TheInfoPopup,
      TutorialStoryboard
    },
    created() {
      if(!this.workspaceContent.length) {
        this.$store.dispatch('mod_workspace/ADD_network', {'ctx': this});
      }
    },
    mounted() {
      this.showPage = true;
      this.$nextTick(()=> this.addListeners())
    },
    beforeDestroy() {
      this.removeListeners()
    },
    data() {
      return {
        showPage: false,
        dragMeta: {
          dragged: null,
          outClassName: 'svg-arrow'
        },
      }
    },
    computed: {
      ...mapGetters({
        activeAction:   'mod_tutorials/getActiveAction',
        selectedElList: 'mod_workspace/GET_currentSelectedEl',
        currentNetwork: 'mod_workspace/GET_currentNetwork'
      }),
      workspaceContent() {
        return this.$store.state.mod_workspace.workspaceContent
      },
      infoText() {
        return this.$store.state.globalView.globalPopup.showInfoPopup
      },
      networkMode() {
        return this.currentNetwork.networkMeta
          ? this.currentNetwork.networkMeta.netMode
          : 'edit'
      },
    },
    watch: {
      networkMode(newVal) {
        if(newVal == 'edit') {
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
        tutorialPointActivate: 'mod_tutorials/pointActivate'
      }),
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
        if ( event.target.draggable && this.networkMode === 'edit' && event.target.className.includes('btn--layersbar')) {
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
