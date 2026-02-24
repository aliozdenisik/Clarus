import nodemailer from "nodemailer"
import { logger } from "@/lib/logger"
// Server-only module - do not import in client components
// This module handles email delivery via Gmail SMTP

interface SendEmailOptions {
  to: string
  subject: string
  html: string
  text?: string
}

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: Number(process.env.SMTP_PORT) || 587,
  secure: false, // TLS via STARTTLS
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASSWORD,
  },
})

/**
 * Send an email via Gmail SMTP.
 *
 * IMPORTANT: Always call with `void sendEmail(...)` (fire-and-forget).
 * This function handles all errors internally and never throws to the caller.
 * This pattern prevents OWASP timing attacks in auth flows.
 */
export async function sendEmail(options: SendEmailOptions): Promise<void> {
  try {
    await transporter.sendMail({
      from: process.env.SMTP_FROM,
      to: options.to,
      subject: options.subject,
      html: options.html,
      text: options.text,
    })
  } catch (error) {
    logger.error("[email] Failed to send email", {
      subject: options.subject,
      error: error instanceof Error ? error.message : String(error),
    })
    // Never re-throw: fire-and-forget ensures timing safety in auth flows
  }
}
