<template lang="pug">
  main.page_login
    .login_logo
      img(src="./../../../../static/img/percepti-labs-logo.svg" alt="percepti labs logo")
    view-loading
    .login_main(v-if="!isShowPolicy")
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
            button.btn.btn--link.policy-btn(@click="showHidePolicy") terms and policy
          p.text-error(v-show="errors.has('terms')") {{ errors.first('terms') }}

        .form_holder
          button.btn.btn--dark-blue-rev(type="button" @click="validateForm" :disabled="isLoading || !terms") Register
        .form_holder
          router-link(:to="{name: 'login'}").btn.btn--link Already Have Account

    .policy(v-else)
      .btn.btn--dark-blue-rev(@click="showHidePolicy") Back
      article.policy_main
        header
          h2 End-User License Agreement ("Agreement")
          time Last updated: 11/20/2018
          p
        .policy_intro
          p Please read this End-User License Agreement ("Agreement") carefully before clicking the "I Agree" button, downloading or using Percepti ("Application").
          p Perceptilabs AB ("PerceptiLabs") is a registered company (559112-8300) with headquarters in Stockholm, Sweden.
          p By clicking the "I Agree" button, downloading or using the Application, you are agreeing to be bound by the terms and conditions of this Agreement.
          p If you do not agree to the terms of this Agreement, do not click on the "I Agree" button and do not download or use the Application.
        .policy_article
          h3 License
          p PerceptiLabs grants you a revocable, non-exclusive, non-transferable, free limited license to download, install and use the Application solely for your personal, non-commercial purposes to test the Application internally within your company or at your own computer strictly in accordance with the terms of this Agreement.
          h3 Restrictions
          p You agree not to exploit or in any way commercializing the license, and you will not permit others to:
          ul
            li a)	license, sell, rent, lease, assign, distribute, transmit, host, outsource, disclose or otherwise commercially exploit the Application or make the Application available to any third party.
            li b)	decompile, reverse engineer, disassemble, attempt to derive the source code of, or decrypt the Application.
            li c)	Make any modification, adaptation, improvement, enhancement, translation or derivative work from our Application.
            li d)	Violate any applicable laws, rules or regulations in connection with Your access or use of the Application.
            li e)	Remove, alter or obscure any proprietary notice (including any notice of copyright or trademark) of PerceptiLabs or its affiliates, partners, suppliers or the licensor of the Application.
            li f)	Use the application for any purpose for which it is not designed or intended.
            li g)	Making the application available over a network or other environment permitting access or use by multiple users.
            li h)	Use the application for creating a product, service or software that is, directly or indirectly, competitive with or in any way a substitute for any service, product or software offered by PerceptiLabs.
            li i)	Use the Application to send automated queries to any website or to send any unsolicited commercial E-mail.
            li j)	Use any proprietary information or interfaces of PerceptiLabs or other intellectual property of PerceptiLabs in the design, development, manufacturing, licensing or distribution of any applications, accessories or devices for use with the Application.

          h3 Modifications to Application
          p PerceptiLabs reserves the right to modify, suspend or discontinue, temporarily or permanently, the Application or any service to which it connects, with or without notice and without liability to you.

          h3 Term and Termination
          p This Agreement shall remain in effect for a test period of three (3) months or until terminated by PerceptiLabs.
          p PerceptiLabs may, in its sole discretion, at any time and for any or no reason, suspend or terminate this Agreement with or without prior notice.
          p This Agreement will terminate immediately, without prior notice from PerceptiLabs, in the event that you fail to comply with any provision of this Agreement.
          p Upon termination of this Agreement, you shall cease all use of the Application and delete all copies of the Application from your device (including desktop).
          h3 Severability
          p If any provision of this Agreement is held to be unenforceable or invalid, such provision will be changed and interpreted to accomplish the objectives of such provision to the greatest extent possible under applicable law and the remaining provisions will continue in full force and effect.
          h3 Limitations of Liability
          p UNDER NO CIRCUMSTANCES SHALL PERCEPTILABS OR ITS AFFILIATED PARTNERS, SUPPLIERS OR LICENSORS BE LIABLE FOR ANY INDIRECT, INCIDENTAL, CONSQUENTIAL, SPECIAL OR EXAMPLARY DAMAGE ARISING OUT OF OR IN CONNECTION WITH YOUR ACCESS OR USE OF OR INABILITY TO ACCESS OR USE THE APPLICATION AND ANY THIRD PARTY CONTENT AND SERVICES. WHETHER OR NOT THE DAMAGE WERE FORSEEABLE AND WHETHER OR NOT PERCEPTILABS ADVICED OF THE POSSIBILITY OF SUCH DAMAGES. WITHOUT LIMITING THE GENERALITY OF THE FORGOING, PERCEPTILABS’S AGGREGATE LIABILITY TO YOU (WHETHER UNDER CONTRACT, TORT, STATUTE OR OTHERWISE) SHALL NOT EXCEED THE AMOUNT OF FIFTY DOLLARS ($50.00). THE FOREGOING LIMITATIONS WILL APPLY EVEN IF THE ABOVE STATED REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
          h3 Amendments to this Agreement
          p PerceptiLabs reserves the right, at its sole discretion, to modify or replace this Agreement at any time.
          h3 Intellectual Property Rights
          p Copyright and other rights to the Application belong to PerceptiLabs AB. This Agreement does not imply that any other rights than the non-exclusive license to use the Application provided by the Agreement is transferred to you. This Agreement does not either imply that the ownership of the copy of the Application or the medium on which the Application has been delivered is transferred to you.
          h3 Infringement Acknowledgement
          p You and PerceptiLabs acknowledge and agree that, in the event of a third party claim that the Aplication or Your possession or use of the Application infringes any third party’s intellectual property rights, You (and not PerceptiLabs) will be responsible for the investigation, defense, settlement and discharge of any such claim of intellectual property infringement. You will, however, promptly notify PerceptiLabs in writing of such a claim.
          h3 Law and Dispute Resolution
          p A dispute will be handled by Swedish law (without regard to principles of conflict of laws) and the exclusive jurisdiction of the Swedish courts whereby the Stockholm District Court shall be the court of first instance. Swedish Procedural law shall be applied.
          footer
            h3 Contact Information
            p If you have any questions about this Agreement, please contact us.
            p Mail:
              a.btn.btn--link(href="mailto:contact@perceptilabs.com")  contact@perceptilabs.com
</template>

<script>
  import {requestCloudApi}  from '@/core/apiCloud.js'
  import ViewLoading        from '@/components/different/view-loading.vue'
export default {
  name: 'PageRegister',
  components: {
    ViewLoading
  },
  data() {
    return {
      user: {
        firstName: '',
        lastName: '',
        email: '',
        phone: '+00 (000) 000-00-00',
        password: '',
        confirmPassword:'',
        isLoading: false
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
        })
        .catch((error)=>{
          this.$store.dispatch('globalView/GP_infoPopup', error);
        })
        .finally(()=>{
          this.$store.commit('mod_login/SET_showLoader', false);
        });
    },
    showHidePolicy() {
      this.isShowPolicy = !this.isShowPolicy;
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';
  .policy {
    position: relative;
    width: auto;
    max-width: 100rem;
    text-align: left;
    border: 1px solid $login-blue;
    background: #161719;
    margin-top: 2rem;
  }
  .policy_main {
    overflow: auto;
    max-height: 55vh;
    padding: 9rem 7.5rem 7.5rem;
  }
  .btn--dark-blue-rev {
    font-size: 1em;
    position: absolute;
    top: 0;
    left: 50%;
    display: inline-block;
    width: auto;
    padding: 1.7rem 6rem;
    transform: translate(-50%, -50%);
    text-align: center;
    text-transform: uppercase;
    border-radius: 0;
  }
  .btn--link {
    color: $login-blue;
    text-decoration: underline;

    text-decoration-skip: ink;
    &:hover {
      text-decoration: none;
    }
  }
  .policy-btn{
    margin-left: 1rem;
  }
</style>
