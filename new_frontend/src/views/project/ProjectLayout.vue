<template>
  <div class="w-full h-full">
    <span v-if="isLoading">Loading Project ...</span>
    <router-view v-else></router-view>
  </div>
</template>

<script lang="ts">
import { useRoute } from "vue-router";
import { defineComponent, ref, Ref } from "vue";
import { useStore } from "vuex";
import { getModule } from "vuex-module-decorators";

import ProjectsModule from "@/store/modules/mod_projects";
import logger from "@/core/logger";
import router from "@/router";

export default defineComponent({
  setup() {
    const route = useRoute();
    const projectId = +route.params.projectId;
    const isLoading: Ref<boolean> = ref(false);
    const projectsStore = getModule(ProjectsModule, useStore());

    (async () => {
      try {
        isLoading.value = true;
        await projectsStore.getProject(projectId);
        isLoading.value = false;
      } catch (e) {
        logger.error(
          `Failed to load project${projectId}. Navigating to Projects Overview Page.  `,
        );
        router.push({
          name: "ProjectsView",
        });
      }
    })();

    return {
      projectsStore,
      isLoading,
    };
  },
});
</script>
