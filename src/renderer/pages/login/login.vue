<template lang="pug">
  main.page_login
    .login_logo
      img(src="./../../../../static/img/percepti-labs-logo.svg" alt="percepti labs logo")
    view-loading
    .login_main
      h1 Log In please
      h3 Enter your Email & Password
      form.login_form(@keyup.enter="validateForm")
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
          .forgot-password-box
            a.btn.btn--link-without-underline(
              :href="`${baseUrlSite}/restore-account`"
              @click.prevent="toLink(`${baseUrlSite}/restore-account`)"
              ) Forgot password?

        .form_holder
          base-checkbox(v-model="saveToken") Remember me
        .form_holder
          button.btn.btn--dark-blue-rev(type="button" @click="validateForm" :disabled="isLoading") log in
        .form_holder
          router-link.btn.btn--link(:to="{name: 'register'}") Register new account

</template>

<script>

  import {requestCloudApi}  from '@/core/apiCloud.js'
  import { baseUrlSite }    from '@/core/constants.js'
  import { goToLink }       from '@/core/helpers.js'

  import ViewLoading from '@/components/different/view-loading.vue'

export default {
  name: 'PageLogin',
  components: { ViewLoading },
  mounted() {
    if(this.userIsLogin) {
      this.loginUser()
    }
  },
  data() {
    return {
      userEmail: '',
      userPass: '',
      saveToken: true,
      baseUrlSite
    }
  },
  computed: {
    isLoading() {
      return this.$store.state.mod_login.showLoader
    },
    userIsLogin() {
      return this.$store.state.globalView.userToken
    },
  },
  methods: {
    requestCloudApi,
    toLink(url) {
      goToLink(url)
    },
    validateForm() {
      this.$validator.validateAll()
        .then((result) => {
          if (result) {
            this.requestLoginUser();
            return;
          }
      });
    },
    requestLoginUser() {
      this.$store.commit('mod_login/SET_showLoader', true);
      let queryParams = {
        "Email": this.userEmail,
        "Password": this.userPass
      };
      this.requestCloudApi('post', 'Customer/Login', queryParams)
        .then((response)=>{
          let token = parseJwt(response.data.data.token);
          this.$store.dispatch('globalView/SET_userToken', token.unique_name);
          if(this.saveToken) {
            localStorage.setItem('userId', token.unique_name);
            localStorage.setItem('userToken', response.data.data.token);
          }
          this.loginUser()
        })
        .catch((error)=>{
          this.$store.dispatch('globalView/GP_infoPopup', error);
        })
        .finally(()=>{
          this.$store.commit('mod_login/SET_showLoader', false);
        });

      function parseJwt(token) {
        var base64Url = token.split('.')[1];
        var base64 = base64Url.replace('-', '+').replace('_', '/');
        return JSON.parse(window.atob(base64));
      }
    },

    loginUser() {
      this.$router.replace('/projects');
    },
  }
}
</script>
