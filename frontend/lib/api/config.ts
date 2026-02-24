import { client } from "./client.gen"
import { API_BASE } from "@/lib/config"
export function configureApiClient(): void {
  client.setConfig({
    baseUrl: API_BASE,
    credentials: "include",
  })
}
