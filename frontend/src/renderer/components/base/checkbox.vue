<template lang="pug">
label.custom-checkbox(
  :class="{ 'v-2': isNewUi, 'is-mini-map': isMiniMap, disabled: disabled, 'type-secondary': styleTypeSecondary }"
)
  .checkbox-text(v-if="labelPosition === 'left'")
    slot
  input(
    type="checkbox",
    :disabled="disabled",
    v-model="valueInput",
    @change="change"
  )
  .checkbox-fake(:class="{ 'checkbox-fake--icon': iconTheme }")
    i.icon.icon-check
  .checkbox-text(v-if="labelPosition === 'right'")
    slot
</template>

<script>
export default {
  name: "BaseCheckbox",

  props: {
    value: Boolean,
    labelPosition: {
      type: String,
      default: "right",
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    iconTheme: {
      type: Boolean,
      default: false,
    },
    isNewUi: {
      type: Boolean,
      default: false,
    },
    isMiniMap: {
      type: Boolean,
      default: false,
    },
    styleTypeSecondary: {
      type: Boolean,
      default: false,
    },
    onClick: {
      type: Function,
      default: () => {},
    },
  },
  mounted() {
    this.valueInput = this.value;
  },
  data() {
    return {
      valueInput: null,
    };
  },
  watch: {
    value: function(newValue) {
      this.valueInput = newValue;
    },
  },
  methods: {
    change(event) {
      const newValue = event.target.checked;
      this.valueInput = newValue;
      this.$emit("input", newValue);

      this.onClick();
    },
  },
};
</script>

<style lang="scss" scoped>
.custom-checkbox {
  font-size: 1.2rem;
  position: relative;
  display: inline-flex;
  align-items: center;
  padding: 0;

  input[type="checkbox"] {
    position: absolute;
    left: -9999px;
    opacity: 0;
    width: 1px;
    height: 1px;
    &:checked + .checkbox-fake {
      //background: $bg-grad-blue;
      //box-shadow: $icon-shad;
      border-color: $color-6;
      background: $color-6;
      .icon {
        opacity: 1;
        color: $black;
      }
      /*<!--&.checkbox-fake&#45;&#45;icon {-->*/
      /*<!--  background: $bg-workspace;-->*/
      /*<!--  &:after {-->*/
      /*<!--    opacity: 1;-->*/
      /*<!--  }-->*/
      /*<!--}-->*/
    }

    &:disabled {
      pointer-events: none;
      color: gray;
      opacity: 50%;
      + .checkbox-fake {
        cursor: not-allowed;
        background: theme-var($neutral-6);
      }
    }
  }
  .checkbox-text {
    font-size: inherit;
    color: inherit;
    margin-right: 0.75em;
  }
  .checkbox-fake {
    position: relative;
    // flex: 0 0 1.4em;
    width: 18px;
    height: 18px;
    cursor: pointer;
    // background: theme-var($neutral-8);
    border: 1px solid theme-var($neutral-1);
    border-radius: 2px;

    .icon {
      font-size: 12px;
      line-height: 1;
      position: absolute;
      top: 50%;
      left: 50%;
      opacity: 0;
      transform: translate(-50%, -50%);
    }
    /*<!--&.checkbox-fake&#45;&#45;icon {-->*/
    /*<!--  background-color: $bg-workspace;-->*/
    /*<!--  &:after {-->*/
    /*<!--    content: '\e937';-->*/
    /*<!--    font-family: 'icomoon';-->*/
    /*<!--    font-size: .9em;-->*/
    /*<!--    line-height: 1;-->*/
    /*<!--    position: absolute;-->*/
    /*<!--    top: 50%;-->*/
    /*<!--    left: 50%;-->*/
    /*<!--    opacity: 0;-->*/
    /*<!--    transform: translate(-50%, -50%);-->*/
    /*<!--  }-->*/
    /*<!--}-->*/
    + .checkbox-text {
      margin-left: 0.75em;
    }
  }
  .text-error {
    position: absolute;
    top: 100%;
    left: 0;
  }

  &.v-2 {
    .checkbox-fake {
      flex: 0 0 18px;
      width: 18px;
      height: 18px;
      background: theme-var($neutral-8);
      border: $border-1;
      border-radius: 2px;
    }
  }
  &.type-secondary {
    .checkbox-fake {
      flex: 0 0 18px;
      width: 18px;
      height: 18px;
      background: transparent;
      border-radius: 2px;
      border: 1px solid #b6c7fb;
    }
    input[type="checkbox"] {
      &:checked + .checkbox-fake {
        background-color: #b6c7fb;
      }
    }
    .checkbox-text {
      color: #fff;
      font-size: 14px;
      font-family: "Roboto", sans-serif;
    }
  }
  &.is-mini-map {
    .checkbox-fake {
      background: #23252a;
    }
  }
  &.disabled {
    pointer-events: none;
    color: gray;
    .checkbox-fake {
      background: theme-var($neutral-7);
    }
  }
  &.is-silver {
    input[type="checkbox"] {
      position: absolute;
      left: -9999px;
      opacity: 0;
      width: 1px;
      height: 1px;
      &:checked + .checkbox-fake {
        background: #eee;
      }
    }
  }
}
</style>
