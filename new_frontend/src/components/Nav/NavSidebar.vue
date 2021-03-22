<template>
  <div class="border-r border-gray-300 bottom-0 h-full sticky w-40">
    <component :is="componentType" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, Ref, watch } from "vue";
import { useRoute } from "vue-router";

import NavSidebarProjectOverView from "./NavSidebarProjectOverview.vue";
import NavSidebarProjectDetail from "./NavSidebarProjectDetail.vue";

export default defineComponent({
  components: { NavSidebarProjectOverView, NavSidebarProjectDetail },
  setup() {
    const route = useRoute();
    const componentType: Ref<string> = ref("NavSidebarProjectOverView");

    watch(
      () => route.name,
      () => {
        if (route.name === "ModelsView") {
          componentType.value = "NavSidebarProjectDetail";
        } else {
          componentType.value = "NavSidebarProjectOverView";
        }
      },
    );

    return { componentType };
  },
});
</script>
