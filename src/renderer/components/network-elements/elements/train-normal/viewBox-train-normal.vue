<template lang="pug">
  .statistics-box
    ul.statistics-box_tabset(v-if="!testIsOpen")
      li.statistics-box_tab(
      v-for="(tab, i) in tabset"
      :key="i"
      )
        //:disabled="i > 2"
        button.btn.btn--tabs.tutorial-relative(
        type="button"
        v-tooltip-interactive:right="tab.interactiveInfo"
        @click="setTab(tab.name, tab.id)"
        :class="{'active': currentTab === tab.name}"
        
        :id="tab.id"
        ) {{ tab.name }}
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Prediction'")
      .statistics-box_row(v-if="!testIsOpen")
        .statistics-box_col
          chart-switch(
            key="1"
            chart-label="Input"
            :chart-data="chartData.Prediction.Input"
            )
        .statistics-box_col
          chart-pie(
            key="8"
            chart-label="Accuracy"
            :chart-data="chartData.Prediction.Accuracy"
            :custom-color="colorPie"
          )
      .statistics-box_row
        .statistics-box_col
          chart-base#tutorial_prediction-chart(
            key="2"
            chart-label="Prediction vs Ground truth"
            :chart-data="chartData.Prediction.PvG"
            :custom-color="colorList"
          )
        .statistics-box_col(v-if="!testIsOpen")
          chart-base(
            key="3"
            chart-label="Batch Average Prediction vs Ground truth"
            :chart-data="chartData.Prediction.AveragePvG"
            :custom-color="colorList"
          )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Accuracy'")
      chart-base(
        key="4"
        chart-label="Accuracy during one epoch"
        :chart-data="chartData.Accuracy.Current"
        :custom-color="colorListAccuracy"
      )
      chart-base(
        key="5"
        chart-label="Accuracy over all epochs"
        :chart-data="chartData.Accuracy.Total"
        :custom-color="colorListAccuracy"
      )
    .statistics-box_main.statistics-box_col(v-if="currentTab === 'Loss'")
      chart-base(
        key="6"
        chart-label="Loss during one epoch"
        :chart-data="chartData.Loss.Current"
        :custom-color="colorListAccuracy"
      )
      chart-base(
        key="7"
        chart-label="Loss over all epochs"
        :chart-data="chartData.Loss.Total"
        :custom-color="colorListAccuracy"
      )
    //.statistics-box_main.statistics-box_col(v-if="currentTab === 'F1'")
      chart-base(
      chartLabel="F1 during one epoch"
      /:chartData="optionLine1"
      )
      chart-base(
      chartLabel="F1 over all epochs"
      /:chartData="optionLine1"
      )
    //.statistics-box_main.statistics-box_col(v-if="currentTab === 'Precision & Recall'")
      chart-base(
      /:chartData="optionLine1"
      )
    //.statistics-box_main.statistics-box_col(v-if="currentTab === 'ROC'")
      chart-base(
      /:chartData="optionLine1"
      )
</template>

<script>
  import ChartBase      from "@/components/charts/chart-base";
  import ChartPie       from "@/components/charts/chart-pie";
  import ChartHeatmap   from "@/components/charts/chart-heatmap.vue";
  import ChartD3        from "@/components/charts/chart-3d.vue";
  import ChartSwitch    from "@/components/charts/chart-switch.vue";

  import viewBoxMixin   from "@/core/mixins/net-element-viewBox.js";
  import { mapActions } from 'vuex';

  export default {
    name: "ViewBoxTrainNormal",
    components: {ChartBase, ChartPie, ChartHeatmap, ChartD3, ChartSwitch},
    mixins: [viewBoxMixin],
    data() {
      return {
        chartData: {
          Prediction: {
            Input: null,
            PvG: null,
            AveragePvG: null,
            Accuracy: null
          },
          Accuracy: {
            Current: null,
            Total: null,
          },
          Loss: {
            Current: null,
            Total: null,
          }
        },
        currentTab: 'Prediction',
        tabset: [
          {
            name: 'Prediction',
            id: 'tutorial_prediction-tab',
            interactiveInfo: `<div class="tooltip-tutorial_italic">
                                <img src="../../../../../../static/img/logo_small_dark.svg" alt=""></br>
                                <div class="tooltip-tutorial_bold">Lorem Ipsum:</div> is simply dummy text</br> the printing and typesetting  </br> industry. Lorem Ipsum </br>
                                <div class="tooltip-tutorial_bold">Has been the industry's standard</div>
                              </div>`
          },
          {
            name: 'Accuracy',
            id: 'tutorial_accuracy-tab',
            interactiveInfo: `<div class="tooltip-tutorial_italic">
                                <img src="../../../../../../static/img/logo_small_dark.svg" alt=""></br>
                                <div class="tooltip-tutorial_bold">Lorem Ipsum:</div> is simply dummy text</br> the printing and typesetting  </br> industry. Lorem Ipsum </br>
                                <div class="tooltip-tutorial_bold">Has been the industry's standard</div>
                              </div>`
          },
          {
            name: 'Loss',
            id: 'tutorial_loss-tab',
            interactiveInfo: `<div class="tooltip-tutorial_italic">
                                <img src="../../../../../../static/img/logo_small_dark.svg" alt=""></br>
                                <div class="tooltip-tutorial_bold">Lorem Ipsum:</div> is simply dummy text</br> the printing and typesetting  </br> industry. Lorem Ipsum </br>
                                <div class="tooltip-tutorial_bold">Has been the industry's standard</div>
                              </div>`
          },
          {
            name: 'F1',
            id: 'tutorial_f1-tab',
            interactiveInfo: `<div class="tooltip-tutorial_italic">
                                <img src="../../../../../../static/img/logo_small_dark.svg" alt=""></br>
                                <div class="tooltip-tutorial_bold">Lorem Ipsum:</div> is simply dummy text</br> the printing and typesetting  </br> industry. Lorem Ipsum </br>
                                <div class="tooltip-tutorial_bold">Has been the industry's standard</div>
                              </div>`
          },
          {
            name: 'Precision & Recall',
            id: 'tutorial_precision-tab',
            interactiveInfo: `<div class="tooltip-tutorial_italic">
                                <img src="../../../../../../static/img/logo_small_dark.svg" alt=""></br>
                                <div class="tooltip-tutorial_bold">Lorem Ipsum:</div> is simply dummy text</br> the printing and typesetting  </br> industry. Lorem Ipsum </br>
                                <div class="tooltip-tutorial_bold">Has been the industry's standard</div>
                              </div>`
          },
          {
            name: 'ROC',
            id: 'tutorial_roc-tab',
            interactiveInfo: `<div class="tooltip-tutorial_italic">
                                <img src="../../../../../../static/img/logo_small_dark.svg" alt=""></br>
                                <div class="tooltip-tutorial_bold">Lorem Ipsum:</div> is simply dummy text</br> the printing and typesetting  </br> industry. Lorem Ipsum </br>
                                <div class="tooltip-tutorial_bold">Has been the industry's standard</div>
                              </div>`
          }
        ],
        colorList: ['#6B8FF7', '#FECF73'],
        colorListAccuracy: ['#9173FF', '#6B8FF7'],
        colorPie: ['#6B8FF7', '#383F50']
      }
    },
    watch: {
      testIsOpen(newVal) {
        newVal ? this.setTab('Prediction') : null
      }
    },
    methods: {
      ...mapActions({
        tutorialPointActivate:    'mod_tutorials/pointActivate',
      }),
      setTab(name, id) {
        this.currentTab = name;
        this.setTabAction();
        this.tutorialPointActivate({way: 'next', validation: id})
      },
      getData() {
        switch (this.currentTab) {
          case 'Prediction':
            this.chartRequest(this.statElementID, 'TrainNormal', 'Prediction');
            break;
          case 'Accuracy':
            this.chartRequest(this.statElementID, 'TrainNormal', 'Accuracy');
            break;
          case 'Loss':
            this.chartRequest(this.statElementID, 'TrainNormal', 'Loss');
            break;
        }
      }
    },
  }
</script>
