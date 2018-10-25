<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        settings-reshape

      .popup_body(
          :class="{'active': tabSelected == 1}"
        )
        settings-code

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
  import SettingsReshape from "@/components/network-elements/elements-settings/setting-reshape";

  export default {
    name: 'SetDataData',
    mixins: [mixinSet],
    components: {
      SettingsReshape,
      SettingsCode
    },
    data() {
      return {
        tabs: ['Settings', 'Code']
      }
    }
  }
</script>
