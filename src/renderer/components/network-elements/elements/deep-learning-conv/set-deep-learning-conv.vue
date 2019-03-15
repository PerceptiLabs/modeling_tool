<template lang="pug">
  .popup
    ul.popup_tab-set
      button.popup_header(
        v-for="(tab, i) in tabs"
        :key="tab.i"
        @click="setTab(i)"
        :class="{'disable': tabSelected != i}"
      )
        h3(v-html="tab")
    .popup_tab-body
      .popup_body(:class="{'active': tabSelected == 0}")
        .settings-layer
          .settings-layer_section
            .form_row
              .form_label Dimension:
              .form_input
                base-radio(groupName="group" valueInput="Automatic" v-model="settings.Conv_dim")
                  span Automatic
                base-radio(groupName="group" valueInput="1D" v-model="settings.Conv_dim")
                  span 1D
                base-radio(groupName="group" valueInput="2D" v-model="settings.Conv_dim")
                  span 2D
                base-radio(groupName="group" valueInput="3D" v-model="settings.Conv_dim")
                  span 3D
          .settings-layer_section
            .form_row
              .form_label Patch size:
              .form_input(id="tutorial_patch-size")
                input(type="text" @input="changeInputFields($event, 'Patch_size')")
          .settings-layer_section
            .form_row
              .form_label Stride:
              .form_input(id="tutorial_stride")
                input(type="text" @input="changeInputFields($event, 'Stride')")
          .settings-layer_section
            .form_row
              .form_label Feature maps:
              .form_input(id="tutorial_feature-maps")
                input(type="text" @input="changeInputFields($event, 'Feature_maps')")

          .settings-layer_section
            .form_row
              .form_label Zero-padding:
              .form_input
                base-radio(groupName="group3" valueInput="'SAME'"  v-model="settings.Padding")
                  span SAME
                base-radio(groupName="group3" valueInput="'VALID'"  v-model="settings.Padding")
                  span VALID
          .settings-layer_section
            .form_row
              .form_label Activation function:
              .form_input
                base-radio(groupName="group1" valueInput="None"  v-model="settings.Activation_function")
                  span None
                base-radio(groupName="group1" valueInput="Sigmoid"  v-model="settings.Activation_function")
                  span Sigmoid
                base-radio(groupName="group1" valueInput="ReLU"  v-model="settings.Activation_function")
                  span ReLU
                base-radio(groupName="group1" valueInput="Tanh"  v-model="settings.Activation_function")
                  span Tanh
          .settings-layer_section
            .form_row
              .form_label Dropout:
              .form_input
                base-radio(groupName="group5" :valueInput="true"  v-model="settings.Dropout")
                  span Yes
                base-radio(groupName="group5" :valueInput="false"  v-model="settings.Dropout")
                  span No
          .settings-layer_section
            .form_row
              .form_label Pooling:
              .form_input
                base-radio(groupName="group6" :valueInput="true"  v-model="settings.PoolBool")
                  span Yes
                base-radio(groupName="group6" :valueInput="false"  v-model="settings.PoolBool")
                  span No
          //-.settings-layer_section
            .form_row
              .form_label Batch Normalization:
              .form_input
                base-radio(groupName="group6")
                  span Yes
                base-radio(groupName="group6")
                  span No
          //-.settings-layer_section
            .form_row
              .form_label Pooling:
              .form_input
                base-checkbox(valueInput="Pooling" v-model="settings.pooling")
                //input(type="checkbox" :value="settings.pooling" @change="changeCheckbox($event)")
          template(v-if="settings.PoolBool")
            .settings-layer_section
              .form_row
                .form_label Pooling type:
                .form_input
                  base-radio(groupName="Pooling" valueInput="Max"  v-model="settings.Pooling")
                    span Max pooling
                  base-radio(groupName="Pooling" valueInput="Mean"  v-model="settings.Pooling")
                    span Mean pooling
            .settings-layer_section
              .form_row
                .form_label Pooling area:
                .form_input
                  input(type="text" v-model="settings.Pool_area")
            .settings-layer_section
              .form_row
                .form_label Pooling stride:
                .form_input
                  input(type="text" v-model="settings.Pool_stride")
            .settings-layer_section
              .form_row
                .form_label Zero-padding for pooling:
                .form_input
                  base-radio(groupName="Pool_padding" valueInput="'SAME'" v-model="settings.Pool_padding")
                    span SAME
                  base-radio(groupName="Pool_padding" valueInput="'VALID'" v-model="settings.Pool_padding")
                    span VALID

          .settings-layer_foot
            button.btn.btn--primary(type="button" @click="saveSettings" id="tutorial_apply-button") Apply

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
          :the-code="coreCode"
        )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
import { mapActions } from 'vuex';

export default {
  name: 'SetDeepLearningConv',
  mixins: [mixinSet],
  components: {
    SettingsCode
  },
  data() {
    return {
      tabs: ['Settings', 'Code'],
      settings: {
        Conv_dim: "2D", //Automatic, 1D, 2D, 3D
        Patch_size: "", // 3
        Stride: "",     // 2
        Padding: "'SAME'", //'SAME', 'VALID'
        Feature_maps: "",  // 8
        Activation_function: "Sigmoid", //Sigmoid, ReLU, Tanh, None
        Dropout: false, //True, False
        PoolBool: false, //True, False
        Pooling: "Max", //Max, Mean
        Pool_area: "2",
        Pool_padding: "'SAME'", //'SAME', 'VALID'
        Pool_stride: "2",
      }
    }
  },
  computed: {
    coreCode() {
      let addPooling = '';
      if(this.settings.Pooling === "Max") {
        addPooling = `Y=max_pool(Y, properties["${this.settings.Pool_area}"],
               properties["${this.settings.Stride}"],properties["${this.settings.Padding}"],properties["${this.settings.Conv_dim}"])`;
      }
      else {
        addPooling = `Y=tf.nn.pool(Y, window_shape=properties["${this.settings.Pool_area}"],pooling_type='AVG',properties["${this.settings.Padding}"],strides=properties["${this.settings.Stride}"])`
      }
      switch (this.settings.Conv_dim) {
        case 'Automatic':
          return `
          properties["${this.settings.Conv_dim}"] = str(len(X.get_shape())-1) + "D"
          ${addPooling}`
          break;
        case '1D':
          return `
          shape=[properties["${this.settings.Patch_size}"],X.get_shape()[-1].value,properties["${this.settings.Feature_maps}"]];
          initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(properties["${this.settings.Patch_size}"]**2 * properties["${this.settings.Feature_maps}"])));
          W = tf.Variable(initial);
          initial = tf.constant(0.1, shape=[properties["${this.settings.Feature_maps}"]]);
          b=tf.Variable(initial);
          node = tf.nn.conv1d(X, W, properties["${this.settings.Stride}"],
          padding=properties["${this.settings.Padding}"]);
          node=tf.nn.dropout(node, keep_prob);
          node=node+b
          ${addPooling}`
          break;
        case '2D':
          return `
          shape=[properties["${this.settings.Patch_size}"],properties["${this.settings.Patch_size}"],X.get_shape()[-1].value,properties["${this.settings.Feature_maps}"]];
          initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(properties["${this.settings.Patch_size}"]**2 * properties["${this.settings.Feature_maps}"])));
          W = tf.Variable(initial);
          initial = tf.constant(0.1, shape=[properties["${this.settings.Feature_maps}"]]);
          b=tf.Variable(initial);
          node = tf.nn.conv2d(X, W, strides=[1, properties["${this.settings.Stride}"],properties["${this.settings.Stride}"], 1], padding=properties["${this.settings.Padding}"]);
          node=tf.nn.dropout(node, keep_prob);
          node=node+b
          ${addPooling}`
          break;
        case '3D':
          return `
          shape=[properties["${this.settings.Patch_size}"],properties["${this.settings.Patch_size}"],properties["${this.settings.Patch_size}"],X.get_shape()[-1].value,properties["${this.settings.Feature_maps}"]];
          initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(properties["${this.settings.Patch_size}"]**2 * properties["${this.settings.Feature_maps}"])));
          W = tf.Variable(initial);
          initial = tf.constant(0.1, shape=[properties["${this.settings.Feature_maps}"]]);
          b=tf.Variable(initial);
          node = tf.nn.conv3d(X, W, strides=[1, properties["${this.settings.Stride}"],
          properties["${this.settings.Stride}"], properties["${this.settings.Stride}"], 1],
          padding=properties["${this.settings.Padding}"]);
          node=tf.nn.dropout(node, keep_prob);
          node=node+b
          ${addPooling}`
          break;
      }
    },
    patch_size() {
      return this.settings.Patch_size
    },
    stride() {
      return this.settings.Stride
    },
    feature_maps() {
      return this.settings.Feature_maps
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    changeInputFields(event, settingProperty) {
      this.settings[settingProperty] = event.target.value
    },
    saveSettings() {
      this.applySettings()
      this.tutorialPointActivate({way:'next', validation: 'tutorial_apply-button'})
    }
  },
  watch: {
    // for tutorial
    patch_size() {
      this.tutorialPointActivate({way:'next', validation: 'tutorial_patch-size'})
    },
    stride() {
      this.tutorialPointActivate({way:'next', validation: 'tutorial_stride'})
    },
    feature_maps() {
      this.tutorialPointActivate({way:'next', validation: 'tutorial_feature-maps'})
    }
  }
}
</script>
