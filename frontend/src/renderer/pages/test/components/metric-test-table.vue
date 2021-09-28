<template lang="pug">
  div.wrapper
    div.head {{testFeature}} {{name}}
    div.body
      table
        thead
          tr
            th(v-for="name in columnsNames") {{ name }}
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
  dice_coefficient: 'Dice coefficient',
  IoU: 'Intersection over Union',
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
    },
    name: {
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
  
  .wrapper {
    background: theme-var($neutral-8);
    padding: 20px 25px;
    border: $border-1;
    border-radius: 4px;
  }

  .head {
    display: flex;
    align-items: center;
    flex: 0 0 auto;
    justify-content: space-between;    
    width: 100%;
    color: $color-6;
    font-size: 14px;
  }
  .body {
    margin-top: 20px;    
  }
  table {
    font-size: 14px;
    width: 100%;
    text-align: center;
  }
  th {    
    padding: 10px 5px;
    border: $border-1;
    background: theme-var($neutral-7);
  }
  td {
    padding: 10px 5px;
    border: $border-1;
  }
</style>