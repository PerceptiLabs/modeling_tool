import { computed } from "vue";

export function useModelWrapper(
  props: { [i: string]: unknown },
  emit: (event: string, ...args: unknown[]) => void,
  name = "modelValue",
) {
  return computed({
    get: () => props[name],
    set: (value) => emit(`update:${name}`, value),
  });
}
