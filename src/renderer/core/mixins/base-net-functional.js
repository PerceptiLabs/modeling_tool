const baseNetFunctional = {
  data() {
    return {
      contextIsOpen: false,
      settingsIsOpen: false
    }
  },
  mounted() {
    // this.$refs.el.addEventListener("focus", (event)=> {
    //   console.log('focus')
    //   document.addEventListener('keydown', (event) => {
    //     const keyName = event.key;
    //     alert('keydown event\n\n' + 'key: ' + keyName);
    //   });
    // }, false);
    // document.addEventListener('keydown', (event) => {
    //   const keyName = event.key;
    //   alert('keydown event\n\n' + 'key: ' + keyName);
    // });
  },
  methods: {
    openSettings() {
      this.hideAllWindow();
      this.settingsIsOpen = true;
    },
    openContext() {
      this.hideAllWindow();
      this.contextIsOpen = true;
    },
    hideAllWindow() {
      this.settingsIsOpen = false;
      this.contextIsOpen = false;
    },
    blurElement() {
      this.deselect();
    },
    clickEl() {
      console.log('clickEl')
    },
    setFocusBtn() {
      this.$refs.btn.focus()
      this.active = true;
    }
  }
}

export default baseNetFunctional
