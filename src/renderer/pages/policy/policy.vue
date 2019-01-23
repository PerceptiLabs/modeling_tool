<template lang="pug">
  main.page_login
    .login_logo
      img(src="~@/assets/percepti-labs-logo.svg" alt="percepti labs logo")
    .page_policy
      router-link(:to="{name: 'register'}").btn.btn--dark-blue-rev Back
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
export default {
  name: 'PagePolicy'
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';
  .page_policy {
    position: relative;
    width: auto;
    max-width: 100rem;
    text-align: left;
    border: 1px solid $login-blue;
    background: #161719;
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
</style>
