<template lang="pug">
  div
    project-sidebar
    div.project-wrapper
      h3.title.pl-40 /Models
      div.header-controls
        div.left-side
          span.btn-round-icon
            img(src="../../../../static/img/project-page/minus.svg")
          span.btn-round-icon
            img(src="../../../../static/img/project-page/plus.svg")
          div.search-input
            img(src="../../../../static/img/project-page/search-input.svg")
            input(
              type="text"
              placeholder="Search"
              v-bind="searchValue"
            )
        div.right-side
          img.img-button(v-if="isAtLeastOneItemSelected()" @click="toggleFavoriteItems()" src="../../../../static/img/project-page/star.svg")
          img.img-button(v-if="isAtLeastOneItemSelected()" @click="removeItems()" src="../../../../static/img/project-page/remove.svg")
          span.text-button(v-if="isAtLeastOneItemSelected()") Open
          span.text-button(v-if="isAtLeastOneItemSelected()") BlackBox
          span.text-button(v-if="isAtLeastOneItemSelected()") History
          span.text-button(v-if="isAtLeastOneItemSelected()" :class="{'is-disable': isDisabledCompareBtn()}") Compare
          sort-by-button(
            :options="sortOptions"
            :optionSelected="isSelectedSortType"
            @onSelectHandler="onSortByChanged"
          )
      div.models-list
        div.models-list-row.model-list-header
          div.column-1 Name
          div.column-2 Status
          div.column-3 Saved Version
          div.column-4 Session End Time
          div.column-5 Collaborators
          div.column-6 Last Modified
        div.models-list-row.model-list-item(v-for="model in modelList" :key="model.id" :class="{'is-selected': isItemSelected(model.id)}")
          div.column-1
            span.btn-round-icon(@click="toggleItemSelection(model.id)")
              img(v-if="isItemSelected(model.id)" src="../../../../static/img/project-page/checked.svg")
            span {{model.name}}
            svg.is-favorite(v-if="model.isFavorite" width="21" height="19" viewBox="0 0 21 19" fill="none")
              path(d="M9.54894 0.927049C9.8483 0.0057385 11.1517 0.0057404 11.4511 0.927051L13.0819 5.9463C13.2158 6.35833 13.5997 6.63729 14.033 6.63729H19.3105C20.2792 6.63729 20.682 7.8769 19.8983 8.4463L15.6287 11.5484C15.2782 11.803 15.1315 12.2544 15.2654 12.6664L16.8963 17.6857C17.1956 18.607 16.1411 19.3731 15.3574 18.8037L11.0878 15.7016C10.7373 15.447 10.2627 15.447 9.91221 15.7016L5.64258 18.8037C4.85887 19.3731 3.80439 18.607 4.10374 17.6857L5.7346 12.6664C5.86847 12.2544 5.72181 11.803 5.37132 11.5484L1.10169 8.4463C0.317977 7.8769 0.720754 6.63729 1.68948 6.63729H6.96703C7.40026 6.63729 7.78421 6.35833 7.91809 5.9463L9.54894 0.927049Z" fill="#6185EE")
          div.column-2 {{model.status}}
          div.column-3 {{model.savedVersion}}
          div.column-4 {{model.sessionEndTime}}
          div.column-5 Collaborators
          div.column-6 {{model.lastModified.date}}
</template>s

<script>
  import projectSidebar from '@/pages/layout/project-sidebar.vue';
  import SortByButton from '@/pages/projects/components/sort-by-button.vue';
  
  export default {
    name: "pageProjects",
    components: {projectSidebar, SortByButton},
    data: function () {
      return {
        isSelectedSortType: 0,
        searchValue: '',
        sortOptions: [
          {name: 'Name', value: 1},
          {name: 'Date Last Opened', value: 2},
          {name: 'Date Last Modified', value: 3},
          {name: 'Date Created', value: 4},
          {name: 'Size', value: 5},
        ],
        modelList: [
          {id: 1, name:'Placeholder', status: '75%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [], lastModified: { collaboratorId: 1, date: '24/02/20 13:00:00'}, isFavorite: true},
          {id: 2, name:'Placeholder', status: '50%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [], lastModified: { collaboratorId: 1, date: '24/02/20 13:00:00'}, isFavorite: false},
          {id: 3, name:'Placeholder', status: '45%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [], lastModified: { collaboratorId: 1, date: '24/02/20 13:00:00'}, isFavorite: false},
          {id: 4, name:'Placeholder', status: '25%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [], lastModified: { collaboratorId: 1, date: '24/02/20 13:00:00'}, isFavorite: false},
          {id: 5, name:'Placeholder', status: '65%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [], lastModified: { collaboratorId: 1, date: '24/02/20 13:00:00'}, isFavorite: false},
          {id: 6, name:'Placeholder', status: '55%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [], lastModified: { collaboratorId: 1, date: '24/02/20 13:00:00'}, isFavorite: false},
          {id: 7, name:'Placeholder', status: '95%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [], lastModified: { collaboratorId: 1, date: '24/02/20 13:00:00'}, isFavorite: false},
          {id: 8, name:'Placeholder', status: '75%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [], lastModified: { collaboratorId: 1, date: '24/02/20 13:00:00'}, isFavorite: false},
        ],
        selectedListIds: [1],
      }
    },
    methods: {
      onSortByChanged(valueSelected) {
        // logic for sorting
        this.isSelectedSortType = valueSelected;
      },
      isItemSelected(itemId) {
        return this.selectedListIds.indexOf(itemId) !== -1;
      },
      isDisabledCompareBtn() {
        return this.selectedListIds.length < 2;
      },
      toggleItemSelection(modelId) {
        let itmPosition = this.selectedListIds.indexOf(modelId);
        if(itmPosition === -1) {
          this.selectedListIds = [...this.selectedListIds, modelId];
        } else {
          this.selectedListIds = [...this.selectedListIds.slice(0, itmPosition), ...this.selectedListIds.slice(itmPosition+1)]
        }
      },
      isAtLeastOneItemSelected() {
        return this.selectedListIds.length >= 1;
      },
      removeItems() {
        let newModelList = [...this.modelList];
        newModelList = newModelList.filter(item => this.selectedListIds.indexOf(item.id) === -1);
        this.modelList = newModelList;
        this.selectedListIds = [];
      },
      toggleFavoriteItems() {
        
      },
      
    }
  }
</script>

<style lang="scss">
  .project-wrapper {
    margin-left: 40px;
    background-color: #23252A;
    height: 100vh;
  }
  .title {
    padding-top: 14px;
    padding-bottom: 18px;
    margin-bottom: 0;
    font-size: 24px;
    border-bottom: 1px solid #363E51;
  }
  .header-controls {
    padding: 7px 40px;
    border-bottom: 1px solid #363E51;;
    display: flex;
    .left-side {
      display: flex;
    }
    .right-side {
      margin-left: auto;
      display: flex;
    }
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
  .text-button {
    cursor: pointer;
    font-weight: bold;
    background: transparent;
    border-radius: 5px;
    padding: 3px 9px;
    margin: 0 10px;
    font-size: 16px;
    color: #E1E1E1;
    line-height: 23px;
    &.is-disable {
      color: #818181;
    }
    &:hover {
      background: #383F50;
    }
  }
  .img-button {
    cursor: pointer;
    margin: 0 10px 0 25px;
  }
  .btn-round-icon {
    cursor: pointer;
    margin-right: 35px;
    width: 19px;
    height: 19px;
    border: 1px solid #fff;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-self: center;    
  }
  .pl-40 {
    padding-left: 40px;
  }
  
  .models-list-row {
    .column-1 {
      position: relative;
      margin-right: auto;
      padding-left: 135px;
    }
    .column-2 {
      min-width: 130px; 
    }
    .column-3 {
      min-width: 200px;
    }
    .column-4 {
      min-width: 220px;
    }
    .column-5 {
      min-width: 180px;
    }
    .column-6 {
      min-width: 180px;
    }
  }
  .model-list-header {
    display: flex;
    height: 43px;
    font-size: 16px;
    font-weight: bold;
    border-bottom: 1px solid #363E51;
    align-items: center;
  }
  .model-list-item {
    display: flex;
    height: 43px;
    font-size: 16px;
    font-weight: 400;
    border-bottom: 1px solid #363E51;
    align-items: center;
    &.is-selected {
      background: rgba(97, 133, 238, 0.4)
    }
    &:hover {
      background: rgba(97, 133, 238, 0.75);
      box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
      .is-favorite{
        path {
          fill: #E1E1E1;
        }
      }
    }
    
    .column-1 {
      display: flex;
      justify-content: space-between;
      width: 100%;
      .btn-round-icon {
        position: absolute;
        left: 41px;
        top: 50%;
        transform: translateY(-50%)
      }
      .is-favorite {
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
      }
    }
  }
</style>