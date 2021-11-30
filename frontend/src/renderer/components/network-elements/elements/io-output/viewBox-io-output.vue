<template lang="pug">
.statistics-box
  .statistics-box_main.statistics-box_col(v-if="currentTab !== 'Global Loss'")
    div(
      :class="`${getChartDisplayClass()}`",
      v-if="sectionTitle === 'Statistics' && currentTab !== 'Performance'"
    )
      template(v-if="chartData.hasOwnProperty('Accuracy')")
        chart-switch(
          key="1",
          chart-label="Accuracy during one epoch",
          :chart-data="chartData.Accuracy.OverSteps",
          :custom-color="colorListAccuracy"
        )
        chart-switch(
          key="2",
          chart-label="Accuracy over all epochs",
          :chart-data="chartData.Accuracy.OverEpochs",
          :custom-color="colorListAccuracy"
        )
      template(v-if="chartData.hasOwnProperty('LossAndAccuracy')")
        chart-switch(
          key="1",
          chart-label="Loss over all epochs",
          :chart-data="chartData.LossAndAccuracy.LossOverEpochs",
          :custom-color="colorListAccuracy"
        )
        chart-switch(
          key="2",
          chart-label="Accuracy over all epochs",
          :chart-data="chartData.LossAndAccuracy.AccOverEpochs",
          :custom-color="colorListAccuracy"
        )
      template(v-if="chartData.hasOwnProperty('LossAndRSquared')")
        chart-switch(
          key="1",
          chart-label="Loss over all epochs",
          :chart-data="chartData.LossAndRSquared.LossOverEpochs",
          :custom-color="colorListAccuracy"
        )
        chart-switch(
          key="2",
          chart-label="R Squared over all epochs",
          :chart-data="chartData.LossAndRSquared.RSquaredOverEpochs",
          :custom-color="colorListAccuracy"
        )
      template(v-if="chartData.hasOwnProperty('PvGAndConfusionMatrix')")
        chart-switch(
          key="3",
          chart-label="Prediction vs Ground truth",
          :chart-data="chartData.PvGAndConfusionMatrix.Sample",
          :custom-color="colorList"
        )
        chart-switch(
          key="4",
          chart-label="Predictions for Each Class",
          :chart-data="chartData.PvGAndConfusionMatrix.LastEpoch",
          :custom-color="colorList"
        )
      template(v-if="chartData.hasOwnProperty('PvGAndMAE')")
        chart-switch(
          key="3",
          chart-label="Mean Absolute Error over all Epochs",
          :chart-data="chartData.PvGAndMAE.MAEOverEpochs",
          :custom-color="colorList"
        )
        chart-switch(
          key="4",
          chart-label="Prediction vs Ground truth",
          :chart-data="chartData.PvGAndMAE.Sample",
          :custom-color="colorList"
        )
      template(v-if="chartData.hasOwnProperty('PvG')")
        chart-switch(
          key="3",
          chart-label="Prediction vs Ground truth",
          :chart-data="chartData.PvG.Sample",
          :custom-color="colorList"
        )
        chart-switch(
          key="4",
          chart-label="Batch Average Prediction vs Ground truth",
          :chart-data="chartData.PvG.BatchAverage",
          :custom-color="colorList"
        )
      template(v-if="chartData.hasOwnProperty('PvGAndImage')")
        chart-switch(
          key="3",
          chart-label="Prediction overlayed with Ground truth",
          :chart-data="chartData.PvGAndImage.Sample",
          :custom-color="colorList"
        )
        chart-switch(
          key="4",
          chart-label="Predicted image",
          :chart-data="chartData.PvGAndImage.Prediction",
          :custom-color="colorList"
        )
      template(v-if="chartData.hasOwnProperty('IoU')")
        chart-switch(
          key="5",
          chart-label="IoU during one epoch",
          :chart-data="chartData.IoU.OverSteps",
          :custom-color="colorListAccuracy"
        )
        chart-switch(
          key="6",
          chart-label="IoU over all epochs",
          :chart-data="chartData.IoU.OverEpochs",
          :custom-color="colorListAccuracy"
        ) 
      template(v-if="chartData.hasOwnProperty('IoUAndLoss')")
        chart-switch(
          key="5",
          chart-label="Loss over all epochs",
          :chart-data="chartData.IoUAndLoss.LossOverEpochs",
          :custom-color="colorListAccuracy"
        )
        chart-switch(
          key="6",
          chart-label="IoU over all epochs",
          :chart-data="chartData.IoUAndLoss.IoUOverEpochs",
          :custom-color="colorListAccuracy"
        )
    template(
      v-else-if="sectionTitle === 'Statistics' && currentTab === 'Performance'"
    )
      .statistics-box_row
        .statistics-box_col
          view-box-performance-chart(
            :chartData="chartData.Precision && chartData.Precision.PrecisionOverEpochs",
            :colorListAccuracy="colorListAccuracy",
            chartTitle="Precision"
          )
        .statistics-box_col
          view-box-performance-chart(
            :chartData="chartData.Recall && chartData.Recall.RecallOverEpochs",
            :colorListAccuracy="colorListAccuracy",
            chartTitle="Recall"
          )
        .statistics-box_col
          view-box-performance-chart(
            :chartData="chartData.F1 && chartData.F1.F1OverEpochs",
            :colorListAccuracy="colorListAccuracy",
            chartTitle="F1"
          )
    template(v-else-if="chartData.hasOwnProperty('ViewBox')")
      chart-switch(
        key="7",
        chart-label="Output",
        :chart-data="chartData.ViewBox.Output",
        :custom-color="colorListAccuracy"
      )

  .statistics-box_main.statistics-box_col(
    v-if="currentTab === 'Global Loss' && chartData.Loss"
  )
    template(v-if="sectionTitle === 'Statistics'")
      chart-switch(
        key="8",
        chart-label="Loss during one epoch",
        :chart-data="chartData.Loss.OverSteps",
        :custom-color="colorListAccuracy"
      )
      chart-switch(
        key="9",
        v-if="chartData.Loss.OverSteps",
        chart-label="Loss over all epochs",
        :chart-data="chartData.Loss.OverEpochs",
        :custom-color="colorListAccuracy"
      )
    tempalate(v-else)
      chart-switch(
        key="10",
        chart-label="Output",
        :chart-data="chartData.ViewBox.Output",
        :custom-color="colorListAccuracy"
      )
</template>

<script>
import ChartSwitch from "@/components/charts/chart-switch";
import viewBoxMixin from "@/core/mixins/net-element-viewBox.js";
import netIOTabs from "@/core/mixins/net-IO-tabs.js";
import ViewBoxPerformanceChart from "./viewBox-performance-chart.vue";

export default {
  name: "ViewBoxIoOutput",
  components: {
    ChartSwitch,
    ViewBoxPerformanceChart
  },
  mixins: [viewBoxMixin, netIOTabs],
  props: {
    el: Object
  },
  data() {
    return {
      chartData: {
        Data: {},
        Loss: {},
        Accuracy: {
          OverEpochs: {},
          OverSteps: {}
        },
        PvG: {
          Sample: {},
          BatchAverage: {}
        },
        ViewBox: {
          Output: {}
        }
      },

      colorList: ["#6B8FF7", "#FECF73"],
      colorListAccuracy: ["#9173FF", "#6B8FF7"],
      colorPie: ["#6B8FF7", "#383F50"],
      showRequestSpinner: {
        Input: true,
        PvG: true,
        AveragePvG: true,
        Accuracy: true
      }
    };
  },
  watch: {
    testIsOpen(newVal) {
      newVal ? this.setTab("Prediction") : null;
    }
  },
  methods: {
    getChartDisplayClass() {
      const classNamePrefixes = {
        1: "one",
        2: "two",
        4: "four"
      };
      let itemsCount = 0;
      Object.keys(this.chartData).forEach(key => {
        if (key !== "ViewBox" && key !== "__ob__") {
          let itm = this.chartData[key];
          itemsCount += Object.keys(itm).length;
        }
      });
      return `four-box-display`;
    },
    getData() {
      switch (this.currentTab) {
        case "Global Loss":
          this.chartGlobalRequest();
          break;
        default:
          this.chartRequest(this.networkElement.layerId, "IoOutput", "");
          break;
      }
    }
  }
};
</script>
<style scoped lang="scss">
.one-box-display {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  > .base-chart:not(.full-view) {
    width: calc(100% - 5px);
    height: calc(100% - 5px);
    margin-bottom: 6px;
  }
  > .base-chart:nth-child(2n):not(.full-view) {
    margin-left: 10px;
  }
}
.two-box-display {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  > .base-chart:not(.full-view) {
    width: calc(50% - 5px);
    height: calc(100% - 5px);
    margin-bottom: 6px;
  }
  > .base-chart:nth-child(2n):not(.full-view) {
    margin-left: 10px;
  }
}
.four-box-display {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  > .base-chart:not(.full-view) {
    width: calc(50% - 5px);
    height: calc(50% - 5px);
    margin-bottom: 6px;
  }
  > .base-chart:nth-child(2n):not(.full-view) {
    margin-left: 10px;
  }
}
</style>