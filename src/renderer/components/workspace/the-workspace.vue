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
              :data="{el, index}"
              )

      .workspace_meta
        .workspace_scale
          button.btn.btn--icon(type="button" @click="decScale()") -

          .scale-input
            input(type="text" v-model.number="scale")
            span %

          button.btn.btn--icon(type="button" @click="incScale()") +

          base-checkbox Map



</template>

<script src="./the-workspace.js"></script>

<style lang="scss" scoped>
  @import "../../scss/base";
  @import "./tabset/workspace-tabset";
  .workspace {
    display: flex;
    flex-direction: column;
    flex: 1 1 100%;
  }
  .workspace_tabset {
    padding-top: 2px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }
  .workspace_content {
    background-color: $bg-workspace;
    flex: 1 1 100%;
    overflow: scroll;
  }
  .workspace_meta {
    flex: 0 0 auto;
    background-color: $bg-workspace-2;
    display: flex;
    justify-content: space-between;
  }
  .workspace_scale {
    display: flex;
    align-items: center;
  }
  .scale-input {
    position: relative;
    input {
      padding-right: 1em;
      width: 50px;
    }
    span {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      right: .5em;

    }
  }
  .network-field {
    height: 100%;
  }
</style>
