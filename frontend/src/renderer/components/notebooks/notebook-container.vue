<template>
  <div id="notebook-container">
    <section id="toolbar">
      <notebook-toolbar 
        :isSessionOnline="isSessionOnline" />
    </section>
    <div id="cell-list">
      <notebook-cell
        v-for="cell in cells"
        :key="cell.hashCode"
        :cell="cell"
        @click="cellClicked"
        :isFocused="cell.hashCode == focusedCellHashCode"
      />
    </div>
  </div>
</template>

<script>
import NotebookToolbar from "./NotebookToolbar.vue";
import NotebookCell from "./NotebookCell.vue";

import { notebookActions } from '@/helpers/JupyterNotebook';

export default {
  components: {
    NotebookToolbar,
    NotebookCell
  },
  data() {
    return {
      notebookServer: {
        url: "http://127.0.0.1:8888",
        notebookName: "notebook.ipynb",
        token: "?token=abc"
      },
      cells: [],
      focusedCellHashCode: "",
      session: null
    };
  },
  computed: {
    isSessionOnline() { return !!this.session; }
  },
  created() {
    notebookActions.init({
      url: this.notebookServer.url,
      notebookName: this.notebookServer.notebookName,
      token: this.notebookServer.token,
    });

    this.getNotebookContents();
    this.startSession();
  },
  methods: {
    cellClicked(cellHashCode) {
      this.focusedCellHashCode = cellHashCode;
    },
    getCellHashCode(cell) {
      if (!cell) {
        return;
      }

      let hashCode = this.hashCode(cell.cell_type) ^ this.hashCode(cell.source);

      return hashCode;
    },
    hashCode(string) {
      let hash = 13;
      if (string.length == 0) {
        return hash;
      }
      for (let i = 0; i < string.length; i++) {
        let char = string.charCodeAt(i);
        hash = (hash << 5) - hash + char;
        hash = hash & hash; // Convert to 32bit integer
      }
      return hash;
    },
    getNotebookContents() {
      notebookActions.getNotebookContents()
        .then(json => {
          this.cells = json.content.cells.map(c => ({
            ...c,
            hashCode: this.getCellHashCode(c)
          }));
        });
    },
    startSession() {
      notebookActions.startSession()
        .then(json => {
          this.session = json;
        });
    }
  }
};
</script>

<style lang="scss" scoped>
#notebook-container {

  #toolbar {
    position: fixed;
    top: 0;
    width: 100%;
    box-shadow: 0 3px 6px rgba(0,0,0,0.04), 0 3px 6px rgba(0,0,0,0.08);

    background-color: #d9d9d9;

    z-index: 10;
  }

  #cell-list {
    margin-top: 6rem;
  }

}
</style>