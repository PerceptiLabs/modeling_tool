<template lang="pug">
  .policy-background
    .policy
      img(src="../../../../static/img/perceptilabs-logo-icon.svg" alt="PerceptiLabs logo")
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

  ::-webkit-scrollbar {
    background: #161719;
  }

  ::-webkit-scrollbar {
    width: 6px;
  }

  ::-webkit-scrollbar-thumb {
    border-radius: 3px;
    background-color: rgba(#989FB0, .5);
    box-shadow: 0 0 6px rgba(#000, .3);
    &:hover {
      background-color: rgba(#989FB0, 1);
    }
    &:window-inactive {
      background-color: rgba(#989FB0, .2);
    }
  }

  .policy-background {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background: #272C37;

    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .policy {
    position: relative;
    height: 70%;
    width: 30%;
    z-index: 2;
    text-align: left;
    border: 1px solid $login-blue;
    border-radius: 2*$bdrs;
    background: #161719;
    display: flex;
    flex-direction: column;
  }

  img {
    position: absolute;
    left: 50%;
    transform: translate(-50%, -150%);
  }

  .policy_main {
    position: relative;
    overflow: hidden;
    padding: 5rem 0 5rem;
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
    // position: relative;
    // top: 0;
    left: 50%;
    // display: inline-block;
    width: 10rem;
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
