import axios from "axios"

export const tutorApi = axios.create({
    baseURL: "http://127.0.0.1:5002",
    headers: {
        "Content-Type": "application/json"
    }
})