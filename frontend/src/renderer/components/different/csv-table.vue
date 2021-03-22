<template lang="pug">
  .component-wrapper(
    @blur="clearSelectedColumns"
    tabindex="0"
    )
    perfect-scrollbar
      table.table-wrapper(v-if="delimitedDataSet")
        thead
          tr
            th(@click="clearSelectedColumns")
            th.table-column(
              v-for="numColumn in computedNumberOfColumns"
              @click="addSelectedColumn($event, numColumn - 1)"
              :class="{'is-selected': selectedColumns.includes(numColumn - 1)}"
              ) Column {{ numColumn }}
        tbody
          tr.table-row(v-for="dataRow in delimitedDataSet")
            td.no-border(@click="clearSelectedColumns")
            td.table-column(
              v-for="numColumn in computedNumberOfColumns"
              @click="addSelectedColumn($event, numColumn - 1)"
              :class="{'is-selected': selectedColumns.includes(numColumn - 1)}"
              )
              span(v-if="numColumn <= computedNumberOfColumns") {{ dataRow[numColumn-1] }} 
              
              span(v-else) 

          //- Rows for io- and datatypes
          tr.table-row
            td(@click="clearSelectedColumns")
              .label I/O:
            td.table-column.no-padding(
              v-for="numColumn in computedNumberOfColumns"
              :class="{'is-selected': selectedColumns.includes(numColumn - 1)}"
              )
              base-select(
                :select-options="ioOptions"
                :value="formattedDataset.ioTypes[numColumn - 1]"
                @input="setIOSelection($event, numColumn)"
              )
          tr.table-row
            td(@click="clearSelectedColumns")
              .label Type:
            td.table-column.no-padding(
              v-for="numColumn in computedNumberOfColumns"
              :class="{'is-selected': selectedColumns.includes(numColumn - 1)}"
              )
              base-select(
                :select-options="typeOptions"
                :value="formattedDataset.dataTypes[numColumn - 1]"
                @input="setTypeSelection($event, numColumn)"
              )
    //- .delimiter-section
    //-   span Delimiters: 
    //-   input(v-model="delimiters")
</template>

<script>
export default {
  name: 'CSVTable',
  props: {
    dataSet: {
      type: Array,
      default: []
    }
  },
  data() {
    return {
      delimiters: ',',
      ioOptions: ["Input", "Output"],
      typeOptions: ["numerical", "image", "categorical"],
      selectedColumns: [],
      formattedDataset: {
        columnNames: [],
        ioTypes: [],
        dataTypes: []
      }
    }
  },
  computed: {
    computedNumberOfColumns() {
      if (!this.delimitedDataSet || !this.delimitedDataSet.length) { return 0; }

      const longestRow = this.delimitedDataSet.reduce((acc, curr) => acc.length > curr.length ? acc : curr, []);
      return longestRow.length;
    },
    delimitedDataSet() {
      if (!this.delimiters) { return this.dataSet.map(ds => [ds]); }

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
    }
  },
  methods: {
    setIOSelection(event, numColumn) {
      this.formattedDataset.ioTypes.splice(numColumn - 1, 1, event);
      this.emitEvent();
    },
    setTypeSelection(event, numColumn) {
      this.formattedDataset.dataTypes.splice(numColumn - 1, 1, event);
      this.emitEvent();
    },
    emitEvent() {
      this.$emit('update', this.formattedDataset);
    },
    addSelectedColumn(event, columnNumber) {
      // Actions with the meta/CTRL key held down
      if (event.metaKey || event.ctrlKey) {
        if (!this.selectedColumns.includes(columnNumber)) {
          this.selectedColumns.push(columnNumber);
        } else {
          this.selectedColumns = this.selectedColumns.filter(sc => sc !== columnNumber);
        }
      } else {
        this.selectedColumns = [columnNumber];
      }
    },
    clearSelectedColumns() {
      this.selectedColumns = [];
    }
  },
  watch: {
    computedNumberOfColumns: {
      handler(newVal) {
        if (!newVal) { return; }

        this.formattedDataset.columnNames = this.delimitedDataSet[0];
        this.formattedDataset.ioTypes = new Array(newVal);
        this.formattedDataset.dataTypes = new Array(newVal).fill('numerical');
      },
      immediate: true
    }
  }
}
</script>

<style lang="scss" scoped>

  .component-wrapper {
    height: 100%;
    width: 100%;
    box-sizing: border-box;

    & > .ps {
        height: 100%;
        width: 100%;
    }
  }

  .table-wrapper {
    display: table;

    width: 100%;

    box-sizing: border-box;
  }

  th.table-column {
    background-color: #363E51;

    // &.is-selected {
    //   background-color: rgba(97, 133, 238, 0.5);
    // }
  }

  .table-column {
    text-align: left;
    padding: 1rem;
    border: 1px solid #4D556A;
    
    white-space: nowrap;
  }

  .no-padding {
    padding: 0;
  }

  th {
    &.is-selected {
      background-color: rgba(97, 133, 238, 0.5);
    }
    
    > *:first-of-type {
      width: 5rem;
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
  }

  .delimiter-section {
    margin: 1rem;
  }

</style>