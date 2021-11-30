<template lang="pug">
.component-wrapper(@blur="clearSelectedColumns", tabindex="0")
  .csv-table-scrollbar-wrapper
    table.table-wrapper(v-if="delimitedDataSet")
      thead.bold
        tr(:data-tutorial-target="'tutorial-data-wizard-csv-explanation'")
          //- th(@click="clearSelectedColumns")
          th.table-column(
            v-for="(numColumn, ix) in delimitedDataSet[0]",
            :key="numColumn",
            @click="addSelectedColumn($event, numColumn - 1)",
            :class="{ 'is-selected': selectedColumns.includes(numColumn - 1) }"
          )
            .d-flex.justify-between
              div {{ numColumn }}
              data-column-options(
                :columnSelectedType="formattedDataset.dataTypes",
                :index="ix"
              )
      tbody
        tr.table-row.default-row(v-for="dataRow in delimitedDataSet.slice(1)")
          //- td.no-border(@click="clearSelectedColumns")
          td.table-column.justify-left(
            v-for="numColumn in computedNumberOfColumns",
            @click="addSelectedColumn($event, numColumn - 1)",
            :class="{ 'is-selected': selectedColumns.includes(numColumn - 1) }"
          )
            div.d-inline-block(v-if="numColumn <= computedNumberOfColumns" v-tooltip:bottom="dataRow[numColumn - 1]") {{ strShortener(dataRow[numColumn - 1]) }}

            div.d-inline-block(v-else) utton.custom-select_view

        //- Rows for io- and datatypes @TODO can be extracted as separate table on bottom of top one

        tr.table-row
          td.space-cell(v-for="numColumn in computedNumberOfColumns") &nbsp;
        tr.table-row(test-id="io-selection-row")
          //- td(@click="clearSelectedColumns")
          //-   .label I/O:
          td.table-column.no-padding.io-cell(
            v-for="numColumn in computedNumberOfColumns",
            :class="{ 'is-selected': selectedColumns.includes(numColumn - 1) }"
          )
            base-select(
              v-if="!locked || !elementToFeatures",
              :style-type="`text-center ${lastTypeUnselected === numColumn - 1 ? 'active' : ''}`",
              selectPlaceholder="Select",
              :select-options="ioOptions",
              :value="formattedDataset.ioTypes[numColumn - 1]",
              @input="setIOSelection($event, numColumn)"
            )
            .text-center(v-else) {{ getColumnIOType(numColumn - 1) }}
        tr.table-row(
          :data-tutorial-target="'tutorial-data-wizard-io-explanation'"
        )
          //- td(@click="clearSelectedColumns")
          //-   .label Type:
          td.table-column.no-padding.io-cell(
            v-for="numColumn in computedNumberOfColumns",
            :class="{ 'is-selected': selectedColumns.includes(numColumn - 1) }"
          )
            base-select(
              style-type="text-center",
              selectPlaceholder="Select",
              :select-options="formattedDataset.columnOptions[numColumn - 1]",
              :value="formattedDataset.dataTypes[numColumn - 1]",
              @input="setTypeSelection($event, numColumn)"
            )
  //- .delimiter-section
  //-   span Delimiters: 
  //-   input(v-model="delimiters")
  .warning-section(v-if="hasMetaDataType")
    svg(
      width="20",
      height="20",
      viewBox="0 0 11 10",
      fill="none",
      xmlns="http://www.w3.org/2000/svg"
    )
      path(
        d="M4.60311 0.52108C4.9924 -0.173694 6.0076 -0.173693 6.39689 0.521081L10.8714 8.50661C11.2475 9.1779 10.7538 10 9.97446 10H1.02554C0.246238 10 -0.247494 9.1779 0.128646 8.50661L4.60311 0.52108Z",
        fill="#FECF73"
      )
      path(
        d="M5 3.3335L6 3.33979L5.74675 6.44335H5.25325L5 3.3335ZM5.95455 6.9092V7.77794H5.04545V6.9092H5.95455Z",
        fill="#23252A"
      )
    span The Mask datatype automatically resizes to 224x224 (standard size for pre-trained UNets), you may want to resize the Image Input to the same if you have not already.
</template>

<script>
import DataColumnOptions from "@/components/different/data-column-options";
import { strShortener } from "@/core/helpers";

export default {
  name: "CSVTable",
  components: {
    DataColumnOptions
  },
  props: {
    dataSet: {
      type: Array,
      default: [],
    },
    dataSetTypes: {
      type: Object
    },
    locked: {
      type: Boolean,
      default: false
    },
    elementToFeatures: {
      type: Object,
      required: false,
      default: () => ({}),
    },
  },
  data() {
    return {
      delimiters: ",",
      ioOptions: ["Input", "Target", "Do not use"],
      selectedColumns: [],
      formattedDataset: {
        columnNames: [],
        ioTypes: [],
        dataTypes: [],
        columnOptions: [],
        preprocessingTypes: []
      }
    };
  },
  computed: {
    lastTypeUnselected() {
      const arrLength = this.formattedDataset.ioTypes.length;

      for (let i = 0; i < arrLength; i++) {
        if (this.formattedDataset.ioTypes[i] === undefined) {
          return i;
        }
      }
    },
    computedNumberOfColumns() {
      if (!this.delimitedDataSet || !this.delimitedDataSet.length) {
        return 0;
      }

      const longestRow = this.delimitedDataSet.reduce(
        (acc, curr) => (acc.length > curr.length ? acc : curr),
        []
      );
      return longestRow.length;
    },
    delimitedDataSet() {
      if (!this.delimiters) {
        return this.dataSet.map(ds => [ds]);
      }

      const rows = [];

      for (const ds of this.dataSet) {
        const subString = [];
        let fast = 0;
        let slow = 0;

        while (fast < ds.length) {
          if (this.delimiters.includes(ds[fast])) {
            subString.push(ds.slice(slow, fast));
            fast++;
            slow = fast;
          } else {
            fast++;
          }
        }

        if (fast != slow) {
          subString.push(ds.slice(slow, fast));
        }

        rows.push(subString);
      }

      return rows;
    },
    datasetFields() {
      return this.delimitedDataSet[0].map(s => s.trim());
    },
    hasMetaDataType() {
      return this.formattedDataset.dataTypes.find(
        dataType => dataType === "mask"
      );
    }
  },
  methods: {
    strShortener(url) {
      return strShortener(url, 20);
    },
    setIOSelection(event, numColumn) {
      this.formattedDataset.ioTypes.splice(numColumn - 1, 1, event);
      this.emitEvent();
    },
    setTypeSelection(event, numColumn) {
      this.formattedDataset.dataTypes.splice(numColumn - 1, 1, event);
      this.emitEvent();
    },
    emitEvent() {
      this.$emit("update", this.formattedDataset);
    },
    addSelectedColumn(event, columnNumber) {
      // Actions with the meta/CTRL key held down
      if (event.metaKey || event.ctrlKey) {
        if (!this.selectedColumns.includes(columnNumber)) {
          this.selectedColumns.push(columnNumber);
        } else {
          this.selectedColumns = this.selectedColumns.filter(
            sc => sc !== columnNumber
          );
        }
      } else {
        this.selectedColumns = [columnNumber];
      }
    },
    clearSelectedColumns() {
      this.selectedColumns = [];
    },
    handleColumnPreprocessingChange(numColumn, value) {
      this.formattedDataset.preprocessingTypes.splice(numColumn, 1, value);
      this.emitEvent();
    },
    getColumnIOType(index) {
      const columnName = this.datasetFields[index];
      // column isn't used
      if (!this.elementToFeatures.hasOwnProperty(columnName)) {
        return this.ioOptions[2];
      }

      const layerName = this.elementToFeatures[columnName].layerName;

      const layerList = this.$store.getters[
        "mod_workspace/GET_currentNetworkElementList"
      ];
      const el = Object.values(layerList).find(
        el => el.layerName === layerName
      );
      if (el.layerType === "IoInput") {
        return this.ioOptions[0];
      } else if (el.layerType === "IoOutput") {
        return this.ioOptions[1];
      }
    }
  },
  watch: {
    computedNumberOfColumns: {
      handler(newVal) {
        if (!newVal) {
          return;
        }
        let columnDefaultTypes = [];
        let columnAllowedTypes = [];
        let columnNames = this.delimitedDataSet[0];

        columnNames = columnNames.map((name, ix) => {
          name = name.replace(/(\r\n|\n|\r)/gm, "");
          const itm = this.dataSetTypes[name];
          columnDefaultTypes[ix] =
            this.elementToFeatures[name] &&
            this.elementToFeatures[name].dataType
              ? this.elementToFeatures[name].dataType
              : itm[0][itm[1]];
          columnAllowedTypes[ix] = itm[0];
          return name;
        });

        this.formattedDataset.columnNames = columnNames;
        this.formattedDataset.ioTypes = new Array(newVal);

        this.formattedDataset.dataTypes = columnDefaultTypes;
        this.formattedDataset.columnOptions = columnAllowedTypes;
        this.formattedDataset.preprocessingTypes = new Array(newVal).fill({});
        this.$emit("update", this.formattedDataset);
      },
      immediate: true
    }
  }
};
</script>

<style lang="scss" scoped>
.component-wrapper {
  width: 100%;
}
.csv-table-scrollbar-wrapper {
  padding: 0 5px;
}

.justify-between {
  justify-content: space-between;
}

.table-wrapper {
  display: table;

  width: 100%;

  box-sizing: border-box;
  thead {
    .table-column {
      font-family: Roboto;
      font-size: 14px;
      line-height: 24px;
      text-align: left;
      font-weight: normal;
      letter-spacing: 0.02em;
      background: theme-var($neutral-7);
    }
  }
  tbody {
    .default-row {
      .table-column {
        text-align: left;
        font-size: 14px;
      }
    }

    &:last-child {
      border-radius: 4px;
    }
  }
  .io-cell {
  }
  .space-cell {
    height: 20px;
  }
}

th.table-column {
  background-color: #363e51;

  // &.is-selected {
  //   background-color: rgba(97, 133, 238, 0.5);
  // }
}

.table-column {
  padding: 1rem;
  border: $border-1;

  white-space: nowrap;
}

.no-padding {
  padding: 0;
}

th {
  &.is-selected {
    background-color: rgba(97, 133, 238, 0.5);
  }
}

td {
  &.is-selected {
    background-color: rgba(97, 133, 238, 0.2);
  }

  &.no-border {
    border: 0;
  }

  > .label {
    width: 5rem;
    font-weight: bold;
    font-size: 12px;
  }
}

/deep/ button.custom-select_view {
  background-color: transparent;
  height: 50px;
  border-color: transparent;
}

.delimiter-section {
  margin: 1rem;
}

.table-column {
  height: 50px;
}

.warning-section {
  margin-top: 10px;
  max-width: 100%;
  font-size: 14px;
  line-height: 18px;

  display: flex;
  align-items: center;

  span {
    margin-left: 10px;
  }
}

.d-inline-block {
  display: inline-block;
}
</style>
