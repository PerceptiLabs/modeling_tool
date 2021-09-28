<template lang="pug">
  main.pricing-wrapper
    perfect-scrollbar
      h1.pricing-header.bold Billing & Usage
      .pricing-view
        .pricing-column
          .pricing-sub-view
            div 
              span.sub-title.bold.mr-3 Current Cycle
              span June 1 - July 1
            
            table.w-100
              tr.border-bottom
                th.bold Machine
                th.bold Price
                th.bold Usage
                th.bold Cost
              tr(v-for="machine in machineList" :key="machine.id")
                td {{machine.machine}}
                td {{machine.price}}
                td {{machine.usage}}
                td {{machine.cost}}
              tr.border
                td.bold Total cost
                td
                td
                td $0.00
            
            .sub-content Based on your usage this month, you would use approximately $X.XX worth of machine capabilities by the end of this cycle. 

            button.btn.btn--primary View Billing History
          
          .pricing-sub-view
            .sub-title.bold Manage Utility
            .sub-content Training models on GPU optimises quality and efficiency.
            .form_row.justify-left
              .form_label.mr-2.bold Run training on:            
              base-radio(group-name="runOn" value-input="gpu" v-model="runOn")
                span GPU
              base-radio(group-name="runOn" value-input="cpu" v-model="runOn")
                span CPU

          
        .pricing-column
          .pricing-sub-view
            .sub-title.bold Pricing Options
            .sub-content You are currently on the free plan. This means your GPU usage is limited to xxx. To avoid blockers due to limited GPU run time, upgrade your plan. 
            button.btn.btn--primary Upgrade to Pro
          
          .pricing-sub-view
            .sub-title.bold Payment Method
            .sub-content No card linked. Add payment method to start using better machines.
            button.btn.btn--primary(@click="onAddCard") Add Payment Method

          .pricing-sub-view
            .sub-title2.bold Promo Code
            .sub-content2 Got a promo code? Enter it below to use it on your next billing cycle:
            .form_row.justify-left
              input.form_input.sub-promo(type="text" v-model="promoCode" placeholder="Paste")
            button.btn.btn--primary Upgrade to Pro
</template>

<script>
const mockMachineList = [
  {id: 1, machine: 'CPU Unlimited time', price: 'Free', usage: '0 min', cost: '$0.00' },
  {id: 2, machine: 'GPU (hours) First 30 minutes free', price: '$X.XX/h', usage: '28 min', cost: '$0.00' },
  {id: 3, machine: 'GPU (GB)', price: '$X.XX/h', usage: '0 GB', cost: '$0.00' },  
]

export default {
  created() {
  },
  data() {
    return {
      machineList: mockMachineList,
      promoCode:'',
      runOn: 'gpu'
    };
  },
  methods: {
    onAddCard() {
      this.$store.dispatch('globalView/SET_addCardPopup', true);
    }
  }
}
</script>

<style lang="scss" scoped>

.pricing-header {
  margin-bottom: 10px;
}
.pricing-wrapper {
  background-color: theme-var($neutral-7);
  border-radius: 15px 0px 0px 0px;
  padding: 10px 20px;
  display: flex;
  flex-direction: column;
}
.pricing-view {
  background: theme-var($neutral-8);
  border: $border-1;
  box-sizing: border-box;
  border-radius: 4px;

  padding: 30px;
  display: flex;
  flex: 1 1;
}

.pricing-column {
  width: 100%;
  &:not(:first-child) {
    margin-left: 15px;
  }

  .pricing-sub-view {
    width: 100%;
    border: $border-1;
    border-radius: 4px;
    padding: 30px;
    font-size: 16px;
    
    &:not(:first-child) {
      margin-top: 15px;
    }

    .sub-title, 
    .sub-content {
      margin-bottom: 25px;
    }

    .sub-title2,
    .sub-promo {
      margin-bottom: 10px;
    }
    .sub-content2 {
      margin-bottom: 20px;
    }

    .sub-promo {
      max-width: 250px;
    }
  }
}

table {
  margin-bottom: 25px;
  
  tr {
    th {
      text-align: left;
    }

    th, td {
      padding: 16px 0px;
    }

    &.border {
      border-top: $border-1;
      border-bottom: $border-1;
    }
    &.border-bottom {
      border-bottom: $border-1;
    }
  }
}

.mr-2 {
  margin-right: 8px;
}

.mr-3 {
  margin-right: 16px;
}
</style>
