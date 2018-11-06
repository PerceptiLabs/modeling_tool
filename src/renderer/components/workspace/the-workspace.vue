<template lang="pug">
  main.page_workspace
    .workspace_tabset
      include ./tabset/workspace-tabset.pug
    .workspace
      .workspace_content
        .network(
          v-if="currentNetwork === i"
          v-for="(net, i) in workspace"
          :key="net.i"
          :class="{'open-statistic': showStatistics}"
        )
          section.network_info-section(v-if="showStatistics")
            .info-section_head
              h3 Statistics
            .info-section_main
              statistics-out-normal
          section.network_info-section(v-if="showStatistics")
            .info-section_head
              h3 ViewBox
            .info-section_main
              view-box-learn-deep-connect
          section.network_info-section
            .info-section_head(v-if="showStatistics")
              h3 Map
            .info-section_main
              network-field(
              :netIndex="i"
              )
            //chart-bar(:chartData="optionBar")
              chart-line(:chartData="optionLine")
              chart-3d(:chartData="option3d")



        general-settings(v-if="showGlobalSet")
        general-result(v-if="showGlobalResult")
        select-core-side(v-if="showCoreSide")

      .workspace_meta
        include ./meta/workspace-meta.pug



</template>

<script src="./the-workspace.js"></script>

<style lang="scss" scoped>
  @import "../../scss/base";
  @import "./tabset/workspace-tabset";
  @import "./meta/workspace-meta";
  .workspace {
    display: flex;
    flex-direction: column;
    flex: 1 1 100%;
  }
  .workspace_tabset {
    padding-top: 1px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    //height: $h-sidebar-layers-item;
  }
  .workspace_content {
    background-color: $bg-workspace;
    display: flex;
    flex: 1 1 100%;
  }
  .network {
    display: flex;
    //flex-direction: row-reverse;
    flex: 1 1 100%;
    flex-wrap: wrap;
    &.open-statistic {
      .network_info-section {
        flex: 1 1 50%;
        height: 50%;
        &:first-child {
          flex: 0 0 100%;
        }
        &:nth-child(2n) {
          order: 1;
        }
      }
    }
  }
  .network_info-section {
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  /*canvas {*/
    /*position: absolute;*/
    /*left: 0;*/
    /*right: 0;*/
    /*bottom: 0;*/
    /*top: 0;*/
    /*background-color: #040;*/
    /*width: 100%;*/
    /*height: 100%;*/
  /*}*/
  .workspace_meta {
    flex: 0 0 auto;
    background-color: $bg-workspace-2;
    display: flex;
    justify-content: space-between;
    padding: .5rem;
  }
  .info-section {
    width: 100%;
    flex: 1 1 50%;
    display: flex;
    flex-direction: column;
  }
  .info-section_head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: $bg-toolbar;
    padding: .7rem 1rem;
    flex: 0 0 auto;
  }
  .info-section_title {
    h3 {
      margin: 0;
    }
  }
  .info-section_meta {}
  .info-section_main {
    flex: 1 1 100%;
    display: flex;
  }
  .info-section_tab-set {
    flex: 1 1 100%;
    display: flex;
  }
</style>
