<template>
  <nav
    class="bg-gray-100 border-b border-gray-300 flex h-auto items-center justify-between px-4 py-2 sticky top-0 w-full"
  >
    <div>
      <router-link class="cursor-pointer" :to="{ name: 'ProjectsView' }">
        <img
          src="/svg/perceptilabs-logo-and-name.svg"
          class="h-8"
          alt="perceptilabs-logo"
        />
      </router-link>
    </div>
    <div class="flex">
      <img src="/svg/magnifying-glass.svg" class="h-6 ml-6" alt="search" />
      <img src="/svg/question-mark.svg" class="h-6 ml-6" alt="help" />
      <div
        class="bg-red-500 font-bold h-6 rounded-full ml-6 text-center text-white w-6"
      >
        {{ firstNameInitial }}
      </div>
    </div>
  </nav>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";

export default defineComponent({
  setup() {
    const firstNameInitial = ref<string>("A");

    return { firstNameInitial };
  },
});
</script>
