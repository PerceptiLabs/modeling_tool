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
          base-checkbox(v-model="saveToken") Remember me
        .form_holder
          button.btn.btn--dark-blue-rev(type="button" @click="validateForm" :disabled="isLoading") log in
        .form_holder
          router-link.btn.btn--link(:to="{name: 'register'}") Register new account

</template>

<script>
  import {requestCloudApi} from '@/core/apiCloud.js'
  import ViewLoading from '@/components/loading/view-loading.vue'
export default {
  name: 'PageLogin',
  components: {
    ViewLoading
  },
  mounted() {
    if(this.userIsLogin) {
      this.loginUser()
    }
  },
  data() {
    return {
      // userEmail: 'test@test.com',
      // userPass: '123123',
      userEmail: '',
      userPass: '',
      saveToken: true
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
      this.requestCloudApi('post', 'Customer/Login', queryParams, (result, response) => {
        if (result === 'success') {
          this.$store.commit('mod_login/SET_showLoader', false);
          let token = response.data.data.token;
          this.$store.dispatch('globalView/SET_userToken', token);
          if(this.saveToken) {
            localStorage.setItem('userToken', token);
          }
          this.loginUser()
        }
        else {
          this.$store.commit('mod_login/SET_showLoader', false);
          alert("Bed request, please try again");
        }
      })
    },

    loginUser() {
      this.$router.replace('/projects');
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';
</style>
