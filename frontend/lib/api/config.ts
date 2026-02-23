import { client } from "./client.gen"
export function configureApiClient(): void {
  client.setConfig({
    baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
  })
}
