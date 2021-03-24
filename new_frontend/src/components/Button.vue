<template>
  <button
    v-bind="$attrs"
    class="rounded outline-none focus:outline-none p-2 hover:bg-gray-100"
    :class="{
      border: buttonType !== 'icon',
    }"
  >
    <fa-icon :icon="icon" />
    <slot />
  </button>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  props: {
    icon: String,
    buttonType: {
      type: String,
      validator: function(value: string) {
        return ["primary", "secondary", "icon"].includes(value);
      },
      default: "",
    },
  },
});
</script>
