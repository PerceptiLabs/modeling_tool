<template lang="pug">
  main.page_login
    .login_logo
      img(src="./../../../../static/img/percepti-labs-logo.svg" alt="percepti labs logo")
    view-loading
    .login_main
      h1 Get Started
      h3 Register in 1 minute
      form.login_form
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
        //-.form_holder
          input(type="tel" placeholder="Phone"
            v-model="user.phone"
            name="Phone"
            v-mask="'+## (###) ###-##-##'"
            )
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
            button.btn.btn--link.policy-btn(@click="goToPolicyPage") terms and policy
          p.text-error(v-show="errors.has('terms')") {{ errors.first('terms') }}

        .form_holder
          button.btn.btn--dark-blue-rev(type="button" @click="validateForm" :disabled="isLoading || !terms") Register
        .form_holder
          router-link(:to="{name: 'login'}").btn.btn--link Already Have Account
</template>

<script>
  import {requestCloudApi}  from '@/core/apiCloud.js'
  import { baseUrlSite }    from '@/core/constants.js'
  import ViewLoading        from '@/components/different/view-loading.vue'
export default {
  name: 'PageRegister',
  components: {
    ViewLoading
  },
  mounted() {
    let preRegistrationData = JSON.parse(localStorage.getItem('registrationData'));
    if(preRegistrationData) this.user = preRegistrationData;
  },
  data() {
    return {
      user: {
        firstName: '',
        lastName: '',
        email: '',
        phone: '+00 (000) 000-00-00',
        password: '',
        callbackUrl: baseUrlSite
      },
      terms: true
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
          //console.log('result', result);
          if (result) {
            this.registryUser();
            return;
          }
          //error func
        })
        .catch((error)=>{
          console.log('error', error);
        })
    },
    registryUser() {
      this.$store.commit('mod_login/SET_showLoader', true);
      this.requestCloudApi('post', 'Customer/CreateGuest', this.user)
        .then((response)=>{
          this.$store.dispatch('globalView/GP_infoPopup', 'A confirmation email has been sent to your email. Follow the link to complete the registration.');
          this.$router.replace('/login');
          localStorage.removeItem('registrationData')
        })
        .catch((error)=>{
          this.$store.dispatch('globalView/GP_infoPopup', error);
        })
        .finally(()=>{
          this.$store.commit('mod_login/SET_showLoader', false);
        });
    },
    goToPolicyPage() {
      localStorage.setItem('registrationData', JSON.stringify(this.user));
      this.$router.push({name: 'policy'});
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';
  .policy-btn{
    margin-left: 1rem;
  }
</style>
