<template lang="pug">
    main.page
      aside.page_sidebar
        include ./sidebar/sidebar.pug
          
      .page_workspace
        include ./workspace/workspace.pug

</template>
<script>
export default {
    name: 'PageProjects',
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
            }
          ]
      }
    },
    methods: {
      openProject() {
        this.$router.push({name: 'app'});
      },
      addProject() {
        this.$router.push({name: 'app'});
      }
    }
}
</script>
<style lang="scss" scoped>
  @import '../../scss/base';
  @import './sidebar/sidebar';
  @import './workspace/workspace';

  .page {
    grid-template-columns: $w-sidebar 1fr;
    grid-template-rows: inherit;
    grid-template-areas: 
      "sidebar workspace";
  }

</style>


