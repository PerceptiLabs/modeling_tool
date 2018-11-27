<template lang="pug">
  main.page_login
    .login_logo
      img(src="~@/assets/percepti-labs-logo.svg" alt="percepti labs logo")
    .login_main
      h1 Log In please
      h3 Enter your Email & Password
      form.login_form
        .form_holder
          input(type="email" placeholder="Email"
            v-model="userEmail"
            name="Email"
            )
          //v-validate="'required|email'"
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
          //router-link.btn.btn--dark-blue-rev(type="button" :to="{name: 'app'}") log in
          button.btn.btn--dark-blue-rev(type="button" @click="validateForm") log in
        .form_holder
          router-link.btn.btn--link(:to="{name: 'register'}") Register new account
</template>

<script>
  import {requestCloudApi} from '@/core/apiCloud.js'
export default {
  name: 'PageLogin',
  data() {
    return {
      userEmail: 'string',
      userPass: 'string'
    }
  },
  computed: {
    // infoText() {
    //   return this.$store.state.globalView.globalPopup.showInfoPopup
    // },
    // eventLoadNetwork() {
    //   return this.$store.state.mod_events.openNetwork
    // },
    // eventSaveNetwork() {
    //   return this.$store.state.mod_events.saveNetwork
    // },
    // currentNetwork() {
    //   return this.$store.getters['mod_workspace/currentNetwork']
    // },
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
      let queryParams = {
        "Email": "string",
        "Password": "string"
      };
      this.requestCloudApi('post', 'Customer/Login', queryParams, (result, response) => {
        if (result === 'success') {
          console.log(response);
          this.$router.replace('/app');
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';

</style>
