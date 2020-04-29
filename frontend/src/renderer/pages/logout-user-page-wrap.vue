<template lang="pug">
  main.page_login
    view-loading
    .login_main
      .d-flex.align-items-center.log-in-header
        img(src="../../../static/img/perceptilabs-logo-icon.svg" alt="PerceptiLabs logo")
        img(src="./../../../static/img/perceptilabs-logo-icon.svg" alt="PerceptiLabs logo")
        h1(v-if="titlePage.length") {{ titlePage }}
      slot


</template>

<script>
  import ViewLoading from '@/components/different/view-loading.vue'

export default {
  name: 'LogoutUserPageWrap',
  components: { ViewLoading },
  props: {
    titlePage: { type: String, default: '' },
  },
  mounted() {
    if(this.userIsLogin) this.loginUser()
  },
  computed: {
    isLoading() {
      return this.$store.state.mod_login.showLoader
    },
    userIsLogin() {
      return this.$store.getters['mod_user/GET_userIsLogin']
    },
  },
  watch: {
    userIsLogin(newVal) {
      if(newVal) this.loginUser();
    }
  },
  methods: {
    loginUser() {
      this.$router.replace('/projects');
    },
  }
}
</script>
<style lang="scss" scoped>
  @import "../scss/base";
  .page_login {
    display: flex;
    align-items: center;
    flex-direction: column;
    justify-content: center;
    padding: 3rem;
    /*background: #272C37;*/
    /*backdrop-filter: blur(20px);*/
    min-height: 100vh;
    background: #272C37;
    backdrop-filter: blur(20px);
    overflow-y: auto !important;
  }

  .login_logo {
    margin-top: 3rem;
    margin-bottom: 2rem;
  }

  .login_main {
    position: relative;
    /*width: 49rem ;*/
    width: 400px;
    border-radius: 2*$bdrs;
    padding: 4.6rem;
    text-align: center;
    background: linear-gradient(122.07deg, #383F50 6.59%, #23252A 74.82%);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
    border-radius: 10px;
    h1 {
      font-size: 2.4rem;
      margin: 0 0 .5rem;
    }

    h3 {
      font-size: 2rem;
      color: $col-placeholder;
      margin: 0;
    }
    
  }
  .log-in-header {
    img {
      max-width: 35px;
    }
    h1 {
      font-size: 28px;
      margin-left: 25px;
      color: #fff;
    }
  }
</style>
