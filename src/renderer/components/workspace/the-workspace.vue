<template lang="pug">
  main.page_workspace
    .workspace_tabset
      include ./tabset/workspace-tabset.pug
    .workspace
      .workspace_content(v-bar)
        div
          .network-field(
            v-for="(net, i) in workspace"
            :key="i"
            v-if="currentNetwork == i"
            :style="'transform: scale(' + styleScale + ')'"
            )
            component(
              v-for="(el, index) in net.network"
              :key="index"
              :is="el.componentName"
              :elementData="{el, index}"
              )

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
    flex: 1 1 100%;
    overflow: scroll;
  }
  .network-field {
    height: 100%;
  }
  .workspace_meta {
    flex: 0 0 auto;
    background-color: $bg-workspace-2;
    display: flex;
    justify-content: space-between;
    padding: .5rem;
  }
</style>
