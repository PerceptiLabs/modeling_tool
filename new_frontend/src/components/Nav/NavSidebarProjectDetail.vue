<template>
  <div class="bottom-0 flex flex-col h-full justify-between sticky text-black">
    <div class="flex flex-col text-left">
      <!-- All projects -->
      <div class="border-b border-gray-200 py-4">
        <router-link
          class="cursor-pointer flex hover:bg-indigo-500 hover:bg-opacity-20 items-center px-0 py-2 w-full"
          :to="{ name: 'ProjectsView' }"
        >
          <img
            src="/svg/arrow-left.svg"
            class="flex-none h-2 w-8"
            alt="to-all-projects"
          />
          <div>All projects</div>
        </router-link>
      </div>

      <!-- Project specific links -->
      <router-link
        class="hover:bg-indigo-500 hover:bg-opacity-20 px-8 py-2 w-full"
        :to="{ name: '' }"
        >Data</router-link
      >
      <router-link
        class="hover:bg-indigo-500 hover:bg-opacity-20 px-8 py-2 w-full"
        :to="{ name: '' }"
        >Test</router-link
      >
      <router-link
        class="hover:bg-indigo-500 hover:bg-opacity-20 px-8 py-2 w-full"
        :to="{ name: '' }"
        >System</router-link
      >
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({});
</script>
