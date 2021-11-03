<template lang="pug">
  .body-wrapper
    .popup-body
      .content
        .icon-wrapper
          .i.icon.icon-warning-solid
        .message
          p.header The Best Upgrade Yet
          p.message-content Enter 
            span "pip install  --upgrade perceptilabs" into the Terminal
          p.message-content 
            a.link(href="https://perceptilabs.com/docs/changelog" target="_blank") More info...
        .buttons-group
          button.copy(type="button"
            @click="copyClipboard"
          ) Copy Code
          button.dismiss(type="button"
            @click="hidePopup"
          ) Dismiss
</template>

<script>
  import { mapMutations, mapActions } from "vuex";
export default {
  name: 'PiPyPopupUpdate',
  data() {
    return {
    }
  },
  computed: {
  },
  methods: {
    ...mapMutations({
      setShowPiPyNotification:          'mod_workspace-notifications/setShowPiPyNotification'
    }),
    copyClipboard() {
      navigator.clipboard.writeText("pip install  --upgrade perceptilabs")
        .then((data)=> { this.styleClipboard['text-primary'] = true })
        .catch((err)=> { this.styleClipboard['text-error'] = true })
    },    
    hidePopup() {
      this.setShowPiPyNotification({value: false});
    }
  }
}
</script>

<style lang="scss" scoped>
  
  .body-wrapper {
    position: absolute;
    width: 440px;
    height: 110px;
    top: 68px;
    right: 20px;
    z-index: 12;
    animation-name: move;
    animation-duration: 2s;
  }

  .content {
    background-color: theme-var($neutral-7);
    // background-image: none;
    border: $border-1;
    background-size: cover;
    width: 440px;
    height: 110px;
    position: relative;
    display: flex;

    .icon-wrapper {
      width: 65px;
      display: flex;
      justify-content: center;
      align-items: center;

      .icon {
        font-size: 20px;
        color: #B6C7FB;
      }
    }

    .message {
      width: 280px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      border-right: $border-1;

      p, a {
        font-family: Nunito Sans;
        font-style: normal;
        font-weight: normal;
        font-size: 12px;
        line-height: 15px;
        color: theme-var($neutral-1);
        margin-bottom: 3px;
      }
      .header {
        font-weight: bold;
      }

      .message-content {
        span {letter-spacing: 1.2px;}
      }

      a {
        color: #6185EE;
        font-weight: bold;
      }
    }

    .copy {
      position: absolute;
      background: transparent;
      width: 95px;
      height: 55px;
      top: 0;
      right: 0;
      color: theme-var($neutral-1);

      &:hover {
        background: #6185EE;
        color: white;
      }
      border-bottom: $border-1;
    }

    .dismiss {
      position: absolute;
      background: transparent;
      width: 95px;
      height: 55px;
      bottom: 0;
      right: 0;
      color: theme-var($neutral-1);

      &:hover {
        background: #6185EE;
        color: white;
      }
    }
  }

  .popup-body{
    position: relative;
    width: 440px;
    height: 110px;
    background: transparent;
    color: #fff;
  }
  .popup-body:before,
  .popup-body:after{
    content: '';
    position: absolute;
    top: -1px;
    left: -1px;
    width: calc(100% + 2px);
    height: calc(100% + 2px);
    background: linear-gradient(172.48deg, #6185EE, rgba(97, 133, 238, 0), #6185EE, rgba(97, 133, 238, 0));
    z-index: -1;
    background-size: 400%;
    animation: borderbg 20s linear infinite;
  }
  @keyframes borderbg {
    0%{
      background-position: 0 0 ;
    }
    50%{
      background-position: 400% 0;
    }
    100%{
      background-position: 0 0 ;	
    }
  }
  .popup-body:after{
    filter: blur(40px);
  }

  @keyframes move {
    0%   { right: -440px; top: 68px;}
    50%   { right: -440px; top: 68px;}
    80%   { right: 74px; top: 68px;}
    100% { right: 20px; top: 68px;}
  }
</style>


