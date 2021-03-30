<template>
  <div class="flex flex-wrap">
    <span class="m-4" v-if="isLoading">
      Loading All Projects...
    </span>
    <project-overview
      v-else
      v-for="project in projects"
      :key="project.projectId"
      :project="project"
      class="m-4"
    />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, Ref, ref } from "vue";
import { useStore } from "vuex";
import { getModule } from "vuex-module-decorators";

import ProjectsModule from "@/store/modules/mod_projects";

import ProjectOverview from "./ProjectOverview.vue";

export default defineComponent({
  components: {
    ProjectOverview,
  },

  setup() {
    const projectsStore = getModule(ProjectsModule, useStore());
    const isLoading: Ref<boolean> = ref(false);

    (async () => {
      isLoading.value = true;
      await projectsStore.getProjects();
      isLoading.value = false;
    })();

    return { projects: computed(() => projectsStore.projects), isLoading };
  },
});
</script>
