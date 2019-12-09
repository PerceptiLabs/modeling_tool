<template lang="pug">
  .reshape-image_wrap(:style="styleWrap")
    .reshape-image(
      :class="{'reshape-image--3d': show3D}"
      :style="styleFront"
      )
      .side.top(:style="styleTop")
      .side.left(:style="styleLeft")
      .side.front(:style="styleFront")
</template>

<script>
  export default {
    name: "SettingReshapeImage",
    props: {
      axisSettings: {
        type: Array
      }
    },
    computed: {
      show3D() {
        const minVal = Math.min(...this.axisSettings);
        return minVal > 0
        //return true
      },
      ratioNum() {
        const maxVal = Math.max(...this.axisSettings);
        return maxVal/70
      },
      axisX() { return this.axisSettings[0]/this.ratioNum },
      axisY() { return this.axisSettings[1]/this.ratioNum },
      axisZ() { return this.axisSettings[2]/this.ratioNum },
      styleWrap() {
        if(this.show3D) {
          return {
            transform: `translate(${this.axisZ/5}px, ${this.axisY/12}px)`
          }
        }
      },
      styleFront() {
        return {
          width: `${this.axisX}px`,
          height: `${this.axisY}px`,
          //transform: `translateZ(${this.axisSettings[2]/2}px)`
        }
      },
      styleLeft() {
        return {
          width: `${this.axisZ}px`,
          height: `${this.axisY}px`,
          transform: `rotateY(90deg)`
        }
      },
      styleTop() {
        return {
          width: `${this.axisX}px`,
          height: `${this.axisZ}px`,
          transform: `translateY(-${this.axisY}px) rotateX(90deg)`
        }
      }
    }
  }
</script>

<style lang="scss" scoped>
  .reshape-image_wrap {
    display: flex;
    height: 10em;
    perspective: 1000px;
  }
  .side,
  .reshape-image {
    width: 6em;
    height: 6em;
  }
  .reshape-image {
    margin: auto;
    &--3d {
      transform-style: preserve-3d;
      transform: rotate3D(-1, 2, -0.2, 30deg) translate(0em, 0em);
    }
  }
  .side {
    /*min-width: 1px;*/
    /*min-height: 1px;*/
    .reshape-image--3d & {
      position: absolute;
      bottom: 0;
      left: 0;
    }
  }
  .left {
    display: none;
    transform-origin: left;
    background: #6986A7;
    .reshape-image--3d & {
      display: block;
    }
  }
  .top {
    display: none;
    transform-origin: center bottom;
    background: #B4DBF7;
    .reshape-image--3d & {
      display: block;
    }
  }
  .front {
    background: #93B1CD;
    min-width: 1px;
    min-height: 1px;
  }
</style>
