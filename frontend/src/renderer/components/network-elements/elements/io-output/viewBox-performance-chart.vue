<template lang="pug">
.chart-wrapper-performance
  .select-wrapper
    base-select(
      :value="currentChart",
      @input="handleSelectChart",
      :select-options="chartOptions",
      :selectMultiple="true"
    )
  .labels-wrapper
    base-radio(
      :group-name="chartUUID",
      value-input="Validation",
      v-model="labelForDisplay"
    )
      span Validation
    base-radio(
      :group-name="chartUUID",
      value-input="Training",
      v-model="labelForDisplay"
    )
      span Training
  chart-switch(
    :key="chartUUID",
    :chart-label="chartTitle",
    :chart-data="getChart",
    :custom-color="colorListAccuracy"
  )
</template>
<script>
import ChartSwitch from "@/components/charts/chart-switch";
import { v4 as uuidv4 } from "uuid";
export default {
  name: "ViewBoxPerformanceChart",
  components: {
    ChartSwitch
  },
  props: {
    chartData: Object,
    chartTitle: {
      type: String,
      required: true
    },
    colorListAccuracy: {
      type: Array,
      default: function() {
        return [];
      }
    }
  },
  mounted() {
    if (this.chartData === undefined) {
      return;
    }
    this.initializeChart(this.chartData);
    this.currentChart = [Object.keys(this.chartData)[0]];
  },
  data() {
    return {
      chartUUID: uuidv4(),
      currentChart: [],
      chartOptions: [],
      labelForDisplay: "Validation"
    };
  },
  watch: {
    chartData(val) {
      this.initializeChart(val);
    }
  },
  computed: {
    getChart() {
      const ret = {
        legend: {
          data: []
        },
        series: []
      };
      this.currentChart.forEach(id => {
        function buildPayload(data, id, ix) {
          return {
            ...data[id].series[ix],
            name: data[id].series[ix].name + " " + id
          };
        }

        if (this.labelForDisplay === "Validation") {
          ret.series.push(buildPayload(this.chartData, id, 0));
        } else if (this.labelForDisplay === "Training") {
          ret.series.push(buildPayload(this.chartData, id, 1));
        } else {
          ret.series.push({ name: "", data: [], type: "line", x_data: [] });
        }
      });
      return ret;
    }
  },
  methods: {
    initializeChart(data) {
      if (data === undefined) {
        return;
      }
      if (!this.currentChart.length) {
        this.currentChart = [Object.keys(data)[0]];
      }
      this.chartOptions = Object.keys(data).map(ix => ({
        text: ix,
        value: ix
      }));
    },
    handleSelectChart(val) {
      if (!val.length) {
        this.currentChart = ["0"];
      } else {
        this.currentChart = val;
      }
    }
  }
};
</script>
<style scoped lang="scss">
.chart-wrapper-performance {
  position: relative;
}
.select-wrapper {
  z-index: 1;
  position: absolute;
  right: 2px;
  top: 2px;
  width: 140px;
}
.labels-wrapper {
  position: absolute;
  z-index: 1;
  top: 25px;
  left: 50%;
  transform: translateX(-50%);
}
</style>