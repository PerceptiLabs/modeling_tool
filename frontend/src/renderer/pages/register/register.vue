<template lang="pug">
  div
    div.wrapper
      form.left-wrapper(@keyup.enter="validateForm" )
        img.site-logo(src="./../../../../static/img/perceptilabs-new-log.svg")
        .form_holder
            input.new-ui(type="text" placeholder="First Name"
              v-model="user.firstName"
              name="First Name"
              v-validate="'required|alpha_spaces'"
              )
            p.text-error(v-show="errors.has('First Name')") {{ errors.first('First Name') }}
        .form_holder
          input.new-ui(type="text" placeholder="Last Name"
            v-model="user.lastName"
            name="Last Name"
            v-validate="'required|alpha_spaces'"
            )
          p.text-error(v-show="errors.has('Last Name')") {{ errors.first('Last Name') }}
        .form_holder
          input.new-ui(type="email" placeholder="Email"
            v-model="user.email"
            name="Email"
            v-validate="'required|email'"
            )
          p.text-error(v-show="errors.has('Email')") {{ errors.first('Email') }}
        .form_holder
          .relative
            input.new-ui(
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
            input.new-ui(:type="passwordVisibility.confirmPassword ? 'text' : 'password'" placeholder="Confirm password"
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
        .form_holder.d-flex.flex-column.align-items-center
          base-checkbox.terms-policy(
            v-validate="'required'"
            data-vv-name="terms"
            label="terms"
            v-model="terms"
            :isNewUi="true"
          )
            span.fz-12 Agree to
            button.btn.btn--link.policy-btn.fz-12.blue-link(type="button"
              @click="toPolicy"
              ) terms and policy
          p.text-error(v-show="errors.has('terms')") {{ errors.first('terms') }}

          base-checkbox.terms-policy(
            v-validate="'required'"
            data-vv-name="communicationsConsent"
            label="communicationsConsent"
            v-model="communicationsConsent"
            :isNewUi="true"
          )
            span.fz-12 Agree to
            button.btn.btn--link.policy-btn.fz-12.blue-link(type="button"
              @click="toCommunicationsPolicy"
              ) receive communications
          p.text-error(v-show="errors.has('communicationsConsent')") {{ errors.first('communicationsConsent') }}
    
        //- .form_holder
        //-   .form_row
        //-     span.gdpr-text By clicking Sign up below, you consent to allow PerceptiLabs to store and process the personal information submitted above to provide you the content requested.
        .form_holder
          .form_row
            span
            button.btn.btn--dark-blue-rev.sign-up-btn(type="button"
              :disabled="isLoading || !terms"
              @click="validateForm"
              ) Sign up
        .form_holder.fz-12.text-center
          span Already a user? 
          a.btn.btn--link.blue-link(@click="setActivePageAction(MODAL_PAGE_SIGN_IN)") Log in here
    
      div.description-box.d-flex.flex-column.justify-content-center
        .video-box-wrapper
          img.chrome-image(src="./../../../../static/img/chrome.png")
          video(autoplay="autoplay" muted="muted" loop="loop" class="video")
            source(src="./../../../../static/video/sign-up-video.mp4")
        h1.head-text Ready to build with out visual modeling tool?
        div.info-text.text-center Sign up to start building your model. <br/> It’s <span class='white-text'>all free</span> in our browser-based tool. You will also <br/> <span class='white-text'>receive updates</span> on our changelog!
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
  import { googleAnalytics } from '@/core/analytics';
  import {requestCloudApi}  from '@/core/apiCloud.js'
  import { baseUrlSite }    from '@/core/constants.js'
  import Analytics          from '@/core/analytics.js'

  import LogoutUserPageWrap from '@/pages/logout-user-page-wrap.vue'
  import PolicyLogin        from '@/pages/register/policy.vue'
  import CommunicationsPolicy from '@/pages/register/communications-policy.vue'
  import {mapActions} from "vuex";
  import {MODAL_PAGE_SIGN_IN} from "@/core/constants";
  

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
      isShowPolicy: false,
      communicationsConsent: true,
      showPolicy: false,
      showCommuncationsPolicy: false,
      passwordVisibility: {
        password: false,
        confirmPassword: false,
      },
      MODAL_PAGE_SIGN_IN,
    }
  },
  computed: {
    isLoading() {
      return this.$store.state.mod_login.showLoader
    },
  },
  methods: {
    ...mapActions({
      setActivePageAction: 'modal_pages/setActivePageAction',
    }),
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
      googleAnalytics.trackCustomEvent('register');
      this.$store.commit('mod_login/SET_showLoader', true);

      this.$store.dispatch('mod_apiCloud/CloudAPI_userCreate', this.user)
        .then((response)=> {
          Analytics.hubSpot.trackUserRegistration({
            email: this.user.email,
            firstName: this.user.firstName,
            lastName: this.user.lastName,
            communicationsConsent: this.communicationsConsent
          });
          this.setActivePageAction(MODAL_PAGE_SIGN_IN);
        })
        .catch((err)=> {
          console.log(err);
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

  * {
    font-family: "Nunito Sans";
  }
  .policy-btn {
    margin-left: .3em;
  }
  .wrapper {
    width: 1192px;
    height: 592px;
    // background: #272C37;
    backdrop-filter: blur(20px);
    overflow-y: auto;
    display: flex;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    border-radius: 2px;
  }
  .left-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(-60deg, #383F50 0.73%, #23252A 100%);
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
    border-radius: 2px;
    padding: 0 100px 0 80px;
    width: 480px;
  }
  .site-logo {
    margin-bottom: 40px;
  }
  .description-box {
    width: 57%;
    // margin-right: 70px;
    background-image: url(./../../../../static/img/video-bg.jpg);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .video-box-wrapper {
    position: relative;
    margin-top: 40px;
  }
  .chrome-image {
    position: absolute;
    top: -23px;
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

  .logo-box {
    margin-bottom: 50px;
  }
  .head-text {
    margin-top: 20px;
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    line-height: 25px;
  }
  .info-text {
    color: #C4C4C4;
    font-size: 16px;
    line-height: 22px;
    margin-top: 10px;
    span {
      color: white;
    }
  }

  .gdpr-text {
    font-size: 1rem;
  }

  .sign-up-btn {
    width: 100%;
    height: 35px;
    font-weight: bold;
    background: #6185EE;
    border-radius: 20px;
    &:hover {
      color: #fff;
    }

  }
  .terms-policy {
    color: #fff;
    margin-bottom: 8px;
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
  .fz-12 {
    font-size: 12px;
  }
  .text-center {
    text-align: center;
  }
  .blue-link {
    color: #9BB2F6;
  }
  .video {
    margin: 0;
    padding: 0;
    width: 480px;
  }
  .text-error {
    margin-top: 4px;
    padding-left: 20px;
    padding-right: 20px;
    font-size: 12px;
    text-align: center;
    margin-bottom: 0;
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
