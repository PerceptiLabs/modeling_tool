<template lang="pug">
div
</template>

<script>
import mixinSet from "@/core/mixins/net-element-settings.js";
import mixinData from "@/core/mixins/net-element-settings-data.js";
import mixinFocus from "@/core/mixins/net-element-settings-input-focus.js";

import SettingsCloud from "@/components/network-elements/elements-settings/setting-clouds.vue";
import SettingsFileList from "@/components/network-elements/elements-settings/setting-file-list.vue";
import ChartSwitch from "@/components/charts/chart-switch.vue";
import TripleInput from "@/components/base/triple-input";

export default {
  name: "SetIoOutput",
  mixins: [mixinSet, mixinData, mixinFocus],
  components: {
    ChartSwitch,
    SettingsCloud,
    TripleInput,
    SettingsFileList,
  },
  mounted() {},
  data() {
    return {
      settings: {
        Type: "IoOutput",
        FeatureName: "",
        FilePath: "",
        DataType: "",
        testInfoIsInput: true, //input  false - labels
        accessProperties: {
          Sources: [] //{type: 'file'/'directory', path: 'PATH'}
        }
      }
    };
  },
  computed: {},
  watch: {}
};
</script>
<style lang="scss" scoped>
.section-data-select {
  font-size: 1.4rem;
  text-align: center;
  .btn {
    display: inline-flex;
    align-items: center;
    width: 15.5rem;
    height: 3.4rem;
    padding: 0 1.5rem;
    background: rgba(97, 133, 238, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 2px;

    font-family: Nunito Sans;
    font-style: normal;
    font-weight: 600;
    font-size: 1.2rem;

    font-weight: 300;
    + .btn {
      margin-top: 0.8rem;
    }
    .icon {
      font-size: 1.75rem;
      margin-right: 0.5rem;
    }
    &:hover {
      box-shadow: inset 0 0 1px 1px $color-5;
    }
    input[type="file"] {
      display: none;
    }
  }
}
.data-select_text {
  margin: 0 1.4rem;
}
.settings-layer_section .file-list-item_settings {
  font-size: 1rem;
  .triple-input_input {
    max-width: 2.8em;
  }
  .triple-input_input ~ .triple-input_input {
    //margin-left: 1em;
  }
}
.settings-layer_section--data label.light-text {
  font-family: Nunito Sans;
  font-style: normal;
  font-weight: 300;
  font-size: 1.1rem;
  line-height: 1.5rem;
}
</style>
