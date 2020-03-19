<template lang="pug">
  div.wrapper.d-flex.justify-content-center
    div.d-flex.flex-column.align-self-center
      div.sign-up-wrapper.d-flex
        div.description-box.d-flex.flex-column.justify-content-center
          div.logo-box.d-flex
            img(src="../../../../static/img/perceptilabs-logo-icon.svg" alt="PerceptiLabs logo")
            h1.head-text Ready to build with out visual modeling tool?
          div.info-text Sign up to start building your model. It’s <span class='white-text'>all free</span> in our browser-based tool. You will also <span class='white-text'>receive updates</span> on our changelog!
        form.login_form(@keyup.enter="validateForm")
          h2.form-caption Get Started
          div.d-flex
            .form_holder.mr15
              input(type="text" placeholder="First Name"
                v-model="user.firstName"
                name="First Name"
                v-validate="'required|alpha_spaces'"
                )
              p.text-error(v-show="errors.has('First Name')") {{ errors.first('First Name') }}
            .form_holder
              input(type="text" placeholder="Last Name"
                v-model="user.lastName"
                name="Last Name"
                v-validate="'required|alpha_spaces'"
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
            .relative
              input(
                :type="passwordVisibility.password ? 'text' : 'password'"
                placeholder="Password"
                v-model="user.password"
                name="Password"
                v-validate="'required|min:6'"
                ref="userPass")
              img.show-hide-password-icon(
                src="../../../../static/img/inputs/show-hide.png" 
                alt="show-hide-password"
                @click="togglePasswordVisibility('password')"
                )
            p.text-error(v-show="errors.has('Password')") {{ errors.first('Password') }}
          .form_holder
            .relative
              input(:type="passwordVisibility.confirmPassword ? 'text' : 'password'" placeholder="Confirm password"
                v-model="user.confirmPassword"
                name="Confirm password"
                v-validate="'required|confirmed:userPass'"
                data-vv-as="Password"
                )
              img.show-hide-password-icon(
                src="../../../../static/img/inputs/show-hide.png" 
                alt="show-hide-password"
                @click="togglePasswordVisibility('confirmPassword')"
                )
            p.text-error(v-show="errors.has('Confirm password')") {{ errors.first('Confirm password') }}

          .form_holder
            base-checkbox.terms-policy(
              v-validate="'required'"
              data-vv-name="terms"
              label="terms"
              v-model="terms"
            )
              span.fz-16 Agree to
              button.btn.btn--link.policy-btn.fz-16(type="button"
                @click="toPolicy"
                ) terms and policy
            p.text-error(v-show="errors.has('terms')") {{ errors.first('terms') }}

            base-checkbox.terms-policy(
              v-validate="'required'"
              data-vv-name="communicationsConsent"
              label="communicationsConsent"
              v-model="communicationsConsent"
            )
              span.fz-16 Agree to
              button.btn.btn--link.policy-btn.fz-16(type="button"
                @click="toCommunicationsPolicy"
                ) receive communications
            p.text-error(v-show="errors.has('communicationsConsent')") {{ errors.first('communicationsConsent') }}
        
          .form_holder
            .form_row
              span
              button.btn.btn--dark-blue-rev.sign-up-btn(type="button"
                :disabled="isLoading || !terms || !communicationsConsent"
                @click="validateForm"
                ) Sign up
          .form_holder.fz-16.italic
            span Already Have Account? 
            router-link.btn.btn--link(:to="{name: 'login'}") Log in here
        
        policy-login(
          v-show="showPolicy"
          @backToRegister="toRegister"
          )

        communications-policy(
          v-show="showCommuncationsPolicy"
          @backToRegister="toRegister"
          )

</template>

<script>
  import {requestCloudApi}    from '@/core/apiCloud.js'
  import { baseUrlSite }      from '@/core/constants.js'

  import LogoutUserPageWrap   from '@/pages/logout-user-page-wrap.vue'
  import PolicyLogin          from '@/pages/register/policy.vue'
  import CommunicationsPolicy from '@/pages/register/communications-policy.vue'

export default {
  name: 'PageRegister',
  components: { PolicyLogin, CommunicationsPolicy, LogoutUserPageWrap },
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
      communicationsConsent: true,
      showPolicy: false,
      showCommuncationsPolicy: false,
      passwordVisibility: {
        password: false,
        confirmPassword: false,
      }
    }
  },
  computed: {
    isLoading() {
      return this.$store.state.mod_login.showLoader
    },
  },
  methods: {
    togglePasswordVisibility(fieldName) {
      this.passwordVisibility[fieldName] = !this.passwordVisibility[fieldName];
    },
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
        .then((response)=> this.$router.replace('/login'))
        .catch((err)=> {
          console.log(err)
        })
        .finally(()=> this.$store.commit('mod_login/SET_showLoader', false));
    },
    toCommunicationsPolicy() {
      this.showPolicy = false;
      this.showCommuncationsPolicy = true;
    },
    toPolicy() {
      this.showPolicy = true;
      this.showCommuncationsPolicy = false;
    },
    toRegister() {
      this.showPolicy = false;
      this.showCommuncationsPolicy = false;
    },
  }
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';
  .policy-btn {
    margin-left: .3em;
  }
  .wrapper {
    background: #272C37;
    backdrop-filter: blur(20px);
  }
  .login_form {
    padding-top: 0;
    input {
      height: 40px;
    }
    .form_holder {
      margin-bottom: 15px;
    }
  }
  .form-caption {
    font-size: 28px;
    margin-bottom: 30px;
    color: #fff;
  }
  .sign-up-wrapper {
    margin: 0 auto;
    max-width: 849px;
    padding: 40px 50px 50px 65px;
    background: linear-gradient(135.16deg, #383F50 14.59%, #23252A 73.87%);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
    border-radius: 10px;
  }
  .login_form {
    width: 45%;
  }
  .description-box {
    width: 57%;
    margin-right: 70px;
  }
  .logo-box {
    margin-bottom: 50px;
  }
  .head-text {
    font-size: 28px;
    line-height: 39px;
    margin-left: 26px;
    color: #fff;
  }
  .info-text {
    color: #C4C4C4;
    font-size: 20px;
    line-height: 28px;
    span {
      color: white;
    }
  }
  .sign-up-btn {
    width: 100%;
    height: 35px;
    font-weight: bold;

  }
  .terms-policy {
    color: #fff;
  }
  .mr15 {
    margin-right: 15px;
  }
  .fz-16 {
    font-size: 16px;
  }
  .italic {
    font-style: italic;
  }
  .mb-30 {
    margin-bottom: 30px;
  }
  .relative {
    position: relative;
  }
  .show-hide-password-icon {
    cursor: pointer;
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
  }
  // if it should require to autofilled field should look the same as default input's
  /*input:-webkit-autofill,*/
  /*input:-webkit-autofill:hover,*/
  /*input:-webkit-autofill:focus, {*/
  /*  -webkit-box-shadow: 0 0 0px 1000px #383F50 inset;*/
  /*  border: 1px solid #6E92FA;*/
  /*  -webkit-text-fill-color: #E1E1E1;*/
  /*}*/
</style>
