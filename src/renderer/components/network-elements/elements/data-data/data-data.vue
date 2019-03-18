<template lang="pug">
  base-net-el(
    :dataEl="elementData"
  )
    view-el
    template(slot="context")
      context-menu
    template(slot="settings")
      settings-el(
        :layer-id="elementData.el.layerId"
      )

</template>

<script>
  import BaseNetEl    from '@/components/network-elements/net-base-element/net-base-element.vue';
  import ContextMenu  from '@/components/network-elements/net-context-menu/net-context-menu.vue';
  import ViewEl       from './view-data-data.vue';
  import SettingsEl   from './set-data-data';

  export default {
    name: 'DataData',
    components: {
      BaseNetEl,
      ContextMenu,
      ViewEl,
      SettingsEl
    },
    props: {
      elementData: Object
    },
    // mounted() {
    //   if(process.env.NODE_ENV === 'production' && !this.settings.accessProperties.Path) {
    //     switch (process.platform) {
    //       case 'win32':
    //         this.settings.accessProperties.Path = this.appPath + 'core\\mnist';
    //         break;
    //       case 'darwin':
    //         this.settings.accessProperties.Path = this.appPath + 'core/mnist';
    //         break;
    //       case 'linux':
    //         this.settings.accessProperties.Path = this.appPath + 'core/mnist';
    //         break;
    //     }
    //     this.applySettings();
    //   }
    // },
    // data() {
    //   return {
    //     settings: {
    //       Type: 'Data',
    //       accessProperties: {
    //         Category:'Local',
    //         Type: 'Data',
    //         Path: '',
    //       }
    //     }
    //   }
    // },
    // computed: {
    //   appPath() {
    //     return this.$store.getters['globalView/GET_appPath']
    //   },
    // },
    // methods: {
    //   applySettings() {
    //     this.elementData.el.layerSettings.accessProperties.Path = this.settings.accessProperties.Path;
    //   }
    // }
  }
</script>
