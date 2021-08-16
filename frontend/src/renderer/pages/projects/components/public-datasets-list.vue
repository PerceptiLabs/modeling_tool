<template lang="pug">
chart-spinner(v-if="isLoading")
.public-datasets-page(v-else)
  .header
    span Show public datasets for &nbsp;
    .form_input.select
      base-select(
        style-type="darken",
        v-model="category",
        :select-options="categories"
      )
  perfect-scrollbar.table-container
    table.dataset-table
      thead
        tr
          th(v-for="field in fields", :key="field") {{ field }}
          th
      tbody
        tr(v-for="dataset in filteredList", :key="dataset.name")
          td(v-for="field in fields", :key="field") {{ dataset[field] }}
          td
            button.action-button Load
        tr
          td(span=5)
  .footer-actions
    button.go-back-btn(@click="goBack()")
      img(src="./../../../../../static/img/arrow-back.svg")
      | Upload .CSV
</template>

<script>
import ChartSpinner from "@/components/charts/chart-spinner";

import { parse } from "papaparse";

export default {
  components: { ChartSpinner },
  data: () => ({
    isLoading: false,
    categories: [],
    category: "",
    datasetList: [],
    fields: [],
  }),

  mounted() {
    console.log("mounted");
    this.readDatasetList();
  },

  methods: {
    readDatasetList() {
      this.isLoading = true;

      fetch("https://perceptilabs.blob.core.windows.net/data/dataset-list.csv")
        .then((res) => res.text())
        .then((res) => parse(res, { header: true }))
        .then(({ data, meta }) => {
          this.datasetList = data;
          this.fields = meta.fields.filter((field) => field !== "Category");
          this.categories = data
            .map((item) => item.Category)
            .filter((e, i, a) => a.indexOf(e) === i);
          this.category = this.categories[0];
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
    goBack() {
      this.$emit('goBack');
    }
  },

  computed: {
    filteredList() {
      return this.datasetList.filter((item) => item.Category === this.category);
    },
  },
};
</script>

<style lang="scss" scoped>
.public-datasets-page {
  padding: 30px;

  .header {
    display: flex;
    span {
      font-size: 16px;
      line-height: 36px;
    }
    .select {
      width: 150px;
    }
  }
}
.table-container {
  height: 300px;
  overflow: auto;
  margin: 30px 0;
  border: 1px solid #5e6f9f;
  border-radius: 4px;
}
.dataset-table {
  width: 100%;
  font-size: 16px;
  line-height: 32px;

  color: #e1e1e1;

  thead {
    background-color: #202634;
    border-bottom: 1px solid #5e6f9f;
  }
  tbody {
    tr {
      &.disabled {
        pointer-events: none;
        filter: grayscale(1);
        * {
          color: grey;
        }
      }

      &.loading {
        background-color: #1d253d;
        position: relative;

        &:after {
          content: "";
          position: absolute;
          width: 100%;
          height: 4px;
          background: #505050;
          bottom: 0;
          left: 0;
        }

        .action-button {
          display: block;
        }
      }
      &.loaded {
        background-color: #1d253d;
        position: relative;

        .action-button {
          display: block;
        }
      }
      .progress-bar {
        position: absolute;
        height: 4px;
        background: #6185ee;
        bottom: 0;
        left: 0;
        z-index: 1;
      }

      .action-button {
        display: none;
      }
      &:hover {
        background-color: #1d253d;
        .action-button {
          display: block;
        }
      }
    }
  }
  th,
  td {
    padding: 8px 16px;
    text-align: left;

    &:last-child {
      width: 158px;
    }

    a {
      text-decoration: underline;
      color: #b6c7fb;
    }
  }
}

.go-back-btn {
  border: none;
  background: transparent;
  color: #fff;
  font-size: 16px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  img {
    margin-right: 20px;
  }
}

.action-button {
  height: 32px;

  background: #6185ee;
  box-sizing: border-box;
  border-radius: 2px;
  box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.25);

  font-family: Nunito Sans, sans-serif;
  font-style: normal;
  font-weight: 600;
  font-size: 16px;
  line-height: 22px;

  text-align: center;

  color: #ffffff;
  &.is-disabled {
    background-color: rgb(120, 120, 120);
    cursor: not-allowed;
  }
}
</style>