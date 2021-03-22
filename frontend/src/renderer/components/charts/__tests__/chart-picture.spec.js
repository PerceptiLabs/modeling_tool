import { mount, shallowMount } from '@vue/test-utils';
import ChartPicture from '@/components/charts/chart-picture.vue';

import Worker from '@/components/charts/__mocks__/worker-mock';

const testSetup = () => {
  window.Worker = Worker;
  HTMLCanvasElement.prototype.getContext = () => {};
};

testSetup();

describe('ChartPicture', () => {
  it('isMultiSeriesData is falsy if no chartData', () => {
    const localThis = { chartData: null }

    expect(ChartPicture.computed.isMultiSeriesData.call(localThis)).toBe(false);
  });

  it('isMultiSeriesData is falsy if single chartData', () => {
    const localThis = {
      chartData: {
        series: [{
          data: [],
          height: 0,
          type: 'rbga',
          width: 0,
          x_data: null
        }]
      }
    }

    expect(ChartPicture.computed.isMultiSeriesData.call(localThis)).toBe(false);
  });

  it('isMultiSeriesData is falsy if multi chartData', () => {
    const localThis = {
      chartData: {
        series: [{
          data: [],
          height: 0,
          type: 'rbga',
          width: 0,
          x_data: null
        }, {
          data: [],
          height: 0,
          type: 'rbga',
          width: 0,
          x_data: null
        }]
      }
    }

    expect(ChartPicture.computed.isMultiSeriesData.call(localThis)).toBe(true);
  });

  it('renders no arrows if isMultiSeriesData is falsy', () => {
    const wrapper = shallowMount(ChartPicture, {
      computed: {
        isMultiSeriesData() { return false; },
        isNotPicture() { return false; }
      },
      mocks: {
        $store: {
          getters: {
            'mod_workspace/GET_networkShowCharts': true
          }
        }
      }
    });

    expect(wrapper.find('.left-arrow').exists()).toBe(false);
    expect(wrapper.find('.right-arrow').exists()).toBe(false);
  });

  it('renders arrows if isMultiSeriesData is truthy', () => {
    const wrapper = shallowMount(ChartPicture, {
      data() {
        return {
          isHovering: true
        }
      },
      computed: {
        isMultiSeriesData() { return true; },
        isNotPicture() { return false; }
      },
      mocks: {
        $store: {
          getters: {
            'mod_workspace/GET_networkShowCharts': true
          }
        }
      }
    });

    expect(wrapper.find('.left-arrow').exists()).toBe(true);
    expect(wrapper.find('.right-arrow').exists()).toBe(true);
  });

  it('renders no slider if isMultiSeriesData is falsy', () => {
    const wrapper = shallowMount(ChartPicture, {
      computed: {
        isMultiSeriesData() { return false; },
        isNotPicture() { return false; }
      },
      mocks: {
        $store: {
          getters: {
            'mod_workspace/GET_networkShowCharts': true
          }
        }
      }
    });

    expect(wrapper.find('.slider').exists()).toBe(false);
  });

  it('renders slider if isMultiSeriesData is truthy', () => {
    const wrapper = shallowMount(ChartPicture, {
      data() {
        return {
          isHovering: true
        }
      },
      computed: {
        isMultiSeriesData() { return true; },
        isNotPicture() { return false; }
      },
      mocks: {
        $store: {
          getters: {
            'mod_workspace/GET_networkShowCharts': true
          }
        }
      }
    });

    expect(wrapper.find('.slider').exists()).toBe(true);
  });
});