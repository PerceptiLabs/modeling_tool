<template lang="pug">
  div
    project-sidebar
    div(v-show="!isCreateModelModalOpen").project-wrapper
      div.header-controls
        div.left-side
          span(
            @click="openLoadModelPopup()"
            style="margin: 5px 20px 0 0; cursor: pointer"
            )
            img(src="../../../../static/img/project-page/import.svg")
          span.btn-round-icon.btn-rounded-new(@click="handleAddNetworkModal" :class="{'high-lighted': isNewUser}")
            img(src="../../../../static/img/project-page/plus.svg")
            div(v-if="isNewUser").create-first-model Create your first model
          div.search-input
            img(src="../../../../static/img/search-models.svg")
            input(
              type="text"
              placeholder="Search"
              v-model="searchValue"
            )
        div.right-side
          span.img-button.pt-4(v-if="isAtLeastOneItemSelected()" @click="toggleFavoriteItems()")
            svg.fav-icon-action(v-if="!isAllItemSelectedFavorite()" width='22' height='20' viewBox='0 0 22 20' fill='none' xmlns='http://www.w3.org/2000/svg')
              path(d='M10.5245 1.08156C10.6741 0.620903 11.3259 0.620907 11.4755 1.08156L13.2186 6.4463C13.4195 7.06434 13.9954 7.48278 14.6452 7.48278H20.2861C20.7704 7.48278 20.9718 8.10258 20.5799 8.38729L16.0164 11.7029C15.4907 12.0848 15.2707 12.7619 15.4715 13.3799L17.2146 18.7447C17.3643 19.2053 16.8371 19.5884 16.4452 19.3037L11.8817 15.9881C11.3559 15.6061 10.6441 15.6061 10.1183 15.9881L5.5548 19.3037C5.16294 19.5884 4.6357 19.2053 4.78538 18.7447L6.52849 13.3799C6.7293 12.7619 6.50931 12.0848 5.98358 11.7029L1.42006 8.38729C1.0282 8.10259 1.22959 7.48278 1.71395 7.48278H7.35477C8.00461 7.48278 8.58055 7.06434 8.78136 6.4463L10.5245 1.08156Z' stroke='#E1E1E1')

            svg(v-if="isAllItemSelectedFavorite()" width="21" height="19" viewBox="0 0 21 19" fill="none")
              path(d="M9.54894 0.927049C9.8483 0.0057385 11.1517 0.0057404 11.4511 0.927051L13.0819 5.9463C13.2158 6.35833 13.5997 6.63729 14.033 6.63729H19.3105C20.2792 6.63729 20.682 7.8769 19.8983 8.4463L15.6287 11.5484C15.2782 11.803 15.1315 12.2544 15.2654 12.6664L16.8963 17.6857C17.1956 18.607 16.1411 19.3731 15.3574 18.8037L11.0878 15.7016C10.7373 15.447 10.2627 15.447 9.91221 15.7016L5.64258 18.8037C4.85887 19.3731 3.80439 18.607 4.10374 17.6857L5.7346 12.6664C5.86847 12.2544 5.72181 11.803 5.37132 11.5484L1.10169 8.4463C0.317977 7.8769 0.720754 6.63729 1.68948 6.63729H6.96703C7.40026 6.63729 7.78421 6.35833 7.91809 5.9463L9.54894 0.927049Z" fill="#6185EE")
          img.img-button(v-if="isAtLeastOneItemSelected()" @click="removeItems()" src="../../../../static/img/project-page/remove.svg")
          span.text-button(v-if="isAtLeastOneItemSelected()") Open
          //- span.text-button(v-if="isAtLeastOneItemSelected()") BlackBox
          span.text-button.is-disable(v-if="isAtLeastOneItemSelected()") History
          //- span.text-button(v-if="isAtLeastOneItemSelected()" :class="{'is-disable': isDisabledCompareBtn()}") Compare
          //- sort-by-button(
          //-   :options="sortOptions"
          //-   :optionSelected="isSelectedSortType"
          //-   @onSelectHandler="onSortByChanged"
          //- )
      // List
      div.models-list
        div.models-list-row.model-list-header
          div.column-1 
            span.btn-round-icon(@click="toggleSelectedItems()")
              //- img(v-if="isAtLeastOneItemSelected()" src="../../../../static/img/project-page/minus.svg")
              img(v-if="isAtLeastOneItemSelected()" src="../../../../static/img/project-page/checked.svg")
            | Name
          div.column-2 Status
          div.column-3 Saved Version
          div.column-4 Session End Time
          div.column-5 Collaborators
          div.column-6 Last Modified
        div.models-list-row.model-list-item(v-for="(model, index) in workspaceContent"  @click="toggleItemSelection(model.networkID)" :key="model.networkID" :class="{'is-selected': isItemSelected(model.networkID)}")
          div.column-1
            span.btn-round-icon
              img(v-if="isItemSelected(model.networkID)" src="../../../../static/img/project-page/checked.svg")
            span.model-name(v-tooltip:bottom="'Click to view Model Card'" @click.stop="gotToNetworkView(index)") {{model.networkName}}

            svg.is-favorite(v-if="model.isFavorite" @click.stop="setFavoriteValue(index, false)" width="21" height="19" viewBox="0 0 21 19" fill="none")
              path(d="M9.54894 0.927049C9.8483 0.0057385 11.1517 0.0057404 11.4511 0.927051L13.0819 5.9463C13.2158 6.35833 13.5997 6.63729 14.033 6.63729H19.3105C20.2792 6.63729 20.682 7.8769 19.8983 8.4463L15.6287 11.5484C15.2782 11.803 15.1315 12.2544 15.2654 12.6664L16.8963 17.6857C17.1956 18.607 16.1411 19.3731 15.3574 18.8037L11.0878 15.7016C10.7373 15.447 10.2627 15.447 9.91221 15.7016L5.64258 18.8037C4.85887 19.3731 3.80439 18.607 4.10374 17.6857L5.7346 12.6664C5.86847 12.2544 5.72181 11.803 5.37132 11.5484L1.10169 8.4463C0.317977 7.8769 0.720754 6.63729 1.68948 6.63729H6.96703C7.40026 6.63729 7.78421 6.35833 7.91809 5.9463L9.54894 0.927049Z" fill="#6185EE")
            svg.is-not-favorite(v-if="!model.isFavorite" @click.stop="setFavoriteValue(index, true)" width='22' height='20' viewBox='0 0 22 20' fill='none' xmlns='http://www.w3.org/2000/svg')
              path(d='M10.5245 1.08156C10.6741 0.620903 11.3259 0.620907 11.4755 1.08156L13.2186 6.4463C13.4195 7.06434 13.9954 7.48278 14.6452 7.48278H20.2861C20.7704 7.48278 20.9718 8.10258 20.5799 8.38729L16.0164 11.7029C15.4907 12.0848 15.2707 12.7619 15.4715 13.3799L17.2146 18.7447C17.3643 19.2053 16.8371 19.5884 16.4452 19.3037L11.8817 15.9881C11.3559 15.6061 10.6441 15.6061 10.1183 15.9881L5.5548 19.3037C5.16294 19.5884 4.6357 19.2053 4.78538 18.7447L6.52849 13.3799C6.7293 12.7619 6.50931 12.0848 5.98358 11.7029L1.42006 8.38729C1.0282 8.10259 1.22959 7.48278 1.71395 7.48278H7.35477C8.00461 7.48278 8.58055 7.06434 8.78136 6.4463L10.5245 1.08156Z' stroke='#AEAEAE')
          div.column-2
            model-status(
              :statusData="model.networkMeta.coreStatus"
            )
          div.column-3
            span(@click.stop="") -
          div.column-4
            span(@click.stop="") -
          div.column-5
            collaborator-avatar(
                @click.stop=""
                :list="[{id: 1, name: 'Anton', img: null,}, {id: 2, name: 'Robert', img: null,}, {id: 3, name: 'David', img: null,}]"
              )
          div.column-6(@click.stop="")
            collaborator-avatar(
                :list="[{id: 1, name: 'Robert', img: null,}]"
              )
            | {{model.apiMeta.updated.substring(0, 10)}}
        
    file-picker-popup(
      v-if="showFilePickerPopup"
      popupTitle="Load Project Folder"
      :confirmCallback="onLoadNetworkConfirmed"
    )
    select-model-modal(
      v-if="isCreateModelModalOpen"
      @close="onCloseSelectModelModal"
      @onChose="onTemplateChoseSelectModelModal"
      )
    workspace-load-network(
      v-if="showLoadSettingPopup"
    )

</template>

<script>
  import ProjectSidebar from '@/pages/layout/project-sidebar.vue';
  import SortByButton from '@/pages/projects/components/sort-by-button.vue';
  import CollaboratorAvatar from '@/pages/projects/components/collaborator-avatar.vue'
  import FilePicker     from "@/components/different/file-picker.vue";
  import FilePickerPopup        from "@/components/global-popups/file-picker-popup.vue";
  import SelectModelModal from '@/pages/projects/components/select-model-modal.vue';
  import ModelStatus from '@/components/different/model-status.vue';
  import WorkspaceLoadNetwork   from "@/components/global-popups/workspace-load-network.vue";

  import { mapActions, mapMutations, mapState } from 'vuex';
  import {isWeb} from "@/core/helpers";
  import cloneDeep from 'lodash.clonedeep';
  const mockModelList = [
    // {id: 1, dateCreated: new Date().setHours(15), dateLastOpened: new Date(), size: '10', name:'Placeholder 1', status: '75%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [{id: 1, name: 'Anton', img: null,}], lastModified: { user: {id: 1, name: 'Anton', img: null}, date: '19/02/20 13:00:00'}, isFavorite: true},
    // {id: 2, dateCreated: new Date().setHours(3), dateLastOpened: new Date(), size: '12', name:'Placeholder 4', status: '50%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [{id: 2, name: 'Robert', img: null,}], lastModified: { user: {id: 1, name: 'Anton', img: null}, date: '19/02/20 13:00:00'}, isFavorite: false},
    // {id: 3, dateCreated: new Date().setHours(15), dateLastOpened: new Date(), size: '320', name:'Placeholder 3', status: '45%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [{id: 3, name: 'David', img: null,}], lastModified: { user: {id: 1, name: 'Anton', img: null}, date: '19/02/20 13:00:00'}, isFavorite: false},
    // {id: 4, dateCreated: new Date().setHours(8), dateLastOpened: new Date(), size: '30', name:'Placeholder 2', status: '25%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [{id: 1, name: 'Anton', img: null,}, {id: 2, name: 'Robert', img: null,}], lastModified: { user: {id: 1, name: 'Anton', img: null}, date: '19/02/20 13:00:00'}, isFavorite: false},
    // {id: 5, dateCreated: new Date().setHours(4), dateLastOpened: new Date(), size: '205', name:'Placeholder 7', status: '65%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [{id: 1, name: 'Anton', img: null,}, {id: 2, name: 'Robert', img: null,}, {id: 3, name: 'David', img: null,}], lastModified: { user: {id: 1, name: 'Anton', img: null}, date: '19/02/20 13:00:00'}, isFavorite: false},
    // {id: 6, dateCreated: new Date().setHours(23), dateLastOpened: new Date(), size: '85', name:'Placeholder 6', status: '55%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [{id: 1, name: 'Anton', img: null,}, {id: 2, name: 'Robert', img: null,}, {id: 3, name: 'David', img: null,}], lastModified: { user: {id: 1, name: 'Anton', img: null}, date: '19/02/20 13:00:00'}, isFavorite: false},
    // {id: 7, dateCreated: new Date().setHours(6), dateLastOpened: new Date(), size: '120', name:'Placeholder 5', status: '95%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [{id: 1, name: 'Anton', img: null,}, {id: 2, name: 'Robert', img: null,}, {id: 3, name: 'David', img: null,}], lastModified: { user: {id: 1, name: 'Anton', img: null}, date: '19/02/20 13:00:00'}, isFavorite: false},
    // {id: 8, dateCreated: new Date().setHours(12), dateLastOpened: new Date(), size: '80', name:'Placeholder 8', status: '75%', savedVersion: '-', sessionEndTime: 'Placeholder', collaborators: [{id: 1, name: 'Anton', img: null,}, {id: 2, name: 'Robert', img: null,}, {id: 3, name: 'David', img: null,}], lastModified: { user: {id: 1, name: 'Anton', img: null}, date: '19/02/20 13:00:00'}, isFavorite: false},
  ];
  

  export default {
    name: "pageProjects",
    components: {
      ProjectSidebar,
      SortByButton,
      CollaboratorAvatar,
      FilePicker,
      FilePickerPopup,
      SelectModelModal,
      ModelStatus,
      WorkspaceLoadNetwork,
    },
    data: function () {
      return {
        isSelectedSortType: 0,
        searchValue: '',
        isNewUser: false,
        sortOptions: [
          {name: 'Name', value: 1},
          {name: 'Date Last Opened', value: 2},
          {name: 'Date Last Modified', value: 3},
          {name: 'Date Created', value: 4},
          {name: 'Size', value: 5},
        ],
        initialModelList: mockModelList,
        modelList: mockModelList,
        selectedListIds: [],
        isImportModelsOpen: false,
        isCreateModelModalOpen: false,
      }
    },                                                     
    watch: {
      searchValue: function (newValue) {
        console.log({newValue})
        let initialModelList = [...this.initialModelList];
        initialModelList = initialModelList.filter(model => model.name.toLocaleLowerCase().indexOf(newValue.toLowerCase()) !== -1);
        let initialModelListIds = initialModelList.map(model => model.id);
        this.selectedListIds = this.selectedListIds.filter(id => initialModelListIds.indexOf(id) !== -1);
        
        this.modelList = initialModelList;
        this.onSortByChanged(this.isSelectedSortType);
      }
    },
    created() {
      // this.setPageTitleMutation('Project Name / Models');
      if(isWeb()) {
        // this.$store.dispatch('mod_workspace/GET_workspacesFromLocalStorage');
      }
    },
    beforeDestroy() {
      // this.setPageTitleMutation('')
    },
  
    computed: {
      ...mapState({
        currentProjectId: state => state.mod_project.currentProject,
        showFilePickerPopup: state => state.globalView.globalPopup.showFilePickerPopup,
        appVersion:           state => state.globalView.appVersion,
        hotKeyPressDelete:    state => state.mod_events.globalPressKey.del,
        showLoadSettingPopup: state => state.globalView.globalPopup.showLoadSettingPopup,
      }),
      workspaceContent() {
        return this.$store.state.mod_workspace.workspaceContent;
      },
      filteredProjects() {
        this.selectedProject = null;
        return this.projects.filter((project)=> project.name.match(this.search))
      }
    },
    watch: {     
      'localUserInfo.projectsList.length': {
        handler() {
          if(!this.localUserInfo) return;

          let localProjectsList = deepCopy(this.localUserInfo.projectsList);
          if (Array.isArray(localProjectsList)) {
            localProjectsList.forEach((el) => {
              el.notExist = false;
              el.isChecked = false;

              this.$store.dispatch('mod_api/API_loadNetwork', el.pathProject, {root: true})
                .then((net) => {
                  try {
                    if(!(net.networkName
                      && net.networkMeta
                      && net.networkElementList)) {
                        throw('err');
                      }
                  } catch(e) {
                    throw('err');
                  }
                }).catch(err => {
                  el.notExist = true
                })
            });
            this.projects = localProjectsList;
          }
        },
        immediate: true
      },
      hotKeyPressDelete() {
        const indexCheckedProj = this.projects.findIndex((el)=> el.isChecked === true);
        if(indexCheckedProj < 0) return;

        const selectedProject = this.projects[indexCheckedProj];
        //const isProjectNotExist = selectedProject.notExist;
        const pathDelete = selectedProject.pathProject;

        const newProjectsList = deepCopy(this.localUserInfo.projectsList);
        newProjectsList.splice(indexCheckedProj, 1);
        this.saveLocalUserInfo({key: 'projectsList', data: newProjectsList });

        // folderPCDelete(pathDelete)
        //   .then(()=> {
        //     const newProjectsList = deepCopy(this.localUserInfo.projectsList);
        //     newProjectsList.splice(indexCheckedProj, 1);
        //     this.saveLocalUserInfo({key: 'projectsList', data: newProjectsList });
        //     this.$nextTick(()=> this.showInfoPopup("The project has been successfully deleted"))
        //   })
        //   .catch ((err)=> {console.error(err)})
      }
    },
    methods: {
      ...mapActions({
        loadNetwork:        'mod_api/API_loadNetwork',
        addNetwork:         'mod_workspace/ADD_network',
        set_currentNetwork: 'mod_workspace/SET_currentNetwork',
        createProjectModel: 'mod_project/createProjectModel',
        API_getModel:       'mod_api/API_getModel',
        setActivePageAction: 'modal_pages/setActivePageAction',
        delete_network : 'mod_workspace/DELETE_network',
        UPDATE_MODE_ACTION : 'mod_workspace/UPDATE_MODE_ACTION',
      }),
      ...mapMutations({
        // setPageTitleMutation: 'globalView/setPageTitleMutation'
      }),
      gotToNetworkView(index) {
        // maybe should receive a id and search index by it
        this.set_currentNetwork(index);
        this.$router.push({name: 'app'});
      },
      loadFolderPath() {
        this.$store.commit("globalView/set_filePickerPopup", true);
      },
      openTemplate(path) {
        this.loadNetwork(path)
      },
      onSortByChanged(valueSelected) {
        let modelList = [...this.modelList];
        switch (valueSelected) {
          case 1: {
            modelList = modelList.sort((a, b) => a.name.localeCompare(b.name));
            break;
          }
          case 2: {
            modelList = modelList.sort((a, b) => b.dateLastOpened - a.dateLastOpened);
            break;
          }
          case 3: {
            modelList = modelList.sort((a, b) => b.lastModified.date - a.lastModified.date);
            break;
          }
          case 4: {
            modelList = modelList.sort((a, b) => b.dateCreated - a.dateCreated);
            break;
          }
          case 5: {
            modelList = modelList.sort((a, b) => parseInt(a.size, 10) - parseInt(b.size, 10));
            break;
          }
        }
        this.modelList = modelList;
        this.isSelectedSortType = valueSelected;
      },
      isItemSelected(itemId) {
        itemId = parseInt(itemId);
        return this.selectedListIds.indexOf(itemId) !== -1;
      },
      isDisabledCompareBtn() {
        return this.selectedListIds.length < 2;
      },
      openBasicTemplate(net) {
        this.addNetwork(cloneDeep(net.network));
      },
      toggleItemSelection(modelId) {
        modelId = parseInt(modelId);
        let itmPosition = this.selectedListIds.indexOf(modelId);
        if (itmPosition === -1) {
          this.selectedListIds = [...this.selectedListIds, modelId];
        } else {
          this.selectedListIds = [...this.selectedListIds.slice(0, itmPosition), ...this.selectedListIds.slice(itmPosition + 1)]
        }
      },
      isAtLeastOneItemSelected() {
        return this.selectedListIds.length >= 1;
      },
      removeItems() {
        let removeIndexes = [];
        this.workspaceContent.map((network, index) =>  {
          if(this.selectedListIds.indexOf(parseInt(network.networkID)) !== -1) {
            removeIndexes.push(index);
          }
        })
        removeIndexes.sort((a, b) => (b - a));

        removeIndexes.map((index) => {
          this.delete_network(index);
        })
        // get index
        // this.delete_network(index);
        // let modelList = [...this.modelList];
        // let initialModelList = [...this.initialModelList];

        // modelList = modelList.filter(item => this.selectedListIds.indexOf(item.id) === -1);
        // initialModelList = initialModelList.filter(item => this.selectedListIds.indexOf(item.id) === -1);

        // this.modelList = modelList;
        // this.initialModelList = initialModelList;

        // this.selectedListIds = [];
      },
      toggleFavoriteItems() {
        let newModelList = [...this.workspaceContent];
        if (this.isAllItemSelectedFavorite()) {
          newModelList = newModelList.map((item, index) => {
            if (this.selectedListIds.indexOf(parseInt(item.networkID, 10)) !== -1) {
              this.setFavoriteValue(index, false);
            }
            return item;
          })
        } else {
          newModelList = newModelList.map((item, index) => {
            if (this.selectedListIds.indexOf(parseInt(item.networkID, 10)) !== -1) {
             this.setFavoriteValue(index, true);
            }
            return item;
          })
        }

        this.modelList = newModelList;
        this.updateInitialModelListData();
      },
      setFavoriteValue(index, value) {
        // let setIndex = [];
        // this.workspaceContent = this.workspaceContent.map((network, index) =>  {
          
        // })

        this.UPDATE_MODE_ACTION({index, field: 'isFavorite', value});

        // removeIndexes.map((index) => {
        // })
        // udate model fild value


        // let newModelList = [...this.modelList];
        // newModelList = newModelList.map(item => {
        //   if (item.id === itemId) {
        //     item.isFavorite = value;
        //   }
        //   return item;
        // })

      },
      isAllItemSelectedFavorite() {

        const selectedLength = this.selectedListIds.length;
        if (selectedLength === 0) return false;
        let newModelList = [...this.workspaceContent];
        let favoriteItemLength = newModelList.filter(item => this.selectedListIds.indexOf(parseInt(item.networkID, 10)) !== -1 && item.isFavorite);
        return selectedLength === favoriteItemLength.length
      },
      toggleSelectedItems() {
        if (this.isAtLeastOneItemSelected()) {
          this.selectedListIds = [];
        } else {
          let newWorkspaceContent = [...this.workspaceContent];
          this.selectedListIds = newWorkspaceContent.map(networkItem => parseInt(networkItem.networkID, 10));
        }
      },
      updateInitialModelListData() {
        let modelList = [...this.modelList];
        let initialModelList = [...this.initialModelList];
        let initialModelListIds = initialModelList.map(itm => itm.id);
        modelList.map(modelItem => {
          const initialModelListPosition = initialModelListIds.indexOf(modelItem.id);
          initialModelList[initialModelListPosition] = modelItem;
        });
        this.initialModelList = initialModelList;

      },
      handleAddNetwork() {
        this.createProjectModel({
          name: 'New_Model',
          project: this.currentProjectId,
        }).then(apiMeta => {
          this.addNetwork({apiMeta});
          //@todo save the network in project folder
          
        });
      },
      handleAddNetworkModal() {
        // open modal
        this.isCreateModelModalOpen = true;
      },
      onCloseSelectModelModal() {
        this.isCreateModelModalOpen = false;
      },
      onTemplateChoseSelectModelModal() {

      },
      confirmFilePickerSelection(selectedItems) {
        console.log(selectedItems);
        this.clearPath();
      },
      clearPath(x){
        this.isImportModelsOpen = false;
        console.log(x);
      },
      openLoadModelPopup() {
        this.$store.dispatch('globalView/SET_filePickerPopup', {confirmCallback: this.onLoadNetworkConfirmed});
      },
      onLoadNetworkConfirmed(path) {
        if (!path || path.length === 0) { return; }
        this.$store.dispatch('globalView/SET_filePickerPopup', false);
        this.API_getModel(`${path[0]}/model.json`)
          .then(model => {

            if(model.hasOwnProperty('apiMeta')) {
              delete model.apiMeta;
            }
            this.createProjectModel({
              name: model.networkName,
              project: this.currentProjectId,
            }).then(apiMeta => {
              this.addNetwork({network: model, apiMeta});
            });
          })
          .catch(e => console.log(e));
      },
      confirmCallback(el) {
        this.openTemplate(el[0]);
        this.$store.commit("globalView/HIDE_allGlobalPopups");
      },
    }
  }
</script>

<style lang="scss" scoped>
  * {
    font-family: "Nunito Sans";
  }
  .project-wrapper {
    margin-left: 46px;
    background-color: #23252A;
    height: 100vh;
    background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
    border: 1px solid rgba(97, 133, 238, 0.4);
    box-sizing: border-box;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
    padding-left: 10px;
    padding-right: 19px;
  }
  .header-controls {
    padding: 7px 40px;
    border-bottom: 1px solid #464D5F;;
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
      border: 1px solid #4D556A;
      border-radius: 2px;
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
    &.high-lighted {
      position: relative;
      box-shadow: 0 0 10px #FFFFFF;
    }
  }
  .btn-rounded-new {
    border-radius: 2px;
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
      min-width: 200px; 
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
    .column-1 {
      .btn-round-icon {
        position: absolute;
        left: 41px;
        top: 50%;
        transform: translateY(-50%)
      }
    }
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
        cursor: pointer;
        position: absolute;
        left: 80px;
        top: 50%;
        transform: translateY(-50%);
      }
      .is-not-favorite {
        cursor: pointer;
        // opacity: 0;
        position: absolute;
        left: 80px;
        top: 50%;
        transform: translateY(-50%);
        transition: 0.1s;
        // &:hover {
        //   opacity: 1;
        // }
      }
      .model-name {
        cursor: pointer;
      }
    }
    .column-6 {
      display: flex;
      .collaboratorWrapper {
        width: 30px;
      }
    }
  }
  .fav-icon-action {
    &:hover {
      path {
        stroke: #6185EE;
        stroke-width: 2px;
        border-radius: 1px;
      }
    }
  }
  .pt-4 {
    padding-top: 4px;
  }
  .create-first-model {
    z-index: 10;
    top: 31px;
    position: absolute;
    background: #6185EE;
    border-radius: 2px;
    font-size: 16px;
    line-height: 21px;
    width: 188px;
    text-align: center;
    padding-top: 11px;
    padding-bottom: 13px;
    &:after {
      content: "";
      top: -8px;
      left: 50%;
      transform: translateX(-50%);
      position: absolute;
      border-bottom: 9px solid #6185EE;
      border-left: 6px solid transparent;
      border-right: 6px solid transparent;
    }
  }
  .file-picker-wrapper {
    position: absolute;
    z-index: 1234;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: black;
    border-radius: 9px;
    border-radius: 0.5rem;
    background-color: #4D556A;
    min-width: 29rem;
    box-shadow: 0 0 6px rgba(0, 0, 0, 0.7);
  }
</style>