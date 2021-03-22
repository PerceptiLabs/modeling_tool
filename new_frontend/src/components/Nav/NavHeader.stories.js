import NavHeader from "./NavHeader.vue";

export default {
  title: "Components/NavHeader",
  component: NavHeader,
};

const Template = (args) => ({
  // Components used in your story `template` are defined in the `components` object
  components: { NavHeader },
  // The story's `args` need to be mapped into the template through the `setup()` method
  setup() {
    // Story args can be spread into the returned object
    return { ...args };
  },
  // Then, the spread values can be accessed directly in the template
  template: "<NavHeader />",
});

export const BaseState = Template.bind({});
