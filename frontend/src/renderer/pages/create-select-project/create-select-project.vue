<template lang="pug">
  .project-wrapper
    .project-box
      .header Projects
      .content
        .sidebar
          button.create-new-button
            img(src="../../../../static/img/plus.svg")
            span  create new
          button.project-list-filter-button.is-active All Projects
          button.project-list-filter-button My Projects
          button.project-list-filter-button Shared with me
        .main
          .main-header
            div.search-input
              img(src="../../../../static/img/search-input.svg")
              input(
                type="text"
                placeholder="Search"
                v-model="searchValue"
              )
            div
              sort-by-button(
                :options="[{name: 'Test', value: 1}]"
                :option-selected="0"
              )
          .main-list
            .main-list-header
              .list-name-name Name
              .list-last-opened Last Opened
            div.main-list-item(v-for="mock in [0,1,2,3]")
              span.main-list-name.fz-16 Placeholder {{mock}}
              span.main-list-date.fz-16 Yesterday
          
  
</template>
<script>
  import { mapActions } from "vuex";
  import SortByButton from "@/components/sort-by-button";

  export default {
    name: 'CreateSelectProject',
    components: {SortByButton},
    data: function() {
      return {
        searchValue: ''
      }
    },
    created() {
      // this.setActivePageAction()
    },
    computed:{
      isOpen() {
        return this.$store.state.modal_pages.isOpen
      },
      currentPage() {
        return this.$store.state.modal_pages.currentPage
      }
    },
    methods: {
      ...mapActions({
        setActivePageAction: 'modal_pages/setActivePageAction',
        closePageAction: 'modal_pages/closePageAction',
      })
    }
  }

</script>
<style lang="scss" scoped>
  .project-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
  }
  .project-box {
    min-width: 680px;
    min-height: 500px;
    background: #1C1C1E;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
    border-radius: 2px;
  }
  .header {
    background: #363E50;
    border-radius: 2px 2px 0 0;
    height: 38px;
    width: 687px;
    font-size: 14px;
    line-height: 38px;
    text-align: center;
  }
  .content {
    display: flex;
    padding: 23px 0;
  }
  /* Sidebar */
  .sidebar {
    width: 30%;
    padding-left: 29px;
    margin-right: 30px;
  }
  .create-new-button {
    margin-bottom: 30px;
    font-size: 16px;
    background: #1C1C1E;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
    border: 1px solid #E1E1E1;
    border-radius: 2px;
    line-height: 29px;
    width: 100%;
    img {
      margin-right: 7px;
    }
  }
  .project-list-filter-button {
    padding-left: 15px;
    display: block;
    background-color: transparent;
    border-left: 3px solid transparent;
    font-size: 16px;
    height: 29px;
    margin-bottom: 16px;
    &.is-active {
      border-left: 3px solid #fff;
     }
  }
  /* main */
  .main {
    width: 70%;
  }
  .main-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
  }
  .search-input {
    position: relative;
    width: 333px;
    img {
      cursor: pointer;
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      left: 10px;
    }
    input {
      padding-left: 44px;
      background-color: transparent;
      border: 1px solid #363E51;
      border-radius: 5px;
      height: 29px;
    }
  }
  
  .main-list-header {
    display: flex;
    justify-content: space-between;
    padding: 14px 30px 14px 10px;
    border-top: 1px solid #363E51;
    border-bottom: 1px solid #363E51;
  }
  .list-name-name {
    font-size: 16px;
    color: #818181;
    font-weight: bold;
  }
  .list-last-opened {
    font-size: 16px;
    color: #fff;
    font-weight: bold;
  }
  .main-list-item {
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    padding: 14px 30px 14px 10px;
    border-bottom: 1px solid #363E51;
  }
  .fz-16 {
    font-size: 16px;
  }
</style>