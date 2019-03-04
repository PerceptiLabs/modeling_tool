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
      .popup_body(
        :class="{'active': tabSelected == 0}"
      )
        .settings-layer
          .settings-layer_section
            .form_row
              .form_label Dimension:
              .form_input
                base-radio(groupName="group" valueInput="Automatic" v-model="settings.Deconv_dim")
                  span Automatic
                base-radio(groupName="group" valueInput="1D" v-model="settings.Deconv_dim")
                  span 1D
                base-radio(groupName="group" valueInput="2D" v-model="settings.Deconv_dim")
                  span 2D
                base-radio(groupName="group" valueInput="3D" v-model="settings.Deconv_dim")
                  span 3D
          .settings-layer_section
            .form_row
              .form_label Stride:
              .form_input
                input(type="text" v-model="settings.Stride")
          .settings-layer_section
            .form_row
              .form_label Feature maps:
              .form_input
                input(type="text" v-model="settings.Feature_maps")

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
                base-radio(groupName="group5" :valueInput="false"  v-model="settings.Dropout")
                  span None
                base-radio(groupName="group5" :valueInput="true"  v-model="settings.Dropout")
                  span Sigmoid

      .popup_body(:class="{'active': tabSelected == 1}")
        settings-code(
          :the-code="coreCode"
        )
    .settings-layer_foot
      button.btn.btn--primary(type="button" @click="applySettings") Apply

</template>

<script>
import mixinSet       from '@/core/mixins/net-element-settings.js';
import SettingsCode   from '@/components/network-elements/elements-settings/setting-code.vue';

export default {
  name: 'SetDeepLearningDeconv',
  mixins: [mixinSet],
  components: {
    SettingsCode
  },
  data() {
    return {
      tabs: ['Settings', 'Code'],
      settings: {
        Deconv_dim: "2D", //Automatic, 1D, 2D, 3D
        Stride: "2",
        Padding: "'SAME'", //'SAME', 'VALID'
        Feature_maps: "8",
        Activation_function: "Sigmoid", //Sigmoid, ReLU, Tanh, None
        Dropout: false, //True, False
      }
    }
  },
  computed: {
    coreCode() {
      let dim = '';
      let activeFunc = '';
      let pooling = '';

      switch (this.settings.Deconv_dim) {
        case 'Automatic':
          dim = `${this.settings.Deconv_dim} = str(len(X.get_shape())-1) + "D";`;
          break;
        case '1D':
          dim = `shape=[${this.settings.Stride},X.get_shape()[-1].value, ${this.settings.Feature_maps}];
initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(${this.settings.Stride}**2 *${this.settings.Feature_maps})));
W = tf.Variable(initial);
initial = tf.constant(0.1, shape=[${this.settings.Feature_maps}]);
b=tf.Variable(initial);
output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*${this.settings.Stride} for node_shape in X.get_shape().as_list()[1:-1]]+[${this.settings.Feature_maps}]);
node = tf.nn.conv1d_transpose(X, W, output_shape, ${this.settings.Stride},padding=${this.settings.Padding})${this.settings.Dropout ? '\nnode=tf.nn.dropout(node, keep_prob);' : ';'}
node=node+b;`;
          break;
        case '2D':
          dim = `shape=[${this.settings.Stride},${this.settings.Stride},X.get_shape()[-1].value,${this.settings.Feature_maps}];
initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(${this.settings.Stride}**2 * ${this.settings.Feature_maps})));
W = tf.Variable(initial);
initial = tf.constant(0.1, shape=[${this.settings.Feature_maps}]);
b=tf.Variable(initial);
output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*"+${this.settings.Stride}+" for node_shape in X.get_shape().as_list()[1:-1]]+["+${this.settings.Feature_maps}+"]);
node = tf.nn.conv2d_transpose(X, W, output_shape, strides=[1, ${this.settings.Stride}, ${this.settings.Stride}, 1], padding=${this.settings.Padding})${this.settings.Dropout ? '\nnode=tf.nn.dropout(node, keep_prob);' : ';'}
node=node+b;`;
          break;
        case '3D':
          dim = `shape=[${this.settings.Stride},${this.settings.Stride},Stride"],X.get_shape()[-1].value,${this.settings.Feature_maps}];
initial = tf.truncated_normal(shape, stddev=np.sqrt(2/(${this.settings.Stride}**2 * ${this.settings.Feature_maps})));
W = tf.Variable(initial);
initial = tf.constant(0.1, shape=[${this.settings.Feature_maps}]);
b=tf.Variable(initial);
output_shape=tf.stack([tf.shape(X)[0]]+[node_shape*${this.settings.Stride} for node_shape in X.get_shape().as_list()[1:-1]]+[${this.settings.Feature_maps}]);
node = tf.nn.conv3d_transpose(X, W, output_shape, strides=[1, ${this.settings.Stride}, ${this.settings.Stride}, ${this.settings.Stride}, 1], padding=${this.settings.Padding})${this.settings.Dropout ? '\nnode=tf.nn.dropout(node, keep_prob);' : ';'}
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
          pooling = `Y=max_pool(Y, ${this.settings.Pool_area}, ${this.settings.Stride},${this.settings.Padding},${this.settings.Conv_dim});`;
        } else {
          pooling = `Y=tf.nn.pool(Y, window_shape=${this.settings.Pool_area},pooling_type='AVG',${this.settings.Padding},strides=${this.settings.Stride});`
        }
      }
      return `${dim}\n${activeFunc}\n${pooling}`
    }
  }
}
</script>
