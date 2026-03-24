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
    return api.post("/payment/create-checkout-session", data)
  }

  return {
    createCheckoutSession
  }
}