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
        .form_row
          input.form_input(type="text" placeholder="c:")
          button.btn.btn--primary(type="button") Load

      .popup_body(
          :class="{'active': tabSelected == 1}"
        )
        settings-cloud

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import SettingsCloud  from '@/components/base/setting-clouds.vue';

  export default {
    name: 'SetDataData',
    mixins: [mixinSet],
    components: {
      SettingsCloud
    },
    data() {
      return {
        tabs: ['Computer', 'Cloud']
      }
    }
  }
</script>
