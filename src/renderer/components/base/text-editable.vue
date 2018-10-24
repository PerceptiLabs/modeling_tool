<template lang="pug">
  .editable-field(
    @dblclick="openEditMode"
    )
    span.editable-field_title {{ inputText }}
    .editable-field_input-wrap
      input.editable-field_input(type="text"
        v-show="editMode"
        v-model="inputText"
        @blur="closeEditMode"
        @keyup.enter="closeEditMode"
        ref="titleInput"
        )

</template>

<script>
export default {
  name: "TextEditable",
  data() {
    return {
      editMode: false,
      inputText: this.textTitle
    }
  },
  props: {
    textTitle: {
      type: String,
      default: ''
    }
  },
  watch: {
    textTitle(newText) {
      this.inputText = newText;
    }
  },
  methods: {
    openEditMode() {
      this.editMode = true;
      setTimeout( ()=> {
          this.$refs.titleInput.focus()
        }, 100
      )
    },
    closeEditMode() {
      this.editMode = false;
      this.$emit('changeTitle', this.inputText)
    }
  }
}
</script>

<style lang="scss">
  .editable-field {
    cursor: pointer;
    position: relative;
  }
  .editable-field_title {

  }
  .editable-field_input-wrap {
    position: absolute;
    top: 50%;
    left: -.5rem;
    right: -.5rem;
    transform: translateY(-50%);
    input {
      padding: .25rem .5rem;
      height: auto;
      width: 100%;
    }
  }
</style>
