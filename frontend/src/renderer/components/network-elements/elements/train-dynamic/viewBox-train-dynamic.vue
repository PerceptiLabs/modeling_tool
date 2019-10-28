<template lang="pug">
  .statistics-box
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row
        .statistics-box_col
          chart-switch(
            key="1"
            :chart-data="optionLine1"
          )
          chart-switch(
            key="2"
            chart-label="Accuracy over all epochs"
            :chart-data="optionLine1"
          )
          chart-switch(
            key="3"
            :chart-data="optionLine1"
          )
        .statistics-box_col
          chart-switch(
            key="4"
            :chart-data="optionHeat"
          )
        .statistics-box_col
          chart-d3(
            key="5"
            :chart-data="option3d"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Accuracy'")
      chart-switch(
        key="6"
        chart-label="Accuracy during one epoch"
        :chart-data="optionLine1"
      )
      chart-switch(
        key="7"
        chart-label="Accuracy over all epochs"
        :chart-data="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-switch(
        key="8"
        chart-label="Loss during one epoch"
        :chart-data="optionLine1"
      )
      chart-switch(
        key="9"
        chart-label="Loss over all epochs"
        :chart-data="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'F1'")
      chart-switch(
        key="10"
        chart-label="F1 during one epoch"
        :chart-data="optionLine1"
      )
      chart-switch(
        key="11"
        chart-label="F1 over all epochs"
        :chart-data="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Precision & Recall'")
      chart-switch(
        key="12"
        :chart-data="optionLine1"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'ROC'")
      chart-switch(
        key="13"
        :chart-data="optionLine1"
      )
</template>

<script>
  import ChartSwitch    from "@/components/charts/chart-switch";

  export default {
    name: "ViewBoxTrainDynamic",
    components: {ChartSwitch},
    data() {
      return {
        tabset: {'Prediction':null, 'Accuracy':null, 'Loss':null, 'F1':null, 'Precision & Recall':null, 'ROC':null},
        optionLine1: null,
        option3d: data3d,
        optionHeat: null,
        optionBar: null,
      }
    },
    methods: {

    }
  }
</script>
