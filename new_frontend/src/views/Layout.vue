<template>
  <div class="flex flex-col h-screen w-screen">
    <NavHeader />
    <div class="flex h-full w-full">
      <NavSidebar />
      <router-view></router-view>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

import NavHeader from "@/components/Nav/NavHeader.vue";
import NavSidebar from "@/components/Nav/NavSidebar.vue";

export default defineComponent({
  components: { NavHeader, NavSidebar },
});
</script>

<style lang="scss" scoped></style>
