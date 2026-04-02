import { ref } from "vue"
import { usePaymentService } from "../services/paymentService"

export function usePayment() {
  const loading = ref(false)
  const error = ref<any>(null)

  const paymentService = usePaymentService()

  async function checkout(paymentData: any) {
    loading.value = true
    error.value = null

    try {
      const response = await paymentService.createCheckoutSession(paymentData)

      // redirect to Stripe
      window.location.href = response.data.url

    } catch (err: any) {
      error.value = err
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    checkout
  }
}