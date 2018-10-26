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
        .settings-layer
          .settings-layer_section
            .form_row
              .form_label.w-33 Data Input:
              .form_input.w-66
                input
          .settings-layer_section.text-center
            img(src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Hopetoun_falls.jpg/220px-Hopetoun_falls.jpg")
          .settings-layer_section
            .form_row
              .form_label.w-33 Reshape data:
              .form_input.w-66
                input
          .settings-layer_foot
            button.btn.btn--primary(type="button") Apply


      .popup_body(
          :class="{'active': tabSelected == 1}"
        )
        settings-code

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

  export default {
    name: 'SetProcessCrop',
    mixins: [mixinSet],
    components: {
      SettingsCode
    },
    data() {
      return {
        tabs: ['Settings', 'Code']
      }
    }
  }
</script>
