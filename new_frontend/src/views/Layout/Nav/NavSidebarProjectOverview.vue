<template>
  <div class="bottom-0 flex flex-col h-full justify-between sticky text-black">
    <div class="flex flex-col text-left">
      <!-- Project list -->
      <div
        v-if="projects"
        class="border-b border-gray-200 cursor-pointer flex flex-col py-4 w-full"
      >
        <router-link
          v-for="project in projects"
          :key="project.projectId"
          class="cursor-pointer hover:bg-indigo-500 hover:bg-opacity-20 px-6 py-2 truncate w-full"
          :to="{ name: 'ModelsView', params: { projectId: project.projectId } }"
        >
          {{ project.name }}
        </router-link>
      </div>

      <!-- Create project -->
      <router-link
        class="flex hover:bg-indigo-500 hover:bg-opacity-20 items-center justify-center py-2 w-full"
        :to="{ name: '' }"
      >
        <img
          src="/svg/plus.svg"
          class="flex-none h-2 pr-1"
          alt="to-all-projects"
        />
        <div>Create project</div>
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "vue";
import { useStore } from "vuex";
import { getModule } from "vuex-module-decorators";

import ProjectsModule from "@/store/modules/mod_projects";

export default defineComponent({
  setup() {
    const projectsStore = getModule(ProjectsModule, useStore());

    return { projects: computed(() => projectsStore.projects) };
  },
});
</script>
