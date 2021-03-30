<template>
  <div class="w-full h-full px-12 py-10">
    <span v-if="isLoading">
      Loading Models...
    </span>
    <ul v-else>
      <li v-for="model in project.models" :key="model">
        <router-link
          :to="{
            name: 'ModelView',
            params: { modelId: models[model].modelId },
          }"
        >
          {{ models[model].name }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, Ref } from "vue";
import { useStore } from "vuex";
import { useRoute } from "vue-router";
import { getModule } from "vuex-module-decorators";

import ProjectsModule from "@/store/modules/mod_projects";
import ModelsModule from "@/store/modules/mod_models";
import logger from "@/core/logger";
import router from "@/router";

export default defineComponent({
  setup() {
    const route = useRoute();
    const projectsStore = getModule(ProjectsModule, useStore());
    const modelsStore = getModule(ModelsModule, useStore());
    const projectId = +route.params.projectId;

    const isLoading: Ref<boolean> = ref(false);
    const currentProject = projectsStore.projects[projectId];

    if (!currentProject) {
      logger.error(
        `Project${projectId} is not loaded yet. Navigating to projects overview screen`,
      );
      router.push({
        name: "ProjectsView",
      });
    }

    (async () => {
      isLoading.value = true;
      await Promise.all(
        currentProject.models.map((model) => modelsStore.getModel(model)),
      );
      isLoading.value = false;
    })();

    return {
      project: currentProject,
      models: modelsStore.models,
      isLoading,
    };
  },
});
</script>
