<template>
  <div
    class="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12"
  >
    <div class="relative py-3 sm:max-w-xl sm:mx-auto">
      <div
        class="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"
      ></div>
      <div
        class="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20"
      >
        <div class="max-w-md mx-auto">
          <div class="divide-y divide-gray-200">
            <h1 class="text-2xl font-bold">Tailwind CSS Test</h1>
            <div
              class="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7"
            >
              <p>
                An advanced online playground for Tailwind CSS, including
                support for things like:
              </p>
              <ul class="list-disc space-y-2">
                <li class="flex items-start">
                  <span class="h-6 flex items-center sm:h-7">
                    <svg
                      class="flex-shrink-0 h-5 w-5 text-cyan-500"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </span>
                  <p class="ml-2">
                    Customizing your
                    <code class="text-sm font-bold text-gray-900"
                      >tailwind.config.js</code
                    >
                    file
                  </p>
                </li>
                <li class="flex items-start">
                  <span class="h-6 flex items-center sm:h-7">
                    <svg
                      class="flex-shrink-0 h-5 w-5 text-cyan-500"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </span>
                  <p class="ml-2">
                    Extracting classes with
                    <code class="text-sm font-bold text-gray-900">@apply</code>
                  </p>
                </li>
                <li class="flex items-start">
                  <span class="h-6 flex items-center sm:h-7">
                    <svg
                      class="flex-shrink-0 h-5 w-5 text-cyan-500"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fill-rule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </span>
                  <p class="ml-2">Code completion with instant preview</p>
                </li>
              </ul>
              <p>
                Perfect for learning how the framework works, prototyping a new
                idea, or creating a demo to share online.
              </p>
            </div>
            <div
              class="pt-6 text-base leading-6 font-bold sm:text-lg sm:leading-7"
            >
              <p class="mb-3">Vuex Test</p>
              <p class="mb-3">Value: {{ templateStore.getData }}</p>
              <div class="flex justify-between">
                <button
                  class="border border-gray p-2 bg-black text-white rounded"
                  v-on:click="onIncrement()"
                >
                  Increment
                </button>
                <button
                  class="border border-gray p-2 bg-white rounded"
                  v-on:click="onDecrement()"
                >
                  Decrement
                </button>
                <button
                  class="border border-gray p-2 bg-white rounded"
                  v-on:click="onReset()"
                >
                  Reset
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { getModule } from "vuex-module-decorators";
import { defineComponent } from "vue";
import { useStore } from "vuex";

import TemplateModule from "@/store/modules/mod_template";

export default defineComponent({
  setup() {
    const templateStore = getModule(TemplateModule, useStore());

    return { templateStore };
  },

  methods: {
    onIncrement() {
      this.templateStore.increment();
    },
    onDecrement() {
      this.templateStore.decrement();
    },
    onReset() {
      this.templateStore.reset();
    },
  },
});
</script>
