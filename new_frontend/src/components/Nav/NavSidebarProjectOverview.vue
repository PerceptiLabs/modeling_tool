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
          :key="project.id"
          class="cursor-pointer hover:bg-indigo-500 hover:bg-opacity-20 px-6 py-2 truncate w-full"
          :to="{ name: 'ModelsView', params: { projectId: project.id } }"
          >{{ project.name }}</router-link
        >
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
import { defineComponent, reactive } from "vue";

// For testing purposes
interface ProjectMeta {
  id: number;
  name: string;
}

export default defineComponent({
  setup() {
    // For testing purposes, will be populated from rygg
    const projects = reactive<ProjectMeta[]>([]);
    projects.push({
      id: 1,
      name: "Project 1",
    });
    projects.push({
      id: 2,
      name: "Project 123456789123456789",
    });

    return { projects };
  },
});
</script>
