<template lang="pug">
  .collaboratorWrapper
    .collaboratorItem(
      @click.stop=""
      v-for="(collaborator, index) in list"
      :style="generateCollaboratorItemStyle(index)"
      ) {{collaborator.name[0]}}
</template>

<script>
  
  export default {
    name: 'collaborator-avatar',
    props: {
      list: {
        type: Array,
        default: [],
      },
      haveBorder: {
        type: Boolean,
        default: false,
      }
    },
    methods: {
      generateCollaboratorItemStyle(ix) {
        let colorIndex = ix + 4;
        const totalCollaborators = this.list.length;
        return {
          border: this.haveBorder ? '4px solid #23252A': 'none',
          left: `${(ix) * 13}px`,
          zIndex: totalCollaborators - ix,
          backgroundColor: `#${colorIndex + (colorIndex*10) + (colorIndex*100)}`
        };
      }
    }
  }
</script>

<style lang="scss" scoped>
  .collaboratorWrapper {
    position: relative;
    width: 100%;
    box-sizing: content-box;
  }
  .collaboratorItem {
    position: absolute;
    display: inline-block;
    top: 50%;
    transform: translateY(-50%);
    width: 25px;
    height: 25px;
    border-radius: 50%;
    text-align: center;
    line-height: 25px;
    text-transform: uppercase;
  }
</style>