<template>
  <div>
    <div class="border rounded relative mb-2">
      <div class="image-container">
        <img width="200" height="200" :src="image" />
        <div class="tooltip">
          Created: {{ projectCreatedDate }}
          <br />
          Accuracy: --%
        </div>
      </div>
      <div class="absolute border -top-px -right-px bg-white">
        <router-link
          :to="projectDetailLink"
          class="rounded outline-none focus:outline-none p-2 hover:bg-gray-100"
        >
          <fa-icon icon="external-link-alt" />
        </router-link>
        <Button button-type="icon" icon="trash-alt" />
      </div>
    </div>
    <p class="mb-2">
      {{ project.name }}
    </p>
    <p class="text-gray-600">Last activity: {{ projectUpdatedDate }}</p>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue";
import dayjs from "dayjs";

import { IProject } from "@/types";
import { Button } from "@/components";

export default defineComponent({
  components: {
    Button,
  },

  props: {
    project: Object as PropType<IProject>,
  },

  setup(props) {
    return {
      image: `https://www.gravatar.com/avatar/${props.project.projectId}?s=200&d=identicon`,
      projectCreatedDate: computed(() =>
        dayjs(props.project.created).format("YYYY-MM-DD"),
      ),
      projectUpdatedDate: computed(() =>
        dayjs(props.project.updated).format("YYYY-MM-DD"),
      ),
      projectDetailLink: computed(() => `/projects/${props.project.projectId}`),
    };
  },
});
</script>

<style lang="scss" scoped>
.tooltip {
  display: none;
  bottom: -24px;
  right: -120px;
}

.image-container:hover .tooltip {
  display: block;
}
</style>
