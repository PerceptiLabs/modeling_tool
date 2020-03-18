<template lang="pug">
  .policy
    button.btn.btn--dark-blue-rev.back(
      type="button"
      @click="backToRegister") Back
    .policy_main
      article.policy_main-article
        header
          h2 NOTICE AND CONSENT / LEGITIMATE INTEREST
          h2 IMPORTANT- READ CAREFULLY
          time Last updated: 03/17/2020
          p
        .policy_intro
          p PerceptiLabs is committed to protecting and respecting your privacy, and we’ll only use your personal information to administer your account and to provide the products and services you requested from us. From time to time, we would like to contact you about our products and services, as well as other content that may be of interest to you. 
          p You can unsubscribe from these communications at any time. For more information on how to unsubscribe, our privacy practices, and how we are committed to protecting and respecting your privacy, please review our Privacy Policy.
</template>

<script>
  export default {
    name: "CommunicationsPolicy",
    methods: {
      backToRegister(){
        this.$emit('backToRegister');
      }
    }
  }
</script>

<style scoped lang="scss">
  @import '../../scss/base';
  .policy {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 2;
    //max-width: 100rem;
    text-align: left;
    //border: 1px solid $login-blue;
    border-radius: 2*$bdrs;
    background: #161719;
    //margin-top: 2rem;
    display: flex;
  }
  .policy_main {
    overflow: hidden;
    padding: 9rem 0 7.5rem;
    display: flex;
  }
  .policy_main-article {
    overflow: auto;
    padding-right: 7.5rem;
    padding-left: 7.5rem;
  }
  .btn--dark-blue-rev.back {
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
