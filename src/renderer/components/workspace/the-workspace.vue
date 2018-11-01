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
          :class="{'open-statistic': appMode !== 'edit'}"
        )
          .network_info-section.network-statistics(v-if="appMode !== 'edit'")
            p statistics
          .network_info-section.network-statistics(v-if="appMode !== 'edit'")
            p statistics
          .network_info-section
            network-field(
              :netIndex="i"
              )
          .network_info-section.network-viewbox(v-if="appMode !== 'edit'")
            p network viewbox
        general-settings(v-if="showGlobalSet")
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
    flex: 1 1 100%;
    flex-wrap: wrap;
    &.open-statistic {
      .network_info-section {
        border: 1px solid #fff;
      }
    }
  }
  .network_info-section {
    display: flex;
    flex: 1 1 50%;
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
</style>
