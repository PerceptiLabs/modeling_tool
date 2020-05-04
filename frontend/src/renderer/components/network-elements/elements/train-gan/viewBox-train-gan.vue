<template lang="pug">
  .statistics-box
    //-ul.statistics-box_tabset(v-if="!testIsOpen")
      li.statistics-box_tab(
      v-for="(tab, i) in tabset"
      /:key="i"
      )
        button.btn.btn--tabs.tutorial-relative(
        type="button"
        v-tooltip-interactive:right="tab.interactiveInfo"
        @click="setTab(tab.name, tab.id)"
        /:class="{'active': currentTab === tab.name}"
        /:id="tab.id"
        ) {{ tab.name }}
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Generator_Loss'")
      chart-switch(
        key="1"
        chart-label="Current"
        :chart-data="chartData.Generator_Loss.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="2"
        chart-label="Total"
        :chart-data="chartData.Generator_Loss.Total"
        :custom-color="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Discriminator_Loss'")
      chart-switch(
        key="3"
        chart-label="Current"
        :chart-data="chartData.Discriminator_Loss.Current"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="4"
        chart-label="Total"
        :chart-data="chartData.Discriminator_Loss.Total"
        :custom-color="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Images'")
      chart-switch(
        key="5"
        chart-label="Real Inpput"
        :chart-data="chartData.Images.Real_Input"
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="6"
        chart-label="Generated Output"
        :chart-data="chartData.Images.Generated_Output"
        :custom-color="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Data_distribution'")
      chart-switch(
        key="11"
        chart-label="Data_distribution"
        :chart-data="chartData.Data_distribution.Data_distribution"
        :custom-color="colorListAccuracy"
      )
</template>

<script>
  import ChartSwitch      from "@/components/charts/chart-switch";
  import viewBoxMixin   from "@/core/mixins/net-element-viewBox.js";


  export default {
    name: "ViewBoxTrainGan",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Generator_Loss:   { Current: null, Total: null },
          Discriminator_Loss:       { Current: null, Total: null },
          Images:         { Real_Input: null, Generated_Output: null },
          Data_distribution:        { Data_distribution: null }
        },
        btnList: {
          'Generator_Loss': {
            btnId: 'tutorial_generator_loss-tab',
            btnInteractiveInfo: {
              title: 'Generator_Loss',
              text: 'View the Generator_Loss data'
            }
          },
          'Discriminator_Loss': {
            btnId: 'tutorial_discriminator_loss-tab',
            btnInteractiveInfo: {
              title: 'Discriminator_Loss',
              text: 'View the Discriminator_Loss data.'
            }
          },
          'Images': {
            btnId: 'tutorial_images-tab',
            btnInteractiveInfo: {
              title: 'Images',
              text: 'View the images.'
            }
          },
          'Data_distribution': {
            btnId: 'tutorial_data_distribution-tab',
            btnInteractiveInfo: {
              title: 'Data_distribution',
              text: 'View the Data_distribution.'
            }
          },
        },
        colorList: ['#6B8FF7', '#FECF73'],
        colorListAccuracy: ['#9173FF', '#6B8FF7'],
        colorPie: ['#6B8FF7', '#383F50'],
        showRequestSpinner: {
          Input: true,
          PvG: true,
          AveragePvG: true,
          Accuracy: true
        }
      }
    },
    watch: {
      testIsOpen(newVal) {
        newVal ? this.setTab('Generator_Loss') : null
      }
    },
    methods: {

      getData() {
        switch (this.currentTab) {
          case 'Generator_Loss':
            this.chartRequest(this.statElementID, 'TrainGan', 'Generator_Loss');
            break;
          case 'Discriminator_Loss':
            this.chartRequest(this.statElementID, 'TrainGan', 'Discriminator_Loss');
            break;
          case 'Images':
            this.chartRequest(this.statElementID, 'TrainGan', 'Images');
            break;
          case 'Data_distribution':
            this.chartRequest(this.statElementID, 'TrainGan', 'Data_distribution');
            break;
        }
      }
    },

  }
</script>
