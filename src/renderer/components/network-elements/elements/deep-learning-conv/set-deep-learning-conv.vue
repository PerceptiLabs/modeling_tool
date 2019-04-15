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
              #tutorial_patch-size.form_input.tutorial-relative
                input( type="text"
                  v-model="settings.Patch_size"
                  ref="pathSize"
                )
          .settings-layer_section
            .form_row
              .form_label Stride:
              #tutorial_stride.form_input.tutorial-relative
                input( type="text"
                  v-model="settings.Stride"
                  @focus="onFocus('tutorial_patch-size')"
                )
          .settings-layer_section
            .form_row
              .form_label Feature maps:
              #tutorial_feature-maps.tutorial-relative.form_input
                input( type="text"
                  v-model="settings.Feature_maps"
                  @focus="onFocus('tutorial_stride')"
                  @blur="onBlur('tutorial_feature-maps')"
                )

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

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
          :the-code="coreCode"
        )
    .settings-layer_foot
      button#tutorial_apply-button.btn.btn--primary(type="button" @click="saveSettings") Apply

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';
import { mapGetters, mapActions } from 'vuex';

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
        Patch_size: "3",
        Stride: "2",
        Padding: "'SAME'", //'SAME', 'VALID'
        Feature_maps: "8",
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
  mounted() {
   if(this.isTutorialMode) this.$refs.pathSize.focus()
  },
  computed: {
    ...mapGetters({
      isTutorialMode:   'mod_tutorials/getIstutorialMode',
    }),
    coreCode() {
      let dim = '';
      let activeFunc = '';
      let pooling = '';
      let switcherDim = calcSwitcher(this);
      switch (switcherDim) {
        case '1D':
          dim = `shape=[${this.settings.Patch_size},${this.codeInputDim}[-1],${this.settings.Feature_maps}];
initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(${this.settings.Patch_size}**2 * ${this.settings.Feature_maps})));
initial = tf.constant(0.1, shape=[${this.settings.Feature_maps}]);
b=tf.Variable(initial);
node = tf.nn.conv1d(X, W, ${this.settings.Stride}, padding=${this.settings.Padding})${this.settings.Dropout ? '\nnode=tf.nn.dropout(node, keep_prob);' : ';'}
node=node+b;`;
          break;
        case '2D':
          dim = `shape=[${this.settings.Patch_size},${this.settings.Patch_size},${this.codeInputDim}[-1],${this.settings.Feature_maps}];
initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(${this.settings.Patch_size}**2 * ${this.settings.Feature_maps})));
W = tf.Variable(initial);
initial = tf.constant(0.1, shape=[${this.settings.Feature_maps}]);
b=tf.Variable(initial);
node = tf.nn.conv2d(X, W, strides=[1, ${this.settings.Stride},${this.settings.Stride}, 1], padding=${this.settings.Padding})${this.settings.Dropout ? '\nnode=tf.nn.dropout(node, keep_prob);' : ';'}
node=node+b;`;
          break;
        case '3D':
          dim = `shape=[${this.settings.Patch_size},${this.settings.Patch_size},${this.settings.Patch_size},${this.codeInputDim}[-1],${this.settings.Feature_maps}];
initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(${this.settings.Patch_size}**2 * ${this.settings.Feature_maps})));
W = tf.Variable(initial);
initial = tf.constant(0.1, shape=[${this.settings.Feature_maps}]);
b=tf.Variable(initial);
node = tf.nn.conv3d(X, W, strides=[1, ${this.settings.Stride},
${this.settings.Stride}, ${this.settings.Stride}, 1],
padding=${this.settings.Padding})${this.settings.Dropout ? '\nnode=tf.nn.dropout(node, keep_prob);' : ';'}
node=node+b;`;
          break;
      }
      switch (this.settings.Activation_function) {
        case 'Sigmoid':
          activeFunc = `Y=tf.sigmoid(node);`;
          break;
        case 'ReLU':
          activeFunc = `Y=tf.nn.relu(node);`;
          break;
        case 'Tanh':
          activeFunc = `Y=tf.tanh(node);`;
          break;
        case 'None':
          activeFunc = `Y=node;`;
          break;
      }

      if(this.settings.PoolBool) {
        if (this.settings.Pooling === "Max") {
          //pooling = `Y=max_pool(Y, ${this.settings.Pool_area}, ${this.settings.Stride},${this.settings.Padding},${this.settings.Conv_dim});`;
          pooling = '';
          var switcherPooling = calcSwitcher(this);
          console.log('switcherPooling ', switcherPooling);
          switch (switcherPooling) {
            case '1D':
              pooling = `Y=tf.nn.max_pool(Y, ksize=[1, ${this.settings.Pool_area}, 1], strides=[1, ${this.settings.Pool_stride}, 1], padding=${this.settings.Pool_padding})`;
              break;
            case '2D':
              pooling = `Y=tf.nn.max_pool(Y, ksize=[1, ${this.settings.Pool_area}, ${this.settings.Pool_area}, 1], strides=[1, ${this.settings.Pool_stride}, ${this.settings.Pool_stride}, 1], padding=${this.settings.Pool_padding})`;
              break;
            case '3D':
              pooling = `Y=tf.nn.max_pool(Y, ksize=[1, ${this.settings.Pool_area}, ${this.settings.Pool_area}, ${this.settings.Pool_area}, 1], strides=[1, ${this.settings.Pool_stride}, ${this.settings.Pool_stride}, ${this.settings.Pool_stride}, 1], padding=${this.settings.Pool_padding});`;
              break;
          }
        } else {
          pooling = `Y=tf.nn.pool(Y, window_shape=${this.settings.Pool_area},pooling_type='AVG',${this.settings.Pool_padding},strides=${this.settings.Pool_stride});`
        }
      }
      return `${dim}\n${activeFunc}\n${pooling}`

      function calcSwitcher(ctx) {
        var self = ctx;
        if(!self.codeInputDim) return 'Empty Input Dim';
        var switcher = '';
        var codeInputDim = JSON.parse(self.codeInputDim);
        if (self.settings.Conv_dim === 'Automatic') {
          switcher = (codeInputDim.length - 1) + 'D'
        }
        else switcher = self.settings.Conv_dim;
        return switcher
      }
    }
  },
  methods: {
    ...mapActions({
      tutorialPointActivate:    'mod_tutorials/pointActivate',
    }),
    onFocus(inputId) {
      this.tutorialPointActivate({way:'next', validation: inputId})
    },
    onBlur(inputId) {
      this.tutorialPointActivate({way:'next', validation: inputId})
    },
    saveSettings() {
      this.applySettings();
      this.tutorialPointActivate({way:'next', validation: 'tutorial_apply-button'})
    }
  }
}
</script>
