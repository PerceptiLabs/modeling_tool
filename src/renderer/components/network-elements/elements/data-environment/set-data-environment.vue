<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        :class="{'disable': tabSelected != i}"
        @click="setTab(i)"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              base-select(
                v-model="settings.accessProperties.Atari"
                :selectOptions="selectOptions"
                )
            .form_row
              chart-picture(
                v-if="imgType === 'image' || imgType === 'RGB'"
                :disable-header="true"
                :chartData="imgData"
              )
              chart-base(
                v-if="imgType === 'line' || imgType === 'bar' || imgType === 'scatter'"
                :disable-header="true"
                :chartData="imgData"
              )
              chart-heatmap(
                v-if="imgType === 'heatmap'"
                :disable-header="true"
                :chartData="imgData"
              )

      .popup_body(
        :class="{'active': tabSelected == 1}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              input.form_input(type="text" placeholder="c:")
              button.btn.btn--primary(type="button") Load

    .settings-layer_foot
      button.btn.btn--primary(type="button" @click="applySettings") Apply

</template>

<script>
  import mixinSet   from '@/core/mixins/net-element-settings.js';
  import mixinData  from '@/core/mixins/net-element-settings-data.js';

  import ChartPicture from "../../../charts/chart-picture";
  import ChartBase    from "../../../charts/chart-base";
  import ChartHeatmap from "../../../charts/chart-heatmap";

  export default {
    name: 'SetDataEnvironment',
    mixins: [mixinSet, mixinData],
    components: { ChartHeatmap, ChartBase, ChartPicture },
    data() {
      return {
        selectOptions: [
          { text: 'Breakout',     value: 'Breakout' },
          { text: 'BankHeist',    value: 'BankHeist' },
          { text: 'DemonAttack',  value: 'DemonAttack' }
        ],
        tabs: ['Gym', '<i class="icon icon-search"></i> Unity'],
        settings: {
          Type: 'Environment',
          accessProperties: {
            EnvType: 'Gym',
            Atari: 'Breakout', //select
            Category: 'Local',
            Type: 'Data',
          }
        }
      }
    },
    watch: {
      'settings.accessProperties.Atari': {
        handler(newVal) {
          if(newVal) {
            this.getDataImg('DataEnvironment')
          }
        },
        immediate: true
      }
    },
  }
</script>
