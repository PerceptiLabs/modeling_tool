<template lang="pug">
  div
    div.head {{testFeature}}  Metrics Table
    div.body
      table
        thead
          tr
            td(v-for="name in columnsNames") {{ name }}
        tbody
          tr(v-for="(data, modelId) in testData")
            td {{modelName(modelId)}}
            td(:title="value")(v-for="value in data[testFeature]") {{ (value).toFixed(4) }}
</template>
<script>
import { getFirstElementFromObject } from "@/core/helpers";

const tableColumnNamePretty =  {
  categorical_accuracy: 'Categorical Accuracy',
  top_k_categorical_accuracy: 'Top K categorical Accuracy',
  precision: 'Precision',
  recall: 'Recall',
}

export default {
  name: "MetricTableTestTable",
  data() {
    return {
      columnsNames: [
        'Model Name', // other will be filled by fn:setTableHeadColumnNames 
      ],
    }
  },
  props: {
    testData: {
      type: Object,
      default: {}
    },
    testFeature: {
      type: String,
      default: '',
    }
  },
  created() {
    this.setTableHeadColumnNames(this.testData);
  },
  methods: {
    setTableHeadColumnNames(data) {
      let chartData = getFirstElementFromObject(data);
      chartData = getFirstElementFromObject(chartData);
      Object.keys(chartData).forEach(key => {
        this.columnsNames.push(tableColumnNamePretty[key] || key);
      })  
    },
    modelName(id){
      return this.$store.getters['mod_workspace/GET_modelName'](id);
    },
  }
}
</script>
<style lang="scss" scoped>
  .head {
    display: flex;
    align-items: center;
    flex: 0 0 auto;
    justify-content: space-between;
    width: 100%;
    height: 2.5rem;
    padding: 0 1rem 0 1rem;
    border: 1px solid rgba(97, 133, 238, 0.4);
    border-radius: 2px 2px 0 0;
    background: #3F4C70;
  }
  .body {
    background: #212839;
    padding: 20px;
    
  }
  table {
    font-size: 14px;
    width: 100%;
    text-align: center;
  }
  td {
    padding: 10px 5px;
    border: 1px solid #4D556A;
  }
  .chart-container {
    width: calc(50% - 20px);
    margin: 10px;
  }
  .wrap {
    width: 100%;
    display: flex;
  }
</style>