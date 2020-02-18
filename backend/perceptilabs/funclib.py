Placeholder="tf.placeholder(dtype,shape=None,name=None)"
Conv2D="tf.nn.conv2d(input,filter,strides,padding,use_cudnn_on_gpu=True,data_format='NHWC',dilations=[1, 1, 1, 1],name=None)"
Relu6="tf.nn.relu6(features,name=None)"
Relu="tf.nn.relu(features,name=None)"
# FusedBatchNorm="tf.contrib.layers.batch_norm(inputs,decay=0.999,center=True,scale=False,epsilon=0.001,activation_fn=None,param_initializers=None,param_regularizers=None,updates_collections=tf.GraphKeys.UPDATE_OPS,is_training=True,reuse=None,variables_collections=None,outputs_collections=None,trainable=True,batch_weights=None,fused=None,data_format=DATA_FORMAT_NHWC,zero_debias_moving_mean=False,scope=None,renorm=False,renorm_clipping=None,renorm_decay=0.99,adjustment=None)"
FusedBatchNorm="tf.nn.fused_batch_norm(x,scale,offset,mean=None,variance=None,epsilon=0.001,data_format='NHWC',is_training=True,name=None)"
DepthwiseConv2dNative="tf.nn.depthwise_conv2d(input,filter,strides,padding,rate=None,name=None,data_format=None)"
Reshape="tf.reshape(tensor,shape,name=None)"
Transpose="tf.transpose(a,perm=None,name='transpose',conjugate=False)"
MaxPool="tf.nn.max_pool(value,ksize,strides,padding,data_format='NHWC',name=None,input=None)"
AvgPool="tf.nn.avg_pool(value,ksize,strides,padding,data_format='NHWC',name=None)"
ConcatV2="tf.concat(values,axis,name='concat')"
Sum="tf.math.reduce_sum(input_tensor,axis=None,keepdims=None,name=None,reduction_indices=None,keep_dims=None)"
Add="tf.math.add(x,y,name=None)"
BiasAdd="tf.nn.bias_add(value,bias,data_format=None,name=None)"
AddN="tf.math.add_n(inputs,name=None)"
Sub="tf.math.subtract(x,y,name=None)"
Mul="tf.math.multiply(x,y,name=None)"
MatMul="tf.linalg.matmul(a,b,transpose_a=False,transpose_b=False,adjoint_a=False,adjoint_b=False,a_is_sparse=False,b_is_sparse=False,name=None)"
Exp="tf.math.exp(x,name=None)"
ReduceProd="tf.math.reduce_prod(input_tensor,axis=None,keepdims=None,name=None,reduction_indices=None,keep_dims=None)"
ReduceMean="tf.math.reduce_mean(input_tensor,axis=None,keepdims=None,name=None,reduction_indices=None,keep_dims=None)"
Sqrt="tf.math.sqrt(x,name=None)"
RealDiv="tf.realdiv(x,y,name=None)"
ArgMax="tf.math.argmax(input,axis=None,name=None,dimension=None,output_type=tf.dtypes.int64)"
Softmax="tf.nn.softmax(logits,axis=None,name=None,dim=None)"
Squeeze="tf.squeeze(input,axis=None,name=None,squeeze_dims=None)"
Slice="tf.slice(input_,begin,size,name=None)"
Shape="tf.shape(input,name=None,out_type=tf.dtypes.int32)"
Size="tf.size(input,name=None,out_type=tf.dtypes.int32)"
Identity="tf.identity(input, name=None)"
StridedSlice="tf.strided_slice(input_,begin,end,strides,begin_mask=0,end_mask=0,ellipsis_mask=0,new_axis_mask=0,shrink_axis_mask=0,var=None,name=None)"
LogicalAnd="tf.math.logical_and(x,y,name=None)"
LogicalNot="tf.math.logical_not(x,name=None)"
LogicalOr="tf.math.logical_or(x,y,name=None)"
Greater="tf.math.greater(x,y,name=None)"
GreaterEqual="tf.math.greater_equal(x,y,name=None)"
Maximum="tf.math.maximum(x,y,name=None)"
ReduceMax="tf.math.reduce_max(input_tensor,axis=None,keepdims=None,name=None,reduction_indices=None,keep_dims=None)"
Minimum="tf.math.minimum(x,y,name=None)"
ReduceMin="tf.math.reduce_min(input_tensor,axis=None,keepdims=None,name=None,reduction_indices=None,keep_dims=None)"
Less="tf.math.less(x,y,name=None)"
#Assert= Don't include Assert, it is only for testing
ExpandDims="tf.expand_dims(input,axis=None,name=None,dim=None)"
Fill="tf.fill(dims,value,name=None)"
Pad="tf.pad(tensor,paddings,mode='CONSTANT',name=None,constant_values=0)"
OneHot="tf.one_hot(indices,depth,on_value=None,off_value=None,axis=None,dtype=None,name=None)"
####Control Flow low level API###### Use from tensorflow.python.ops import control_flow_ops
Switch="control_flow_ops.switch(data,pred,dtype=None,name=None)"
Merge="control_flow_ops.merge(inputs,name=None)"
Enter="_Enter(data,frame_name,is_constant=False,parallel_iterations=10,use_ref=True,use_input_shape=True,name=None)" #Might need an control_flow_ops.Enter() in front of it. 
Exit="control_flow_ops.exit(data,name=None)"
NextIteration="control_flow_ops._NextIteration(data, name=None)"
LoopCond="LoopCond(None)"
####################################
####TensorArray API#################
TensorArrayV3="tf.TensorArray(dtype,size=None,dynamic_size=None,clear_after_read=None,tensor_array_name=None,handle=None,flow=None,infer_shape=True,element_shape=None,colocate_with_first_write_call=True,name=None)"
TensorArrayScatterV3="Scatter(None,None,None)"
TensorArrayReadV3="Read(Non,None,None)"
TensorArrayWriteV3="Write(None,None,None)"
TensorArraySizeV3="Size(None)"
TensorArrayGatherV3="Gather(None,None,None)"
NoOp="NoOp(None)"
####################################
Round="tf.math.round(x,name=None)"
Stack="tf.stack(values,axis=0,name='stack')"
Unstack="tf.unstack(value,num=None,axis=0,name='unstack')"
GatherV2="tf.gather(params,indices,axis=None,validate_indices=None,name=None,batch_dims=0)"
CropAndResize="tf.image.crop_and_resize(image,boxes,box_ind=None,crop_size=None,method='bilinear',extrapolation_value=0,name=None,box_indices=None)"
ResizeBilinear="tf.image.resize_bilinear(images,size,align_corners=False,name=None,half_pixel_centers=False)"
####tf.resize_nearest_neighbor
####tf.resize_bicubic
####tf.resize_area
Tile="tf.tile(input,multiples,name=None)"
Range="tf.range(start, limit, delta=1, dtype=None, name='range')"
Equal="tf.math.equal(x,y,name=None)"
All="tf.keras.backend.all(x,axis=None,keepdims=False)"   #Might not be correct function
Any="tf.keras.backend.any(x,axis=None,keepdims=False)"   #Might not be correct function
Where="tf.where(condition,x=None,y=None,name=None)"
Split="tf.split(value,num_or_size_splits,axis=0,num=None,name='split')"
ZerosLike="tf.zeros_like(tensor,dtype=None,name=None,optimize=True)"
DynamicStitch="tf.dynamic_stitch(indices,data,name=None)"
RandomShuffle="tf.random.shuffle(value,seed=None,name=None)"
StopGradient="tf.stop_gradient(input,name=None)"
TopKV2="tf.math.top_k(input,k=1,sorted=True,name=None)"
NonMaxSuppressionV3="tf.image.non_max_suppression(boxes,scores,max_output_size,iou_threshold=0.5,score_threshold=float('-inf'),name=None)"
Cast="tf.cast(x,SrcT,name=None)"


#######Variables and constants############
Variable="tf.Variable(initial_value,trainable=None,collections=None,validate_shape=True,caching_device=None,name=None,variable_def=None,dtype=None,expected_shape=None,import_scope=None,constraint=None,use_resource=None,synchronization=tf.VariableSynchronization.AUTO,aggregation=tf.VariableAggregation.NONE,shape=None)"
Constant="tf.constant(value,dtype=None,shape=None,name='Const',verify_shape=False)"

OpNameDict={
   "Placeholder":Placeholder,
   "Conv2D":Conv2D,
   "Relu6":Relu6,
   "Relu":Relu,
   "FusedBatchNorm":FusedBatchNorm,
   "DepthwiseConv2dNative":DepthwiseConv2dNative,
   "Reshape":Reshape,
   "Transpose":Transpose,
   "MaxPool":MaxPool,
   "AvgPool":AvgPool,
   "ConcatV2":ConcatV2,
   "Sum":Sum,
   "Add":Add,
   "BiasAdd":BiasAdd,
   "AddN":AddN,
   "Sub":Sub,
   "Mul":Mul,
   "MatMul":MatMul,
   "Exp":Exp,
   "Prod":ReduceProd,
   "Mean":ReduceMean,
   "RealDiv":RealDiv,
   "ArgMax":ArgMax,
   "Softmax": Softmax,
   "Squeeze":Squeeze,
   "Slice":Slice,
   "Shape":Shape,
   "Size":Size,
   # "Identity":Identity,     #Identity is more or less just a bridge. Hopefully can be ignored
   "StridedSlice":StridedSlice,
   "LogicalAnd":LogicalAnd,
   "LogicalNot":LogicalNot,
   "LogicalOr":LogicalOr,
   "Greater":Greater,
   "GreaterEqual":GreaterEqual,
   "Maximum":Maximum,
   "Max":ReduceMax,
   "Minimum":Minimum,
   "Min":ReduceMin,
   "Less":Less,
   "ExpandDims":ExpandDims,
   "Fill":Fill,
   "Pad":Pad,
   "OneHot":OneHot,
   ##########################
   # "Switch":Switch,     #Switch and       can have a bunch of issues, conider disabling if unstable.
   # "Merge":Merge,       #           Merge
   # "Enter":Enter,
   # "Exit":Exit,
   # "LoopCond":LoopCond,
   # "NextIteration":NextIteration,
   # "TensorArrayV3":"tf.TensorArray(dtype,size=None,dynamic_size=None,clear_after_read=None,tensor_array_name=None,handle=None,flow=None,infer_shape=True,element_shape=None,colocate_with_first_write_call=True,name=None)",
   # "TensorArrayScatterV3":TensorArrayScatterV3,
   # "TensorArrayReadV3":TensorArrayReadV3,
   # "TensorArrayWriteV3":TensorArrayWriteV3,
   # "TensorArraySizeV3":TensorArraySizeV3,
   # "TensorArrayGatherV3":TensorArrayGatherV3,
   # "NoOp":NoOp,
   ###########################
   "Round":Round,
   "Pack":Stack,           #Pack and       are the same, although only Stack exists in python tf
   "Stack":Stack,          #         Stack 
   "Unpack":Unstack,
   "Unstack":Unstack,
   "GatherV2":GatherV2,
   "CropAndResize":CropAndResize,
   "ResizeBilinear":ResizeBilinear,
   "Tile":Tile,
   "Sqrt":Sqrt,
   "Range":Range,
   "Equal":Equal,
   "All":All,
   "Any":Any,
   "Where":Where,
   "Select":Where,
   "Split":Split,
   "ZerosLike":ZerosLike,
   "DynamicStitch":DynamicStitch,
   "RandomShuffle":RandomShuffle,
   "StopGradient":StopGradient,
   "TopKV2":TopKV2,
   "NonMaxSuppressionV3":NonMaxSuppressionV3,
   "Cast":Cast
}

ConstantNameDict={
   "Variable":Variable,
   "VariableV2":Variable,
   "Const":Constant
}