<template lang="pug">
  div.tutorial-instruction-box
    button.btn.btn--dark-blue-rev.green-status(type="button"
      @click="showInstructions"
    )
      span Tutorial Mode
      i.icon.icon-ellipse
    div.tutorial-instruction-box_list-area(v-if="isShowInstructions")
      header.list-area_header
        div
          button.header_close-instructions.i.icon.icon-appClose(@click="showInstructions")
          span.header_title title_q
        .header_arrows-top
          i.icon.icon-shevron
          i.icon.icon-shevron
      
      //- ul.list-area_list
      //-   div.list-element.list_title Instructions:
      //-   div.list-element When working with AI, you can divide the process into 2 overarching steps: 
      //-   div.list-element 
      //-     p 1) Knowing your data
      //-     p 2) Building your model
      //- footer.list-area_footer
      //-   button.footer_all-tutorials-btn
      //-     i.icon.icon-shevron-right
      //-     span All tutorials
      //-   .curent-steps 1/10
      //-   div
      //-     button.footer_btn Back
      //-     button.footer_btn(disabled) Next

      ul.list-area_list
        div.list-element.list_title Step 1. Import your data
        div.list-element.list_subtitle  
          |In the 
          .marker Operations Toolbar 
          | go to 
          .marker Data 
          | > Select and drop 
          .marker Data 
          | to workspace > Load dataset
        div.list-element For this tutorial we will use the MNIST dataset
        div.list-element Every input image has been flattened out to a 784x1 array
      footer.list-area_footer
        button.footer_all-tutorials-btn
          i.icon.icon-shevron-right
          span All tutorials
        .curent-steps 1/10
        div
          button.footer_btn Back
          button.footer_btn(disabled) Next

</template>
<script>
export default {
  name: 'TutorialInstructions',
  data() {
    return {
      isShowInstructions: false,
      step_0: [
        {
          content: '<p class="instruction-title">Instruction</p>',
        },
        {
          content: '<p>When working with AI, you can divide the process into 2 overarching steps: 1) Knowing your data 2) Building your model  </p>',
          status: 'not passed' // active, passed, not passed
        }
      ]
    }
  },
  computed: {

  },
  methods: {
    showInstructions() {
      this.isShowInstructions =  !this.isShowInstructions; 
    }
  }
}
</script>
<style lang="scss">
  @import "../../scss/base";
  $color-text-instructions:#AEAEAE;
  $title-padding: 0 2.1rem;


  .btn--dark-blue-rev {
    position: relative;
    z-index: 2;
  }
  .tutorial-instruction-box {
    position: relative;
  }
  .tutorial-instruction-box_list-area {
    position: absolute;
    z-index: 1;
    background: $col-txt2;
    width: 24rem;
    top: 90%;
    right: 0;
    color: $white;
    border-radius: 5px;
    overflow: hidden;
  }
  .list-area_header {
    background: $bg-workspace;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 2.6rem;
    margin-bottom: 1rem;
  }
  .header_close-instructions {
    background: none;
    border: 1px solid $color-text-instructions;
    color: $color-text-instructions;
    border-radius: 20rem;
    font-size: 0.9rem;
    padding: 0.1rem;
    margin-left: 0.5rem;
  }
  .header_title {
    font-size: 1.4rem;
    margin-left: 1rem;
    color: $color-text-instructions;
  }
  .header_arrows-top {
    color: $col-txt;
    background: $col-txt2;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    padding: 0 1.2rem;
    .icon{
      font-size: 1.3rem;
      position: relative;
      transform: rotate(-90deg);
      &:first-child {
        top: 0.4rem;
      }
      &:last-child {
        top: -0.4rem;
      }
    }
  }
  .list-area_list {
    height: 15rem;
    overflow: scroll;
  }
  .list-element {
    padding: 0 3rem;
    margin-bottom: 1.5rem;
    font-size: 1.2rem;
    &.list_title {
      font-weight: 700;
      font-size: 1.2rem;
      padding: $title-padding;
    }
    &.list_subtitle {
      padding: $title-padding;
    }
    p {
      margin-bottom: 0.3rem;
    }
    .marker {
      color: #3bc5ff;
      font-weight: 700;
      display: inline;
    }
  }
  .list-area_footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding: 0 1rem;
    button {
      background: none;
    }
  }
  .footer_all-tutorials-btn {
    display: flex;
    align-items: center;
    color: $color-text-instructions;
    padding: 0;
    .icon {
      transform: rotate(-180deg);
      display: inline-block;
      margin-right: 0.5rem;
    }
    font-size: 1.2rem;
  }
  .footer_btn {
    font-size: 1.2rem;
    border: 1px solid $login-blue;
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    margin-right: 1rem;
    &:last-child {
      margin-right: 0; 
    }
    &[disabled] {
      border: 1px solid $color-text-instructions;
      color: $color-text-instructions;
    }
  }
  .curent-steps {
    font-size: 1.2;
    color: $color-text-instructions;
  }
</style>