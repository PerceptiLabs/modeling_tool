<template lang="pug">
  div(v-if="isOpen")#modal-page-engine-wrapper.modal-page-engine-wrapper
    create-select-project(v-if="currentPage === MODAL_PAGE_PROJECT")
    page-whats-new(v-else-if="currentPage === MODAL_PAGE_WHATS_NEW")
    page-questionnaire(v-else-if="currentPage === MODAL_PAGE_QUESTIONNAIRE")
</template>
<script>
  import { mapActions } from "vuex";
  import CreateSelectProject from "@/pages/create-select-project/create-select-project";
  import { MODAL_PAGE_PROJECT, MODAL_PAGE_WHATS_NEW, MODAL_PAGE_QUESTIONNAIRE } from "@/core/constants";
  import PageWhatsNew from "@/pages/onboarding/whats-new.vue";
  import PageQuestionnaire from "@/pages/questionnaire/questionnaire.vue";
  
  let visibilityWatcher = null;
  
  export default {
    name: 'ModalPagesEngine',
    components: { PageWhatsNew, CreateSelectProject, PageQuestionnaire},
    created() {},
    data: function() {
      return {
        MODAL_PAGE_PROJECT,
        MODAL_PAGE_WHATS_NEW,
        MODAL_PAGE_QUESTIONNAIRE
      }
    },
    computed:{
      isOpen() {
        return this.$store.state.modal_pages.isOpen
      },
      currentPage() {
        return this.$store.state.modal_pages.currentPage
      },
    },
    
    watch:{
      isOpen(isOpened) {
        if(isOpened) {
          visibilityWatcher = setInterval(() => {
            const el = document.getElementById('modal-page-engine-wrapper');
            if(!el) { location.reload();  }
            el.style.display="block";
          }, 2000)
        } else {
          clearInterval(visibilityWatcher);
        }
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
    backdrop-filter: blur(10px);
    z-index: 13;
  }
</style>