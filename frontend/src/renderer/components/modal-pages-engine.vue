<template lang="pug">
  div(v-if="isOpen" @click="closePageAction()").modal-page-engine-wrapper
    create-select-project(:v-if="currentPage === MODAL_PAGE_PROJECT")
</template>
<script>
  import { mapActions } from "vuex";
  import CreateSelectProject from "@/pages/create-select-project/create-select-project";
  import { MODAL_PAGE_PROJECT } from "@/core/constants";
  
  export default {
    name: 'ModalPagesEngine',
    components: {CreateSelectProject},
    created() {
      this.setActivePageAction(MODAL_PAGE_PROJECT)
    },
    computed:{
      isOpen() {
        return this.$store.state.modal_pages.isOpen
      },
      currentPage() {
        return this.$store.state.modal_pages.currentPage
      }
    },
    methods: {
      ...mapActions({
        setActivePageAction: 'modal_pages/setActivePageAction',
        closePageAction: 'modal_pages/closePageAction',
      })
    }
  }
  
</script>
<style scoped>
  .modal-page-engine-wrapper {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    min-height: 100%;
    background: rgba(35, 37, 42, 0.7);
    backdrop-filter: blur(17px);
    z-index: 999;
  }
</style>