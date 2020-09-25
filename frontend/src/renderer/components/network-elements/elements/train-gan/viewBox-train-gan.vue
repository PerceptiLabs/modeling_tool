<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col(v-if="computedCurrentTab === 'Generator_Loss'")
      chart-switch(
        key="1"
        chart-label="Generator loss during one epoch"
        :chart-data="chartData.Generator_Loss.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="2"
        chart-label="Generator loss over all epochs"
        :chart-data="chartData.Generator_Loss.Total"
        :custom-color="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="computedCurrentTab === 'Discriminator_Loss'")
      chart-switch(
        key="3"
        chart-label="Discriminator loss during one epoch"
        :chart-data="chartData.Discriminator_Loss.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="4"
        chart-label="Discriminator loss over all epochs"
        :chart-data="chartData.Discriminator_Loss.Total"
        :custom-color="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="computedCurrentTab === 'Samples'")
      .statistics-box_row
        .statistics-box_col(v-if="!testIsOpen")
          chart-switch(
            key="5"
            chart-label="Real Inpput"
            :chart-data="chartData.Images.Real_Input"
            :custom-color="colorListAccuracy"
          )
        .statistics-box_col
          chart-switch(
            key="6"
            chart-label="Generated Output"
            :chart-data="chartData.Images.Generated_Output"
            :custom-color="colorListAccuracy"
          )
    .statistics-box_main.statistics-box_col(v-if="computedCurrentTab === 'Data_distribution'")
      chart-switch(
        key="11"
        chart-label="Data distribution"
        :chart-data="chartData.Data_distribution.Data_distribution"
        :custom-color="colorListAccuracy"
      )
</template>

<script>
  import ChartSwitch      from "@/components/charts/chart-switch";
  import viewBoxMixin   from "@/core/mixins/net-element-viewBox.js";
  import { mapActions } from 'vuex';

  export default {
    name: "ViewBoxTrainGan",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Generator_Loss:           { Current: null, Total: null },
          Discriminator_Loss:       { Current: null, Total: null },
          Images:                   { Real_Input: null, Generated_Output: null },
          Data_distribution:        { Data_distribution: null }
        },
        btnList: {
          'Generator_Loss': {
            btnId: 'tutorial_generator_loss-tab',
            btnInteractiveInfo: {
              title: 'Generator Loss',
              text: 'View the Generator Loss Data'
            }
          },
          'Discriminator_Loss': {
            btnId: 'tutorial_discriminator_loss-tab',
            btnInteractiveInfo: {
              title: 'Discriminator Loss',
              text: 'View the Discriminator Loss Data.'
            }
          },
          'Samples': {
            btnId: 'tutorial_samples-tab',
            btnInteractiveInfo: {
              title: 'Samples',
              text: 'View the samples.'
            }
          },
          'Data_distribution': {
            btnId: 'tutorial_data_distribution-tab',
            btnInteractiveInfo: {
              title: 'Data distribution',
              text: 'View the Data distribution.'
            }
          },
        },
        colorList: ['#6B8FF7', '#FECF73'],
        colorListAccuracy: ['#9173FF', '#6B8FF7'],
        colorPie: ['#6B8FF7', '#383F50'],
      }
    },
    watch: {
      currentTab() {
        this.setTabAction();
      }
    },
    methods: {
      ...mapActions({
      }),
      getData() {
        switch (this.computedCurrentTab) {
          case 'Generator_Loss':
            this.chartRequest(this.statElementID, 'TrainGan', 'Generator_Loss');
            break;
          case 'Discriminator_Loss':
            this.chartRequest(this.statElementID, 'TrainGan', 'Discriminator_Loss');
            break;
          case 'Samples':
            this.chartRequest(this.statElementID, 'TrainGan', 'Images');
            break;
          case 'Data_distribution':
            this.chartRequest(this.statElementID, 'TrainGan', 'Data_distribution');
            break;
        }
      }
    },
    computed: {
      computedCurrentTab() {
        return this.testIsOpen ? 'Samples' : this.currentTab;
      }
    }

  }
</script>
