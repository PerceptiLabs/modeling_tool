<template lang="pug">
  .bg-loader
    .loader-box
      .dot.dot-1(ref='dot')
      .dot.dot-2(ref='dot')
      .dot.dot-3(ref='dot')
      .dot.dot-4(ref='dot')
      .dot.dot-5(ref='dot')
      .dot.dot-6(ref='dot')
      .dot.dot-7(ref='dot')
      .dot.dot-8(ref='dot')
</template>

<script>
  export default {
    name: "loader",
    mounted() {
      let dots = document.querySelectorAll('.dot');
      dots.forEach((dot)=>{
        dot.classList.add('animation');
      });

      setTimeout(()=>{
        dots.forEach((dot)=>{
          dot.classList.remove('animation');
        });
      }, 9300)
    }
  }
</script>

<style scoped lang="scss">
  $startTime: 0.5s;

  .bg-loader {
    background: rgba(0, 0, 0, 0.5);
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;

  }
  .loader-box {
    width: 12rem;
    height: 12rem;
    position: relative;
    animation: move-all $startTime linear $startTime*8 forwards;
  }
  .dot {
    width: 1.5rem;
    height: 1.5rem;
    background: #fff;
    border-radius: 10px;
    position: absolute;
    opacity: 0;
  }
  .dot-1{
    top: 5%;
    left: 43%;
    opacity: 1;
    animation:  move-all-to-center $startTime linear $startTime*9 forwards;
  }
 .dot-2{
   top: 5%;
   left: 43%;
   animation: move-dot-2 $startTime linear $startTime forwards,
              move-all-to-center $startTime linear $startTime*9 forwards;
  }
  .dot-3{
    //top: 43%;
    //left: 80%;
    top: 18%;
    left: 70%;
    animation:  move-dot-3 $startTime linear $startTime*2 forwards,
                move-all-to-center $startTime linear $startTime*9 forwards;
  }
  .dot-4{
    //top: 68%;
    //left: 70%;
    top: 43%;
    left: 80%;
    animation:  move-dot-4 $startTime linear  $startTime*3 forwards,
                move-all-to-center $startTime linear $startTime*9 forwards;
  }
  .dot-5{
    //top: 78%;
    //left: 43%;
    top: 68%;
    left: 70%;
    animation:  move-dot-5 $startTime linear $startTime*4 forwards,
                move-all-to-center $startTime linear $startTime*9 forwards;
  }
  .dot-6{
    //top: 68%;
    //left: 15%;
    top: 78%;
    left: 43%;
    animation:  move-dot-6 $startTime linear $startTime*5 forwards,
                move-all-to-center $startTime linear $startTime*9 forwards;
  }
  .dot-7{
    //top: 43%;
    //left: 6%;
    top: 68%;
    left: 15%;
    animation:  move-dot-7 $startTime linear $startTime*6 forwards,
                move-all-to-center $startTime linear $startTime*9 forwards;
  }
  .dot-8{
    //top: 18%;
    //left: 15%;
    top: 43%;
    left: 6%;
    animation:  move-dot-8 $startTime linear $startTime*7 forwards,
                move-all-to-center $startTime linear $startTime*9 forwards;
  }


  @-webkit-keyframes move-dot-2 {
    to {
      top: 18%;
      left: 70%;
      opacity: 1;
    }
  }
  @-webkit-keyframes move-dot-3 {
    to {
      top: 43%;
      left: 80%;
      opacity: 1;
    }
  }
  @-webkit-keyframes move-dot-4 {
    to {
      top: 68%;
      left: 70%;
      opacity: 1;
    }
  }
  @-webkit-keyframes move-dot-5 {
    to {
      top: 78%;
      left: 43%;
      opacity: 1;
    }
  }
  @-webkit-keyframes move-dot-6 {
    to {
      top: 68%;
      left: 15%;
      opacity: 1;
    }
  }
  @-webkit-keyframes move-dot-7 {
    to {
      top: 43%;
      left: 6%;
      opacity: 1;
    }
  }
  @-webkit-keyframes move-dot-8 {
    to {
      top: 18%;
      left: 15%;
      opacity: 1;
    }
  }
  @-webkit-keyframes move-dot-9 {
    to {
      opacity: 1;
    }
  }
  @-webkit-keyframes move-all {
    to{
      transform: rotate(360deg);
    }
  }
  @-webkit-keyframes move-all-to-center {
    to{
      top: 43%;
      left: 43%;
      transform: scale(0);
    }
  }
  @-webkit-keyframes move-to-center-2 {
    from{
      top: 18%;
      left: 15%;
    }
    to{
      top: 43%;
      left: 43%;
    }
  }


</style>



<!--Stats Load Animation: 1) one dot &ndash;&gt; 2 dots &ndash;&gt; 3 etc.-->
<!--reference: http://gph.is/2cI6gr9  but slower-->

<!--2) once full circle is complete: spin - shrink - disappear  reference: https://cdn.dribbble.com/users/1573707/screenshots/3712012/aug-4-2017-6-11-pm.gif-->

<!--3) start again if loading incomplete.-->

<!--maybe use the colours in the network?-->

