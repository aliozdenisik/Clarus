import {
  Html,
  Head,
  Body,
  Container,
  Heading,
  Text,
  Button,
  Preview,
} from "@react-email/components"

interface ResetPasswordTemplateProps {
  userName: string
  actionUrl: string
  locale?: string
}

export function ResetPasswordTemplate({
  userName,
  actionUrl,
  locale = "tr",
}: ResetPasswordTemplateProps) {
  const isTr = locale === "tr"

  return (
    <Html>
      <Head />
      <Preview>{isTr ? "Şifrenizi sıfırlayın" : "Reset your password"}</Preview>
      <Body style={{ backgroundColor: "#0f0f11", fontFamily: "sans-serif" }}>
        <Container
          style={{
            margin: "0 auto",
            padding: "40px 24px",
            maxWidth: "560px",
          }}
        >
          <Heading
            style={{
              fontSize: "24px",
              fontWeight: "700",
              color: "#ffffff",
              marginBottom: "8px",
            }}
          >
            {isTr ? "Şifrenizi sıfırlayın" : "Reset your password"}
          </Heading>
          <Text style={{ fontSize: "15px", color: "#a1a1aa", marginBottom: "24px" }}>
            {isTr
              ? `Merhaba ${userName}, aşağıdaki butona tıklayarak şifrenizi sıfırlayabilirsiniz.`
              : `Hi ${userName}, click the button below to reset your Clarus password.`}
          </Text>
          <Button
            href={actionUrl}
            style={{
              backgroundColor: "#4f46e5",
              color: "#ffffff",
              padding: "12px 24px",
              borderRadius: "6px",
              fontSize: "15px",
              fontWeight: "600",
              textDecoration: "none",
              display: "inline-block",
            }}
          >
            {isTr ? "Şifremi Sıfırla" : "Reset My Password"}
          </Button>
          <Text style={{ fontSize: "13px", color: "#71717a", marginTop: "16px" }}>
            {isTr ? "Bu linkin süresi 1 saat sonra dolacak." : "This link expires in 1 hour."}
          </Text>
          <Text style={{ fontSize: "13px", color: "#71717a", marginTop: "8px" }}>
            {isTr
              ? "Bu e-postayı siz istemediyseniz görmezden gelebilirsiniz."
              : "If you didn't request this, you can safely ignore this email."}
          </Text>
        </Container>
      </Body>
    </Html>
  )
}
