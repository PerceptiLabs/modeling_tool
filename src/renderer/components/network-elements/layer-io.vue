<template lang="pug">
  .layer
    button.btn.btn--layersbar.layer_parent(type="button"
      @click="toggleChild"
      )
      i.icon.icon-data-toggle
    ul.layer_child-list(
      :class="{'open': openChild}"
    )
      li(
        v-for="(layer, i) in child"
        :key="i"
      )
        button.btn.btn--layersbar(type="button")
          i.icon(:class="layer.iconClass")

</template>

<script>
export default {
  name: 'LayerIo',
  data() {
    return {
      openChild: false,
      child: [
        {
          name: 'Input',
          iconClass: 'icon-data-in'
        },
        {
          name: 'Output',
          iconClass: 'icon-data-out'
        }
      ]
    }
  },
  methods: {
    toggleChild() {
      this.openChild = !this.openChild;
    }
  }
}
</script>

<style lang="scss" scoped>
  .layer_parent {
    background: linear-gradient(#8394C5 , #66708B);
  }
  .layer_child-list .btn {
    background: linear-gradient(#D3DFFE, #A1A9BF);
  }
</style>
