<template>
  <div class="px-12 py-10">
    <div class="flex mb-8 items-center">
      <h1 class="font-medium text-xl mr-3">All Projects</h1>
      <Button button-type="icon" icon="plus" />
    </div>

    <div class="flex mb-8">
      <v-select
        :options="filterOptions"
        v-model="filterOption"
        :close-on-select="true"
        placeholder="Filter by"
      ></v-select>

      <Input
        class="ml-3 w-full md:w-80"
        v-model="searchString"
        icon="search"
        placeholder="Search for a project"
      />
    </div>

    <div class="-m-4">
      <projects-list />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

import { Input, Button } from "@/components";

import ProjectsList from "./ProjectsList.vue";

export default defineComponent({
  components: {
    Input,
    Button,
    ProjectsList,
  },

  data() {
    return {
      filterOptions: ["Name", "Time Created", "Last Opened", "Accuracy"],
      filterOption: "",
      searchString: "",
    };
  },
});
</script>
