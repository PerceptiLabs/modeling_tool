<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row
        .statistics-box_col(v-if="!testIsOpen")
          chart-switch(
            key="2"
            chart-label="Input"
            :chart-data="chartData.Prediction.Input"
          )
        .statistics-box_col
          chart-switch(
            key="3"
            chart-label="Probability to take action vs Taken action"
            :chart-data="chartData.Prediction.Prediction"
            :custom-color="colorList"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Reward'")
      chart-switch(
        key="4"
        chart-label="Reward during one episode"
        :chart-data="chartData.Reward.Current"
      )
      chart-switch(
        key="5"
        chart-label="Reward over all episodes"
        :chart-data="chartData.Reward.Total"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-switch(
        key="6"
        chart-label="Loss during one episode"
        :chart-data="chartData.Loss.Current"
      )
      chart-switch(
        key="7"
        chart-label="Loss over all episodes"
        :chart-data="chartData.Loss.Total"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Steps'")
      chart-switch(
        key="8"
        chart-label="Steps per episode"
        :chart-data="chartData.Steps.Steps"
      )

</template>

<script>
  import ChartSwitch    from "@/components/charts/chart-switch";
  import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";

  export default {
    name: "ViewBoxTrainReinforce",
    components: {ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Prediction: {
            Input: null,
            PvG: null,
            AveragePvG: null,
          },
          Reward: {
            Current: null,
            Total: null,
          },
          Loss: {
            Current: null,
            Total: null,
          },
          Steps: {
            Steps: null
          }
        },
        btnList: {
          'Prediction': {
            btnInteractiveInfo: {
              title: 'Prediction',
              text: 'View the input, current accuracy and <br/> output prediction vs ground truth/labels'
            }
          },
          'Reward': {
            btnInteractiveInfo: {
              title: 'Reward',
              text: 'See the current and total <br/> accumulated Reward'
            }
          },
          'Loss': {
            btnInteractiveInfo: {
              title: 'Loss',
              text: 'See the Loss of the model'
            }
          },
          'Steps': {
            btnInteractiveInfo: {
              title: 'Steps',
              text: 'See how many Steps the model <br/> has taken before it gets a Done state'
            }
          },
        },
        colorList: ['#6B8FF7', '#FECF73'],
      }
    },
    watch: {
      testIsOpen(newVal) {
        newVal ? this.setTab('Prediction') : null
      }
    },
    methods: {
      getData() {
        switch (this.currentTab) {
          case 'Prediction':
            this.chartRequest(this.networkElement.layerId, 'TrainReinforce', 'Prediction');
            break;
          case 'Reward':
            this.chartRequest(this.networkElement.layerId, 'TrainReinforce', 'Reward');
            break;
          case 'Loss':
            this.chartRequest(this.networkElement.layerId, 'TrainReinforce', 'Loss');
            break;
          case 'Steps':
            this.chartRequest(this.networkElement.layerId, 'TrainReinforce', 'Steps');
            break;
        }
      }
    },
  }
</script>
