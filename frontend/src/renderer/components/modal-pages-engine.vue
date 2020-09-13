<template lang="pug">
  div(v-if="isOpen")#modal-page-engine-wrapper.modal-page-engine-wrapper
    create-select-project(v-if="currentPage === MODAL_PAGE_PROJECT")
    page-login(v-else-if="currentPage === MODAL_PAGE_SIGN_IN")
    page-register(v-else-if="currentPage === MODAL_PAGE_SIGN_UP")
    page-whats-new(v-else-if="currentPage === MODAL_PAGE_WHATS_NEW")
    page-restore-account(v-else-if="currentPage === MODAL_PAGE_RESTORE_ACCOUNT")
</template>
<script>
  import { mapActions } from "vuex";
  import CreateSelectProject from "@/pages/create-select-project/create-select-project";
  import { MODAL_PAGE_PROJECT, MODAL_PAGE_SIGN_IN, MODAL_PAGE_SIGN_UP, MODAL_PAGE_WHATS_NEW, MODAL_PAGE_RESTORE_ACCOUNT } from "@/core/constants";
  import PageLogin from "@/pages/login/login";
  import PageRegister from "@/pages/register/register";
  import PageWhatsNew from "@/pages/onboarding/whats-new.vue";
  import PageRestoreAccount from "@/pages/restore-account/restore-account";
  
  let visibilityWatcher = null;
  
  export default {
    name: 'ModalPagesEngine',
    components: {PageRestoreAccount, PageRegister, PageWhatsNew, PageLogin, CreateSelectProject},
    created() {

      try {
        let localUserToken = JSON.parse(localStorage.getItem('currentUser'));
        if(!localUserToken.accessToken) {
          throw "haven't token";
        }
      } catch(e) {
        this.setActivePageAction(MODAL_PAGE_SIGN_UP)
      };

     
      // let localUserToken = JSON.parse(localStorage.getItem('currentUser'));
      
      // if(!localUserToken) {
      //   this.setActivePageAction(MODAL_PAGE_SIGN_UP)
      // }
    },
    data: function() {
      return {
        MODAL_PAGE_PROJECT,
        MODAL_PAGE_SIGN_UP,
        MODAL_PAGE_WHATS_NEW,
        MODAL_PAGE_SIGN_IN,
        MODAL_PAGE_RESTORE_ACCOUNT,
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
    z-index: 12;
  }
</style>