<template lang="pug">
  base-global-popup.add-card-popup(
    :title="popupTitle"
    title-align="text-center"
    @closePopup="closePopup"
  )
    template(:slot="popupTitle + '-content'")
      .popup-content
        .form_holder
          .form_label.bold Card number:
          .form_row
            input.form_input(
              type="text"
              v-model="cardNumber"
              maxLength="19"
              placeholder="1234 1234 1234 1234"
            )
        .form_holder
          .form_label.bold Full Name on Card:
          .form_row
            input.form_input(
              type="text"
              v-model="nameOnCard"
              placeholder="Type..."
            )
        .form_holder
          .form_row
            .form_holder.expiry
              .form_label.bold Expiry:
              .form_row
                input.form_input(
                  type="text"
                  v-model="expiry"
                  maxLength="5"
                  placeholder="MM / YY"
                )
            .form_holder.cvc
              .form_label.bold CVC:
              .form_row
                input.form_input(
                  type="text"
                  v-model="cvc"
                  placeholder="CVC"
                )
        .form_holder
          p.desc We do not keep any of your sensitive credit card information. All payments are securely handled by Stripe.
    template(slot="action")
      button.btn.btn--secondary(type="button" @click="closePopup") Cancel
      button.btn.btn--primary(type="button" @click="runTest") Run Test

</template>

<script>

  import BaseGlobalPopup from "@/components/global-popups/base-global-popup";
  export default {
    name: "AddCardPopup",
    components: { BaseGlobalPopup },
    data() {
      return {
        popupTitle: 'Add Card Details',
        cardNumber: '',
        nameOnCard: '',
        expiry: '',
        cvc: '',
      }
    },
    computed: {
    },
    methods: {
      closePopup() {
        this.$store.commit('globalView/set_addCardPopup', false);
      },

      runTest() {

      }
    },
    watch: {
      cardNumber() {
        let realNumber = this.cardNumber.replace(/ /gi, '')
        let dashedNumber = realNumber.match(/.{1,4}/g)
        this.cardNumber = dashedNumber.join(' ')
      },
      expiry() {
        let realNumber = this.expiry.replace(/\//gi, '')
        let dashedNumber = realNumber.match(/.{1,2}/g)
        this.expiry = dashedNumber.join('/')
      }
    }
  }
</script>

<style scoped lang="scss">
  

  .popup-content {
    max-width: 340px;
  }

  .form_holder {
    &.expiry {
      margin-right: 8px;
      input {
        text-align: center;
      }
    }
    &.cvc {
      margin-left: 8px;
      input {
        text-align: center;
      }
    }

    & .desc {
      font-size: 13px;
      line-height: 18px;
    }
  }
</style>
