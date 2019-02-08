<template lang="pug">
  .tutorial-box
    .tutorial-box_modal-popup
      .modal-popup_eyes
      button.close-tutorial.i.icon.icon-empty
      .modal-popup_title What is AI?
      .modal-popup_info AI refers to a machine or a software program that simulates human intelligence to accomplish a certain task (often in a narrow area).
      .modal-popup_image
      .modal-popup_control-buttons
        button.prev-button.i.icon.icon-player-play
        button.next-button.i.icon.icon-player-play
      button.skip-button
      ul.modal-popup_all-slides-controls
        li 1
        li 2
</template>
<script>
export default {
  name: 'Tutorial',
  data() {
    return {

    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  $distance-control-btn: 5.5rem;

  .tutorial-box {
    position: fixed;
    top: 0;
    left: 0;
    background: rgba(0, 0, 0, .5);
    width: 100%;
    height: 100%;
    z-index: 1;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .tutorial-box_modal-popup {
    border: 1px solid $col-primary;
    border-radius: 5px;
    padding: 6rem 3rem 2rem 3rem;
    position: relative;
    width: 44rem;
    button {
      background: none;
    }

    button.close-tutorial {
      color: $col-primary;
      position: absolute;
      font-size: 2rem;
      top: .4rem;
      left: .4rem;
      padding: 0
    }
  }
  .modal-popup_eyes {}
  .modal-popup_title {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 2rem;
  }
  .modal-popup_info {
    font-size: 1.4rem; 
  }
  .modal-popup_control-buttons {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    justify-content: space-between;
    width: 100%;
    
    button {
      color: $col-primary;
      font-size: 5rem;
      position: relative;
    }
    .prev-button {
      right: $distance-control-btn;
      transform: rotate(-180deg);
    }
    .next-button {
      left: $distance-control-btn;
    }
  }
</style>