<template>
  <div class="relative flex items-center" :class="containerClass">
    <input
      v-bind="$attrs"
      class="border rounded p-2 leading-4 outline-none focus:border-gray-400 border-gray-300 w-full"
      :class="{
        'pl-9': !!icon,
      }"
      v-model="value"
    />
    <fa-icon :icon="icon" class="absolute mr-2 left-3 items-center" />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

import { useModelWrapper } from "@/utility";

export default defineComponent({
  inheritAttrs: false,

  props: {
    class: String,
    icon: String || Array,
    modelValue: String,
  },

  setup(props, { emit }) {
    return { value: useModelWrapper(props, emit), containerClass: props.class };
  },
});
</script>
