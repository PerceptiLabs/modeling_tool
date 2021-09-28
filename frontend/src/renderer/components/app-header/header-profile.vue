<template lang="pug">
  div.profile-wrapper
    div.profile-item
      .profile-item-wrapper(        
        @click="toggleProfile(!showProfilePanel)"
        @blur="toggleProfile(false)"
        tabindex="0"
      )
        .profile-item-Avatar.with-border.f-nunito#user-avatar(
          :data-tutorial-target="'tutorial-model-hub-user-gravatar'"
        )
          | {{user && user.email && user.email[0].toUpperCase()}}
        .profile-username(:class="{'open': showProfilePanel}") {{user.firstName}}
        
        svg.dropdown-icon(:class="{'open': showProfilePanel}" width="9" height="6" viewBox="0 0 9 6" fill="none" xmlns="http://www.w3.org/2000/svg")
          path(d="M3.91611 5.72652L0.193542 1.32977C-0.245778 0.812461 0.111266 2.94912e-07 0.778007 2.94912e-07H8.22315C8.37237 -0.000131902 8.51846 0.0441823 8.64393 0.127636C8.7694 0.211091 8.86893 0.330147 8.9306 0.470548C8.99228 0.610949 9.01347 0.766743 8.99166 0.919273C8.96985 1.0718 8.90595 1.2146 8.80762 1.33057L5.08504 5.72572C5.01219 5.81187 4.92235 5.88091 4.82154 5.92822C4.72073 5.97552 4.6113 6 4.50058 6C4.38986 6 4.28043 5.97552 4.17962 5.92822C4.07881 5.88091 3.98897 5.81187 3.91611 5.72572V5.72652Z")

      .dropdown.profile-item-drop-down(v-if="showProfilePanel" ref="profileDropdown")
        .dropdown-item(@click="toSettings")
          svg(width="20" height="20" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M6.51957 1.79458C6.76688 0.805321 7.65574 0.111328 8.67544 0.111328H9.32499C10.3447 0.111328 11.2336 0.805322 11.4809 1.79458L11.5424 2.04078C11.7402 2.11304 11.934 2.19349 12.1235 2.28169L12.3413 2.15098C13.2157 1.62634 14.335 1.76413 15.056 2.48517L15.5153 2.94447C16.2363 3.66551 16.3741 4.78475 15.8495 5.65914L15.7188 5.87701C15.807 6.06644 15.8874 6.26025 15.9597 6.45802L16.2059 6.51957C17.1951 6.76688 17.8891 7.65574 17.8891 8.67544V9.32499C17.8891 10.3447 17.1951 11.2336 16.2059 11.4809L15.9597 11.5424C15.8874 11.7402 15.807 11.934 15.7188 12.1234L15.8495 12.3413C16.3741 13.2157 16.2363 14.3349 15.5153 15.0559L15.056 15.5152C14.3349 16.2363 13.2157 16.3741 12.3413 15.8494L12.1235 15.7187C11.934 15.8069 11.7402 15.8874 11.5424 15.9597L11.4809 16.2059C11.2336 17.1951 10.3447 17.8891 9.32499 17.8891H8.67544C7.65574 17.8891 6.76688 17.1951 6.51957 16.2059L6.45802 15.9597C6.26024 15.8874 6.06642 15.807 5.87698 15.7188L5.65916 15.8494C4.78477 16.3741 3.66553 16.2363 2.94449 15.5152L2.48519 15.0559C1.76415 14.3349 1.62636 13.2157 2.151 12.3413L2.28169 12.1235C2.19348 11.934 2.11304 11.7402 2.04078 11.5424L1.79458 11.4809C0.805321 11.2336 0.111328 10.3447 0.111328 9.32499V8.67544C0.111328 7.65574 0.805323 6.76688 1.79458 6.51957L2.04078 6.45802C2.11304 6.26023 2.19349 6.06641 2.28169 5.87697L2.151 5.65914C1.62636 4.78475 1.76415 3.66551 2.48519 2.94447L2.94449 2.48517C3.66553 1.76413 4.78477 1.62634 5.65916 2.15098L5.87699 2.28168C6.06643 2.19348 6.26025 2.11304 6.45802 2.04078L6.51957 1.79458ZM8.67544 1.59281C8.33554 1.59281 8.03926 1.82414 7.95682 2.15389L7.69454 3.20299L7.29129 3.32422C6.9085 3.43929 6.54192 3.59209 6.19584 3.7784L5.82487 3.97809L4.89695 3.42134C4.60548 3.24646 4.2324 3.29239 3.99205 3.53273L3.53275 3.99204C3.29241 4.23238 3.24648 4.60546 3.42136 4.89693L3.97811 5.82485L3.77841 6.19581C3.5921 6.5419 3.43929 6.90849 3.32422 7.29129L3.20299 7.69454L2.15389 7.95682C1.82414 8.03926 1.59281 8.33554 1.59281 8.67544V9.32499C1.59281 9.6649 1.82414 9.96118 2.15389 10.0436L3.20299 10.3059L3.32422 10.7091C3.43929 11.0919 3.5921 11.4585 3.77841 11.8046L3.97811 12.1756L3.42136 13.1035C3.24648 13.395 3.29241 13.768 3.53276 14.0084L3.99206 14.4677C4.23241 14.708 4.60549 14.754 4.89695 14.5791L5.82486 14.0223L6.19582 14.222C6.54191 14.4083 6.9085 14.5611 7.29129 14.6762L7.69454 14.7974L7.95682 15.8465C8.03926 16.1763 8.33554 16.4076 8.67544 16.4076H9.32499C9.66489 16.4076 9.96118 16.1763 10.0436 15.8465L10.3059 14.7974L10.7091 14.6762C11.0919 14.5611 11.4585 14.4083 11.8046 14.222L12.1756 14.0223L13.1035 14.5791C13.395 14.754 13.7681 14.708 14.0084 14.4677L14.4677 14.0084C14.708 13.768 14.754 13.395 14.5791 13.1035L14.0223 12.1756L14.222 11.8046C14.4083 11.4585 14.5612 11.0919 14.6762 10.7091L14.7974 10.3059L15.8465 10.0436C16.1763 9.96118 16.4076 9.6649 16.4076 9.32499V8.67544C16.4076 8.33554 16.1763 8.03926 15.8465 7.95682L14.7974 7.69454L14.6762 7.29129C14.5612 6.90851 14.4083 6.54193 14.222 6.19585L14.0223 5.82489L14.5791 4.89692C14.754 4.60546 14.7081 4.23238 14.4677 3.99204L14.0084 3.53273C13.7681 3.29239 13.395 3.24646 13.1035 3.42134L12.1756 3.97811L11.8046 3.77841C11.4585 3.5921 11.0919 3.43929 10.7091 3.32422L10.3059 3.20299L10.0436 2.15389C9.96118 1.82414 9.66489 1.59281 9.32499 1.59281H8.67544Z")
            path(fill-rule="evenodd" clip-rule="evenodd" d="M9.00022 7.51874C8.18202 7.51874 7.51874 8.18202 7.51874 9.00022C7.51874 9.81842 8.18202 10.4817 9.00022 10.4817C9.81842 10.4817 10.4817 9.81842 10.4817 9.00022C10.4817 8.18202 9.81842 7.51874 9.00022 7.51874ZM6.03725 9.00022C6.03725 7.36382 7.36382 6.03725 9.00022 6.03725C10.6366 6.03725 11.9632 7.36382 11.9632 9.00022C11.9632 10.6366 10.6366 11.9632 9.00022 11.9632C7.36382 11.9632 6.03725 10.6366 6.03725 9.00022Z")
          .label Settings

        .dropdown-item(@click="logOut")
          svg(width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg")
            path(d="M17.5004 10.6251C17.3404 10.6251 17.1807 10.5642 17.0586 10.442L12.8598 6.24355C12.6157 5.99949 12.6157 5.60387 12.8598 5.3598C13.1039 5.11574 13.4995 5.11574 13.7436 5.3598L17.9423 9.55824C18.1864 9.8023 18.1864 10.1979 17.9423 10.442C17.8201 10.5639 17.6604 10.6251 17.5004 10.6251Z")
            path(d="M13.3017 14.8234C13.1417 14.8234 12.982 14.7624 12.8598 14.6402C12.6157 14.3962 12.6157 14.0005 12.8598 13.7565L17.0586 9.55805C17.3026 9.31398 17.6982 9.31398 17.9423 9.55805C18.1864 9.80211 18.1864 10.1977 17.9423 10.4418L13.7439 14.6402C13.6217 14.7621 13.4617 14.8234 13.3017 14.8234Z")
            path(d="M17.5 10.625H5.625C5.28 10.625 5 10.345 5 10C5 9.655 5.28 9.375 5.625 9.375H17.5C17.845 9.375 18.125 9.655 18.125 10C18.125 10.345 17.845 10.625 17.5 10.625Z")
            path(d="M3.125 18.125C2.43562 18.125 1.875 17.5644 1.875 16.875C1.875 16.53 2.155 16.25 2.5 16.25C2.845 16.25 3.125 16.53 3.125 16.875V16.8759C3.47 16.8759 3.75 17.1553 3.75 17.5006C3.75 17.8459 3.47 18.125 3.125 18.125Z")
            path(d="M7.5 18.125H3.125C2.78 18.125 2.5 17.845 2.5 17.5C2.5 17.155 2.78 16.875 3.125 16.875H7.5C7.845 16.875 8.125 17.155 8.125 17.5C8.125 17.845 7.845 18.125 7.5 18.125Z")
            path(d="M2.5 17.5C2.155 17.5 1.875 17.22 1.875 16.875V3.125C1.875 2.78 2.155 2.5 2.5 2.5C2.845 2.5 3.125 2.78 3.125 3.125V16.875C3.125 17.22 2.845 17.5 2.5 17.5Z")
            path(d="M2.49969 3.75C2.15438 3.75 1.875 3.47 1.875 3.125C1.875 2.43562 2.43562 1.875 3.125 1.875C3.47 1.875 3.75 2.155 3.75 2.5C3.75 2.845 3.47 3.125 3.125 3.125H3.12406C3.12406 3.47 2.845 3.75 2.49969 3.75Z")
            path(d="M7.5 3.125H3.125C2.78 3.125 2.5 2.845 2.5 2.5C2.5 2.155 2.78 1.875 3.125 1.875H7.5C7.845 1.875 8.125 2.155 8.125 2.5C8.125 2.845 7.845 3.125 7.5 3.125Z")
          .label Log Out
</template>

<script>
  import { mapGet, mapGetters, mapActions} from 'vuex';

  const collaboratorData = [
    {id: 1, name: 'Martin Isaksson', email: 'martin.i@perceptilabs.com'},
    {id: 2, name: 'Anton Bourosu', email: 'anton.b@perceptilabs.com'},
  ];
  
  export default {
    name: "HeaderProfile",
    data: function() {
      return {
        collaboratorData: collaboratorData,
        showProfilePanel: false,
      }
    },
    computed: {
      ...mapGetters({
        user:               'mod_user/GET_userProfile',
        isTutorialMode:     'mod_tutorials/getIsTutorialMode',
        getCurrentStepCode: 'mod_tutorials/getCurrentStepCode',

      })
    },
    methods: {
      ...mapActions({
        popupConfirm:     'globalView/GP_confirmPopup',
        setNextStep:      'mod_tutorials/setNextStep',
      }),
      toggleProfile(visible = null) {
        if(visible)
          this.showProfilePanel = true;
        else {
          setTimeout(() => {
            this.showProfilePanel = false
          }, 200)
        }
      },
      toSettings() {
        this.$router.push({name: 'settings'});
        this.showProfilePanel = false;
      },
      logOut() {
        this.$store.dispatch('mod_events/EVENT_logOut');
        this.showProfilePanel = false;
      }
    }
  }
</script>

<style lang="scss" scoped>
  .profile-item {
    position: relative;
  }
  .profile-item-drop-down {
    position: absolute;
    right: 0;
    top: 46px;
    min-width: 120px;
    box-shadow: 0px 4px 4px rgba(122, 122, 122, 0.36);
  }
  .profile-item-Avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    box-sizing: border-box;
    background-color: #FE7373;
    text-align: center;
    line-height: 34px;
    text-transform: uppercase;
    font-size: 14px;
    color: #fff;
    border: $border-1;
    /*&.with-border {*/
    /*  &:hover {*/
    /*    width: 28px;*/
    /*    height: 28px;*/
    /*    border: 4px solid #23252A; */
    /*  }*/
    /*}*/
  }
  .profile-item-wrapper {
    display: flex;
    align-items: center;
    cursor: pointer;

    & .dropdown-icon {
      fill: theme-var($neutral-1);

      &.open {
        fill: $color-6;
        transform: rotate(180deg);
      }
    }

    .profile-username {
      font-size: 14px;
      font-weight: 500;
      margin-left: 10px;
      margin-right: 5px;
      color: theme-var($neutral-1);

      &.open {
        color: $color-6;
      }
    }
    
  }
  .dropdown-item  {
    & .label {
      margin-left: 8px;
    }
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
  .f-nunito {
    font-family: "Nunito Sans";
  }
  .mt-7 {
    margin-top: 7px;
  }
</style>
