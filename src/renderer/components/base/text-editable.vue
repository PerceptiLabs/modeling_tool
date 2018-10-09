<template lang="pug">
  .editable-field(
    @dblclick="openEditMode"
    )
    span.editable-field_title(
      v-show="!editMode"
      ) {{ inputText }}
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

<style lang="scss" scoped>
  .editable-field {
    cursor: pointer;
  }
  .editable-field_title {

  }
  .editable-field_input {

  }
</style>
