<template lang="pug">
  logout-user-page-wrap(
    title-page="Log in please"
    sub-title="Enter your Email & Password"
  )
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

      .form_holder.login-form_actions
        .form_row
          base-checkbox(v-model="saveToken") Remember me
          button.btn.btn--dark-blue-rev(type="button" @click="validateForm" :disabled="isLoading") Log in
      .form_holder
        router-link.btn.btn--link(:to="{name: 'register'}") Register new account

</template>

<script>
  import { baseUrlSite }    from '@/core/constants.js'
  import { goToLink, encryptionData }       from '@/core/helpers.js'

  import LogoutUserPageWrap from '@/pages/logout-user-page-wrap.vue'

export default {
  name: 'PageLogin',
  components: { LogoutUserPageWrap },
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
  },
  methods: {
    toLink(url) {
      goToLink(url)
    },
    validateForm() {
      this.$validator.validateAll()
        .then((result)=> {
          if (result) {
            this.requestLoginUser();
            return;
          }
      });
    },
    requestLoginUser() {
      this.$store.commit('mod_login/SET_showLoader', true);
      let dataParams = {
        "Email": this.userEmail,
        "Password": this.userPass
      };
      this.$store.dispatch('mod_apiCloud/CloudAPI_userLogin', dataParams)
        .then((tokens)=>{if(this.saveToken) localStorage.setItem('currentUser', JSON.stringify(tokens))})
        .catch((error)=>{console.log(error)})
        .finally(()=>   {this.$store.commit('mod_login/SET_showLoader', false)});
    },
  }
}
</script>
<style lang="scss" scoped>
  .forgot-password-box{
    margin-top: 1rem;
    text-align: left;
  }
</style>
