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
            base-select(v-model="settings.Properties.accessProperties.Atari" :selectOptions="selectOptions")

      .popup_body(
        :class="{'active': tabSelected == 1}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              input.form_input(type="text" placeholder="c:")
              button.btn.btn--primary(type="button") Load

</template>

<script>
  import mixinSet       from '@/core/mixins/net-element-settings.js';
  export default {
    name: 'SetDataData',
    mixins: [mixinSet],
    components: {

    },
    data() {
      return {
        selectOptions: [
          { text: 'Breakout', value: 'Breakout' },
          { text: '2', value: 'b' },
          { text: '3', value: 'c' }
        ],
        tabs: ['Gym', '<i class="icon icon-search"></i> Unity'],
        settings: {
          Name: 'Data_1',
          Type: 'DataEnvironment',
          Properties: {
            Type: 'Environment',
            accessProperties: {
              EnvType: 'Gym',
              Atari: 'Breakout', //select
              Category: 'Local',
              Type: 'Data',
            }
          }
        }
      }
    }
  }
</script>
