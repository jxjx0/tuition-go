import { useApi } from "./api"

export function usePaymentService() {
  const api = useApi()

  function createCheckoutSession(data: {
    amount: number
    title: string
    description: string
    booking_id: string
    tutor_name: string
    subject: string
    lesson_date: string
  }) {
    return api.post("/payments/create-checkout-session", data)
  }

  function getStripeSession(stripeSessionId: string) {
    return api.get(`/payments/stripe-session/${stripeSessionId}`)
  }

  return {
    createCheckoutSession,
    getStripeSession
  }
}