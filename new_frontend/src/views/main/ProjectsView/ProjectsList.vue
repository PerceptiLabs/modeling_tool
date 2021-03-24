<template>
  <div class="flex flex-wrap">
    <project-overview
      v-for="project in projects"
      :key="project.projectId"
      :project="project"
      class="m-4"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useStore } from "vuex";
import { getModule } from "vuex-module-decorators";

import ProjectsModule from "@/store/modules/mod_projects";

import ProjectOverview from "./ProjectOverview.vue";

export default defineComponent({
  components: {
    ProjectOverview,
  },

  async setup() {
    const projectsStore = getModule(ProjectsModule, useStore());

    await projectsStore.getProjects();

    return { projects: projectsStore.projects };
  },
});
</script>
