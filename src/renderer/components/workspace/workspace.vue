<template lang="pug">
  .workspace
    .workspace_content(v-bar)
      .content(:style="'transform: scale(' + styleScale + ')'")
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
        p Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aut eos, id libero nesciunt quaerat quas quidem. Aspernatur fugiat illo impedit, iure maxime nostrum nulla placeat quae recusandae repellendus saepe suscipit?
    .workspace_meta
      .workspace_scale
        button.btn.btn--icon(type="button" @click="decScale()") -

        .scale-input
          input(type="text" v-model.number="scale")
          span %

        button.btn.btn--icon(type="button" @click="incScale()") +

        base-checkbox Map



</template>

<script>
export default {
  name: 'WorkspaceContent',
  data () {
    return {
      scale: 100
    }
  },
  computed: {
    styleScale() {
      return this.scale / 100
    }
  },
  methods: {
    decScale () {
      if (this.scale < 10) {
        this.scale = 5
      }
      else this.scale = this.scale - 10
    },
    incScale () {
      if (this.scale > 90) {
        this.scale = 100
      }
      else this.scale = this.scale + 10
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "../../scss/base";
  .workspace {
    display: flex;
    flex-direction: column;
    flex: 1 1 100%;
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
</style>
