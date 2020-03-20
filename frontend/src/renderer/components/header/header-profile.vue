<template lang="pug">
  div.profile-wrapper
    div.profile-item
      .profile-item-Avatar.with-border
        | A
      .profile-item-drop-down
        button.bgc-transparent.ta-left.p-13
          .d-flex
            .profile-item-Avatar
              | R
            div.ml-12
              h3.white.fz-14.mb-0 Robert Lundberg
              p.fz-12.mb-0 robert.l@perceptilabs.com
        .profile-separator
        button.bgc-transparent.ta-left.profile-item-wrapper(v-for="collaborator in collaboratorData")
          .d-flex
            .profile-item-Avatar
              | {{collaborator.name[0]}}
            div.ml-12
              h3.white.fz-14.mb-0 {{collaborator.name}}
              p.fz-12.mb-0 {{collaborator.email}}
        button.bgc-transparent.ta-left.add-more-collaborators.d-flex
          .circleButton
            img(src="../../../../static/img/project-page/plus.svg")
          h3.fz-14 Add another account
        .profile-separator

        button.sign-out-all
          | Sign out all accounts
</template>

<script>

  const collaboratorData = [
    {id: 1, name: 'Martin Isaksson', email: 'martin.i@perceptilabs.com'},
    {id: 2, name: 'Anton Bourosu', email: 'anton.b@perceptilabs.com'},
  ];
  
  export default {
    name: "HeaderProfile",
    data: function() {
      return {
        collaboratorData: collaboratorData,
      }
    },
    
  }
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .profile-wrapper {
    position: absolute;
    right: 40px;
  }
  .profile-item {
    position: relative;
    &:hover {
      .profile-item-drop-down {
        display: block;
      }
    }
  }
  .profile-item-drop-down {
    display: none;
    right: 0;
    top: 26px;
    position: absolute;
    background: #363E51;
    border: 1px solid #363E51;
    box-sizing: border-box;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
    border-radius: 2px;
    min-width: 230px;
  }
  .profile-item-Avatar {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    box-sizing: border-box;
    background-color: #FE7373;
    text-align: center;
    line-height: 20px;
    text-transform: uppercase;
    font-size: 14px;
    color: #fff;
    &.with-border {
      box-sizing: content-box;
      border: 4px solid #23252A;
    }
  }
  .profile-item-wrapper {
    padding: 13px 13px 0;
  }
  .p-13 {
    padding: 13px;
  }
  .profile-separator {
    height: 1px;
    background-color: #23252A;
    display: block;
  }
  .ml-12 {
    margin-left: 12px;
  }
  .fz-14 {
    font-size: 14px;
  }
  .fz-12 {
    font-size: 12px;
  }
  .white {
    color: #fff;
  }
  .mb-0 {
    margin-bottom: 0;
  }
  .bgc-transparent {
    background-color: transparent;
  }
  .ta-left {
    text-align: left;
  }
  .sign-out-all {
    display: block;
    margin: 13px 23px 15px;
    width: calc(100% - 46px);
    padding: 10px 20px;
    border: 1px solid #000;
    border-radius: 2px;
    text-align: center;
    color: #fff;
    font-size: 14px;
    background-color: transparent;
  }
  .add-more-collaborators {
    margin-top: 10px;
    margin-bottom: 14px;
    h3 {
      margin-top: 2px;
      margin-left: 12px;
      margin-bottom: 0;
      
    }
  }
  .circleButton {
    width: 20px;
    height: 20px;
    margin-left: 8px;
    border: 1px solid #fff;
    border-radius: 50%;
    text-align: center;
    line-height: 17px;
  }
</style>
