<template lang="pug">
  main.page_workspace
    .workspace_tabset(
      ref="tabset"
      v-show="!showTrainingSpinner"
    )
      include ./tabset/workspace-tabset.pug
    
    component(:is="toolbarType")

    .workspace_content.bookmark_content.js-workspace(
      v-show="!isNotebookMode"  
      ref="workspaceNet"
      :class="{'workspace-relative' : showTrainingSpinner}"
      )
      .network(
        v-if="indexCurrentNetwork === i"
        v-for="(net, i) in workspace"
        :key="net.networkID"
        :class="networkClass"
      )
        the-testing.the-testing(v-if="testIsOpen")
        //-the-statistics.the-statistics(
          v-if="statisticsIsOpen || testIsOpen"
          /:el-data="statisticsElSelected.statistics"
          )
        the-view-box#tutorial_statistics.the-statistics(
          v-if="statisticsIsOpen || testIsOpen"
          :el-data="statisticsElSelected.statistics"
          section-title="Statistics"
        )
        the-view-box#tutorial_view-box.the-view-box(
          v-if="statisticsIsOpen  || testIsOpen"
          :el-data="statisticsElSelected.viewBox"
          section-title="ViewBox"
          )
        section.network_info-section.the-network-field(
          ref="networkWindow"
          )
          .info-section_head(v-if="statisticsIsOpen || testIsOpen")
            h3 Map
          perfect-scrollbar.info-section_main.js-info-section_main(
            @wheel="scaleScroll($event)"
            )
            network-field(
              ref="networkField"
              :key="i"
              :scaleNet="scaleNet"
            )
            // when select more then 2 network item its display
            div(:style="dragBoxHorizontalTopBorder()")
            div(:style="dragBoxHorizontalBottomBorder()")
            div(:style="dragBoxVerticalLeftBorder()")
            div(:style="dragBoxVerticalRightBorder()")

          sidebar-layers.layers-sidebar
        //-general-settings(v-if="showGlobalSet")
        general-result(v-if="showGlobalResult")
        select-core-side(v-if="showCoreSide")
        workspace-before-import(v-if="showWorkspaceBeforeImport")
        workspace-load-network(
          v-if="showLoadSettingPopup" 
        )

      start-training-spinner(v-if="showTrainingSpinner")

    .workspace_meta(
      v-if="!isNotebookMode"  
      )
      include ./meta/workspace-meta.pug
    notebook(v-if="isNotebookMode")

    workspace-save-network(
      v-if="showSaveNetworkPopup"
      ref="saveNetworkPopup"
      :popup-settings="saveNetworkPopup"
      )
    export-network(v-if="showExportNetworkPopup")
    file-picker-popup(
      v-if="showFilePickerPopup"
      :filePickerType="showFilePickerPopup.filePickerType"
      :fileTypeFilter="showFilePickerPopup.fileTypeFilter"
      :popupTitle="showFilePickerPopup.popupTitle"
      :confirmCallback="showFilePickerPopup.confirmCallback || showFilePickerPopup")
      //- showFilePickerPopup container the callback function

    .select-modal-wrapper(
      v-if="showNewModelPopup"
      )
      select-model-modal(
        class="select-model-modal"
        v-if="showNewModelPopup"
        @close="onCloseSelectModelModal"
        )

</template>

<script src="./the-workspace.js"></script>

<style lang="scss" scoped>
  @import "../../scss/base";
  @import "./tabset/workspace-tabset";
  @import "./meta/workspace-meta";
  .select-modal-wrapper {
    position: absolute;
    width: calc(100% - 50px);
    height: calc(100% - 40px);
    background: rgba(33, 40, 57, 0.9);
    z-index: 99;
  }
  .select-model-modal {
    z-index: 100;
  }
  .page_workspace {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    width: 100%;
    height: 100%;
  }
  .workspace_tabset {
    flex: 0 0 auto;
    padding-top: 0.5rem;
    display: flex;
    justify-content: flex-start;
    align-items: flex-end;
    background-color: $bg-workspace;
    border-bottom: 1px solid $toolbar-separator-color;

    .tab-group {
      display: flex;
      margin-right: 10px;
    }
  }
  .workspace_content {
    display: flex;
    flex: 1 1 100%;
    overflow: hidden;
  }
  .network {
    width: 100%;
    display: grid;
    grid-template-areas:  'network-field   network-field'
                          'network-field    network-field';
    grid-template-rows: 1fr 1fr;
    grid-template-columns: 1fr 1fr;
    &.open-statistic {
      grid-template-areas:  'the-statistics   the-statistics'
                            'network-field  view-box';
    }
    &.open-test {
      grid-template-rows: auto 1fr 1fr;
      grid-template-columns: 1fr 1fr;
      grid-template-areas:  'the-testing   the-testing'
                            'view-box   the-statistics'
                            'network-field  network-field';

    }
  }
  .network--show-code {
    transform: translate(0);
  }
  .the-statistics {
    grid-area: the-statistics;
  }
  .the-view-box {
    grid-area: view-box;
  }
  .the-testing {
    grid-area: the-testing;
  }
  .the-network-field {
    grid-area: network-field;
    background: linear-gradient(180deg, #363E51 0%, rgba(54, 62, 81, 0) 100%);
    border: 1px solid rgba(97, 133, 238, 0.4);
  }
  .layers-sidebar {
    position: fixed;
    right: 2rem;
    transform: translateY(2rem);
  }

  .network_info-section {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: $bg-workspace-3;

    > .info-section_head {
      background: #090f19;
    }
  }
  .info-section_main {
    display: block;
    overflow: auto;
  }
  .workspace_meta {
    position: relative; //for minimap
    flex: 0 0 auto;
    background-color: #23252A;
    
    display: flex;
    justify-content: space-between;
    padding: .5rem;
  }
  .workspace-relative {
    position: relative;
  }
</style>
