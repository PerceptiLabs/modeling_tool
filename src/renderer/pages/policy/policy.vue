<template lang="pug">
  .page_policy
    router-link(:to="{name: 'register'}").btn.btn--link Back to registarion
    .heading
      | h2 End-User License Agreement ("Agreement")
      p Last updated: 11/20/2018
    .intro
      p Please read this End-User License Agreement ("Agreement") carefully before clicking the "I Agree" button, downloading or using Percepti ("Application").
      p Perceptilabs AB ("PerceptiLabs") is a registered company (559112-8300) with headquarters in Stockholm, Sweden.
      p By clicking the "I Agree" button, downloading or using the Application, you are agreeing to be bound by the terms and conditions of this Agreement.
      p If you do not agree to the terms of this Agreement, do not click on the "I Agree" button and do not download or use the Application.
    .ordered-article
      h3 License
      p
        | PerceptiLabs grants you a revocable, non-exclusive, non-transferable, free limited license to download, install and use the Application solely for your personal, non-commercial purposes to test the Application internally within your company or at your own computer strictly in accordance with the terms of this Agreement.

        | Restrictions

        | You agree not to exploit or in any way commercializing the license, and you will not permit others to:

        | a)	license, sell, rent, lease, assign, distribute, transmit, host, outsource, disclose or otherwise commercially exploit the Application or make the Application available to any third party.
        | b)	decompile, reverse engineer, disassemble, attempt to derive the source code of, or decrypt the Application.
        | c)	Make any modification, adaptation, improvement, enhancement, translation or derivative work from our Application.
        | d)	Violate any applicable laws, rules or regulations in connection with Your access or use of the Application.
        | e)	Remove, alter or obscure any proprietary notice (including any notice of copyright or trademark) of PerceptiLabs or its affiliates, partners, suppliers or the licensor of the Application.
        | f)	Use the application for any purpose for which it is not designed or intended.
        | g)	Making the application available over a network or other environment permitting access or use by multiple users.
        | h)	Use the application for creating a product, service or software that is, directly or indirectly, competitive with or in any way a substitute for any service, product or software offered by PerceptiLabs.
        | i)	Use the Application to send automated queries to any website or to send any unsolicited commercial E-mail.
        | j)	Use any proprietary information or interfaces of PerceptiLabs or other intellectual property of PerceptiLabs in the design, development, manufacturing, licensing or distribution of any applications, accessories or devices for use with the Application.

        | Modifications to Application

        | PerceptiLabs reserves the right to modify, suspend or discontinue, temporarily or permanently, the Application or any service to which it connects, with or without notice and without liability to you.


        | Term and Termination

        | This Agreement shall remain in effect for a test period of three (3) months or until terminated by PerceptiLabs.

        | PerceptiLabs may, in its sole discretion, at any time and for any or no reason, suspend or terminate this Agreement with or without prior notice.

        | This Agreement will terminate immediately, without prior notice from PerceptiLabs, in the event that you fail to comply with any provision of this Agreement.

        | Upon termination of this Agreement, you shall cease all use of the Application and delete all copies of the Application from your device (including desktop).

        | Severability

        | If any provision of this Agreement is held to be unenforceable or invalid, such provision will be changed and interpreted to accomplish the objectives of such provision to the greatest extent possible under applicable law and the remaining provisions will continue in full force and effect.

        | Limitations of Liability
        | UNDER NO CIRCUMSTANCES SHALL PERCEPTILABS OR ITS AFFILIATED PARTNERS, SUPPLIERS OR LICENSORS BE LIABLE FOR ANY INDIRECT, INCIDENTAL, CONSQUENTIAL, SPECIAL OR EXAMPLARY DAMAGE ARISING OUT OF OR IN CONNECTION WITH YOUR ACCESS OR USE OF OR INABILITY TO ACCESS OR USE THE APPLICATION AND ANY THIRD PARTY CONTENT AND SERVICES. WHETHER OR NOT THE DAMAGE WERE FORSEEABLE AND WHETHER OR NOT PERCEPTILABS ADVICED OF THE POSSIBILITY OF SUCH DAMAGES. WITHOUT LIMITING THE GENERALITY OF THE FORGOING, PERCEPTILABS’S AGGREGATE LIABILITY TO YOU (WHETHER UNDER CONTRACT, TORT, STATUTE OR OTHERWISE) SHALL NOT EXCEED THE AMOUNT OF FIFTY DOLLARS ($50.00). THE FOREGOING LIMITATIONS WILL APPLY EVEN IF THE ABOVE STATED REMEDY FAILS OF ITS ESSENTIAL PURPOSE.


        | Amendments to this Agreement

        | PerceptiLabs reserves the right, at its sole discretion, to modify or replace this Agreement at any time.

        | Intellectual Property Rights

        | Copyright and other rights to the Application belong to PerceptiLabs AB. This Agreement does not imply that any other rights than the non-exclusive license to use the Application provided by the Agreement is transferred to you. This Agreement does not either imply that the ownership of the copy of the Application or the medium on which the Application has been delivered is transferred to you.

        | Infringement Acknowledgement
        | You and PerceptiLabs acknowledge and agree that, in the event of a third party claim that the Aplication or Your possession or use of the Application infringes any third party’s intellectual property rights, You (and not PerceptiLabs) will be responsible for the investigation, defense, settlement and discharge of any such claim of intellectual property infringement. You will, however, promptly notify PerceptiLabs in writing of such a claim.

        | Law and Dispute Resolution
        | A dispute will be handled by Swedish law (without regard to principles of conflict of laws) and the exclusive jurisdiction of the Swedish courts whereby the Stockholm District Court shall be the court of first instance. Swedish Procedural law shall be applied.

        | Contact Information
        | If you have any questions about this Agreement, please contact us.
        | Mail: contact@perceptilabs.com


</template>

<script>
export default {
  name: 'PagePolicy'
}
</script>

<style lang="scss" scoped>
  @import '../../scss/base';
  .page_policy {
    padding: 3rem;
    height: 100vh;
    background: linear-gradient(0deg, #23252A -1.66%, #2D2F35 100%);
    overflow: auto;
  }
</style>
