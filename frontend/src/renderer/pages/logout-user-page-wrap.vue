<template lang="pug">
  main.page_login
    .login_logo
      img(src="./../../../static/img/perceptilabs-logo-icon.svg" alt="PerceptiLabs logo")
    view-loading
    .login_main
      h1(v-if="titlePage.length") {{ titlePage }}
      h3(v-if="subTitle.length") {{ subTitle }}
      slot


</template>

<script>
  import ViewLoading from '@/components/different/view-loading.vue'

export default {
  name: 'LogoutUserPageWrap',
  components: { ViewLoading },
  props: {
    titlePage: { type: String, default: '' },
    subTitle: { type: String, default: '' },
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
    //justify-content: center;
    padding: 3rem;
    background: linear-gradient(0deg, $bg-workspace -1.66%, #2d2f35 100%);
    overflow-y: auto !important;
  }

  .login_logo {
    margin-bottom: 2rem;
  }

  .login_main {
    position: relative;
    width: 49rem;
    border-radius: 2*$bdrs;
    padding: 4.6rem;
    text-align: center;
    border: 1px solid $login-blue;
    background: linear-gradient(180deg, $bg-workspace 0%, #2d2f35 100%);

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
</style>
