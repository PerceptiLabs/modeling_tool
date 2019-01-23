<template lang="pug">
  main.page
    aside.page_sidebar
      include ./sidebar/sidebar.pug

    .page_basic-templates
      include ./basic-templates/basic-templates.pug
    .page_recent-files
      include ./recent-files/recent-files.pug

</template>
<script>
import UpdatePopup from '@/components/global-popups/update-popup/update-popup.vue'

export default {
    components: {
      UpdatePopup
    },
    name: 'PageHome',
    data() {
      return {
          source: 'cloud',
          service: '',
          projects: [
            {
              id: 1,
              name: 'Quantum net (Project_1)',
              icon: 'icon-cloud',
              trained: true,
              time: '25.12.2018 20:24',
              scheme: ''
            },
            {
              id: 2,
              name: 'Quantum net (Project_2)',
              icon: 'icon-computer',
              trained: true,
              time: '25.12.2018 20:24',
              scheme: ''
            },
            {
              id: 3,
              name: 'Quantum net (Project_3)',
              icon: 'icon-cloud',
              trained: false,
              time: '25.12.2018 20:24',
              scheme: ''
            },
            {
              id: 4,
              name: 'Quantum net (Project_4)',
              icon: 'icon-cloud',
              trained: true,
              time: '25.12.2018 20:24',
              scheme: ''
            },
            {
              id: 5,
              name: 'Quantum net (Project_5)',
              icon: 'icon-computer',
              trained: false,
              time: '25.12.2018 20:24',
              scheme: ''
            },
            {
              id: 6,
              name: 'Quantum net (Project_6)',
              icon: 'icon-cloud',
              trained: true,
              time: '25.12.2018 20:24',
              scheme: ''
            },
            {
              id: 7,
              name: 'Quantum net (Project_7)',
              icon: 'icon-cloud',
              trained: false,
              time: '25.12.2018 20:24',
              scheme: ''
            },
            {
              id: 8,
              name: 'Quantum net (Project_8)',
              icon: 'icon-computer',
              trained: true,
              time: '25.12.2018 20:24',
              scheme: ''
            },
            {
              id: 9,
              name: 'Quantum net (Project_9)',
              icon: 'icon-computer',
              trained: false,
              time: '25.12.2018 20:24',
              scheme: ''
            },
                        {
              id: 10,
              name: 'Quantum net (Project_10)',
              icon: 'icon-computer',
              trained: false,
              time: '25.12.2018 20:24',
              scheme: ''
            }
        ],
        processName: '14.11.2018',
        updateButtons: [
          {
            className: 'btn--primary',
            text: 'Install',
            action: this.install
          }
        ],
        updateShowPopup: false,
        moreInfoUpdateText: [
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
          'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
        ],
        startLoading: false,
        fakeTimer: null,
        progressStatus: 0,
        message: ''
      }
    },
    methods: {
      openProject() {
        this.$router.push({name: 'app'});
      },
      addProject() {
        this.$router.push({name: 'app'});
      },
      openPopup() {
        this.updateShowPopup = true;
      },
      closePopup() {
        this.updateShowPopup = false;
      }
    }
  }
</script>
<style lang="scss" scoped>
  @import '../../scss/base';
  @import './sidebar/sidebar';
  @import './basic-templates/basic-templates';
  @import './recent-files/recent-files';

  .page {
    grid-template-columns: $w-sidebar 1fr;
    grid-template-rows: $w-sidebar auto;
    grid-template-areas:  "sidebar basic-templates"
                          "sidebar recent-files";
  }

</style>


