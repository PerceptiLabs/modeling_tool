<template lang="pug">
  logout-user-page-wrap.page_login(
    title-page="Get Started"
    sub-title="Register in 1 minute"
  )
    form.login_form(@keyup.enter="validateForm")
      .form_holder
        input(type="text" placeholder="First Name"
          v-model="user.firstName"
          name="First Name"
          v-validate="'alpha_spaces'"
          )
        p.text-error(v-show="errors.has('First Name')") {{ errors.first('First Name') }}
      .form_holder
        input(type="text" placeholder="Last Name"
          v-model="user.lastName"
          name="Last Name"
          v-validate="'alpha_spaces'"
          )
        p.text-error(v-show="errors.has('Last Name')") {{ errors.first('Last Name') }}
      .form_holder
        input(type="email" placeholder="Email"
          v-model="user.email"
          name="Email"
          v-validate="'required|email'"
          )
        p.text-error(v-show="errors.has('Email')") {{ errors.first('Email') }}
      .form_holder
        input(type="password" placeholder="Password"
          v-model="user.password"
          name="Password"
          v-validate="'required|min:6'"
          ref="userPass")
        p.text-error(v-show="errors.has('Password')") {{ errors.first('Password') }}
      .form_holder
        input(type="password" placeholder="Confirm password"
          v-model="user.confirmPassword"
          name="Confirm password"
          v-validate="'required|confirmed:userPass'"
          data-vv-as="Password"
          )
        p.text-error(v-show="errors.has('Confirm password')") {{ errors.first('Confirm password') }}
      .form_holder
        base-checkbox(
          v-validate="'required'"
          data-vv-name="terms"
          label="terms"
          v-model="terms"
        )
          span Agree
          button.btn.btn--link.policy-btn(@click="toPolicy" type="button") terms and policy
        p.text-error(v-show="errors.has('terms')") {{ errors.first('terms') }}

      .form_holder.login-form_actions
        .form_row
          span
          button.btn.btn--dark-blue-rev(type="button" @click="validateForm" :disabled="isLoading || !terms") Register
      .form_holder
        router-link.btn.btn--link(:to="{name: 'login'}") Already Have Account

    policy-login(
      v-show="isShowPolicy"
      @backToRegister="toRegister"
      )

</template>

<script>
  import { baseUrlSite }    from '@/core/constants.js'

  import LogoutUserPageWrap from '@/pages/logout-user-page-wrap.vue'
  import PolicyLogin        from '@/pages/register/policy.vue'

export default {
  name: 'PageRegister',
  components: { PolicyLogin, LogoutUserPageWrap },
  data() {
    return {
      user: {
        firstName: '',
        lastName: '',
        email: '',
        phone: '+00 (000) 000-00-00',
        password: '',
        callbackUrl: baseUrlSite,
        confirmPassword:'',
      },
      terms: true,
      isShowPolicy: false
    }
  },
  computed: {
    isLoading() {
      return this.$store.state.mod_login.showLoader
    },
  },
  methods: {
    validateForm() {
      this.$validator.validateAll()
        .then((result) => {
          if (result) {
            this.registryUser();
            return;
          }
        })
        .catch((error)=>{
          console.log('error', error);
        })
    },
    registryUser() {
      this.$store.commit('mod_login/SET_showLoader', true);

      this.$store.dispatch('mod_apiCloud/CloudAPI_userCreate', this.user)
        .then((response)=>{
          this.$router.replace('/login');
        })
        // .catch((error)=> {
        //   this.$store.dispatch('globalView/GP_infoPopup', error);
        // })
        .finally(()=> {
          this.$store.commit('mod_login/SET_showLoader', false);
        });
    },
    toPolicy() {
      this.isShowPolicy = true;
    },
    toRegister() {
      this.isShowPolicy = false;
    },
  }
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';
  .policy-btn{
    margin-left: 1rem;
  }
</style>
