<template lang="pug">
  main.page_login
    .login_logo
      img(src="~@/assets/percepti-labs-logo.svg" alt="percepti labs logo")
    view-loading
    .login_main
      h1 Log In please
      h3 Enter your Email & Password
      form.login_form
        .form_holder
          input(type="email" placeholder="Email"
            v-model="userEmail"
            name="Email"
            v-validate="'required|email'"
            )
          p.text-error(v-show="errors.has('Email')") {{ errors.first('Email') }}
        .form_holder
          input(type="password" placeholder="Password"
            v-model="userPass"
            name="Password"
            v-validate="'required|min:6'"
            )
          p.text-error(v-show="errors.has('Password')") {{ errors.first('Password') }}
        .form_holder
          base-checkbox(

          ) Remember me
        .form_holder
          button.btn.btn--dark-blue-rev(type="button" @click="validateForm" :disabled="isLoading") log in
        .form_holder
          router-link.btn.btn--link(:to="{name: 'register'}") Register new account

          router-link.btn.btn--link(:to="{name: 'projects'}" style="margin-left: 10px") Projects
</template>

<script>
  import {requestCloudApi} from '@/core/apiCloud.js'
  import ViewLoading from '@/components/loading/view-loading.vue'
export default {
  name: 'PageLogin',
  components: {
    ViewLoading
  },
  data() {
    return {
      userEmail: 'test@test.com',
      userPass: '123123',
      //userEmail: '',
      //userPass: ''
    }
  },
  computed: {
    isLoading() {
      return this.$store.state.mod_login.showLoader
    },
  },
  methods: {
    requestCloudApi,
    validateForm() {
      this.$validator.validateAll()
        .then((result) => {
          if (result) {
            this.loginUser();
            return;
          }
          //error func
      });
    },
    loginUser() {
      this.$store.commit('mod_login/SET_showLoader', true);
      let queryParams = {
        "Email": this.userEmail,
        "Password": this.userPass
      };
      this.requestCloudApi('post', 'Customer/Login', queryParams, (result, response) => {
        this.$store.commit('mod_login/SET_showLoader', false);
        if (result === 'success') {
          this.$store.commit('globalView/SET_userToken', response.headers.authorization);
          this.$router.replace('/app');
        }
      })
    },
  }
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';
</style>
