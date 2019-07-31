<template lang="pug">
  net-base-settings(
    :current-el="currentEl"
    id-set-btn="tutorial_button-apply"
    @press-apply="saveSettings($event)"
    @press-confirm="confirmSettings"
    @press-update="updateCode"
  )
    template(slot="Settings-content")
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.dimension")
          .form_label Dimension:
          #tutorial_dimension.form_input(data-tutorial-hover-info)
            base-radio(group-name="group" value-input="Automatic" v-model="settings.Conv_dim")
              span Automatic
            base-radio(group-name="group" value-input="1D" v-model="settings.Conv_dim")
              span 1D
            base-radio(group-name="group" value-input="2D" v-model="settings.Conv_dim")
              span 2D
            base-radio(group-name="group" value-input="3D" v-model="settings.Conv_dim")
              span 3D
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.patchSize")
          .form_label Patch size:
          #tutorial_patch-size.form_input.tutorial-relative(data-tutorial-hover-info)
            input( type="text"
              v-model="settings.Patch_size"
              ref="pathSize"
            )
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.stride")
          .form_label Stride:
          #tutorial_stride.form_input.tutorial-relative(data-tutorial-hover-info)
            input( type="text"
              v-model="settings.Stride"
            )
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.featureMaps")
          .form_label Feature maps:
          #tutorial_feature-maps.tutorial-relative.form_input(data-tutorial-hover-info)
            input( type="text"
              v-model="settings.Feature_maps"
            )

      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.zeroPadding")
          .form_label Zero-padding:
          #tutorial_zero-padding.form_input(data-tutorial-hover-info)
            base-radio(group-name="group3" value-input="'SAME'"  v-model="settings.Padding")
              span SAME
            base-radio(group-name="group3" value-input="'VALID'"  v-model="settings.Padding")
              span VALID
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.activationFunction")
          .form_label Activation function:
          #tutorial_activeFunc.form_input(data-tutorial-hover-info)
            base-radio(group-name="group1" value-input="None"  v-model="settings.Activation_function")
              span None
            base-radio(group-name="group1" value-input="Sigmoid"  v-model="settings.Activation_function")
              span Sigmoid
            base-radio(group-name="group1" value-input="ReLU"  v-model="settings.Activation_function")
              span ReLU
            base-radio(group-name="group1" value-input="Tanh"  v-model="settings.Activation_function")
              span Tanh
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.dropout")
          .form_label Dropout:
          #tutorial_dropout.form_input(data-tutorial-hover-info)
            base-radio(group-name="group5" :value-input="true"  v-model="settings.Dropout")
              span Yes
            base-radio(group-name="group5" :value-input="false"  v-model="settings.Dropout")
              span No
      .settings-layer_section
        .form_row(v-tooltip-interactive:right="interactiveInfo.pooling")
          .form_label Pooling:
          #tutorial_pooling.form_input(data-tutorial-hover-info)
            base-radio(group-name="group6" :value-input="true"  v-model="settings.PoolBool")
              span Yes
            base-radio(group-name="group6" :value-input="false"  v-model="settings.PoolBool")
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
          .form_row(v-tooltip-interactive:right="interactiveInfo.poolingType")
            .form_label Pooling type:
            .form_input
              base-radio(group-name="Pooling" value-input="Max"  v-model="settings.Pooling")
                span Max pooling
              base-radio(group-name="Pooling" value-input="Mean"  v-model="settings.Pooling")
                span Mean pooling
        .settings-layer_section
          .form_row(v-tooltip-interactive:right="interactiveInfo.poolingArea")
            .form_label Pooling area:
            .form_input
              input(type="text" v-model="settings.Pool_area")
        .settings-layer_section
          .form_row(v-tooltip-interactive:right="interactiveInfo.poolingStride")
            .form_label Pooling stride:
            .form_input
              input(type="text" v-model="settings.Pool_stride")
        .settings-layer_section
          .form_row(v-tooltip-interactive:right="interactiveInfo.ZeroPaddingPooling")
            .form_label Zero-padding for pooling:
            .form_input
              base-radio(group-name="Pool_padding" value-input="'SAME'" v-model="settings.Pool_padding")
                span SAME
              base-radio(group-name="Pool_padding" value-input="'VALID'" v-model="settings.Pool_padding")
                span VALID
    template(slot="Code-content")
      settings-code(
        :current-el="currentEl"
        v-model="coreCode"
        )

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'SetDeepLearningConv',
  mixins: [mixinSet],
  mounted() {
    this.focusFirstTutorialField();
  },
  data() {
    return {
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
      },
      interactiveInfo: {
        dimension: {
          title: 'Dimension',
          text: 'Choose which type of convolutional operation to use'
        },
        patchSize: {
          title: 'Patch size',
          text: 'Set the patch size'
        },
        stride: {
          title: 'Stride',
          text: 'Set the stride'
        },
        featureMaps: {
          title: 'Feature maps',
          text: 'Set the number of feature maps.'
        },
        zeroPadding: {
          title: 'Zero-padding',
          text: 'Choose to use zero-padding or not.'
        },
        activationFunction: {
          title: 'Activation function',
          text: 'Choose which activation function to use'
        },
        dropout: {
          title: 'Dropout',
          text: 'Choose if dropout should be used or not'
        },
        pooling: {
          title: 'Pooling',
          text: 'Choose if dropout should be used or not'
        },
        poolingType: {
          title: 'Pooling type',
          text: 'Choose if pooling should be used or not'
        },
        poolingArea: {
          title: 'Pooling area',
          text: 'Choose pooling area'
        },
        poolingStride: {
          title: 'Pooling stride',
          text: 'Choose pooling stride'
        },
        ZeroPaddingPooling: {
          title: 'Zero-padding',
          text: 'Zero-padding for pooling'
        },
      },
    }
  },
  computed: {
    ...mapGetters({
      isTutorialMode:   'mod_tutorials/getIstutorialMode',
    }),
    codeDefault() {
      let dim = '';
      let activeFunc = '';
      let pooling = '';
      let switcherDim = calcSwitcher(this);
      //console.log(switcherDim);
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
      return {
        Output: `${dim}\n${activeFunc}\n${pooling}`
      };

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
    saveSettings(tabName) {
      this.applySettings(tabName);
      this.tutorialPointActivate({way:'next', validation: 'tutorial_patch-size'})
    },
    focusFirstTutorialField() {
      this.$nextTick(()=> {
        if (this.isTutorialMode) this.$refs.pathSize.focus()
      })
    }
  }
}
</script>
