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

interface VerifyEmailTemplateProps {
  userName: string
  actionUrl: string
  locale?: string
}

export function VerifyEmailTemplate({
  userName,
  actionUrl,
  locale = "tr",
}: VerifyEmailTemplateProps) {
  const isTr = locale === "tr"

  return (
    <Html>
      <Head />
      <Preview>
        {isTr
          ? "E-posta adresinizi doğrulayın"
          : "Verify your email address"}
      </Preview>
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
            {isTr ? "E-posta adresinizi doğrulayın" : "Verify your email address"}
          </Heading>
          <Text style={{ fontSize: "15px", color: "#a1a1aa", marginBottom: "24px" }}>
            {isTr
              ? `Merhaba ${userName}, Clarus hesabınızı doğrulamak için aşağıdaki butona tıklayın.`
              : `Hi ${userName}, click the button below to verify your Clarus account.`}
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
            {isTr ? "E-postamı Doğrula" : "Verify My Email"}
          </Button>
          <Text style={{ fontSize: "13px", color: "#71717a", marginTop: "24px" }}>
            {isTr
              ? "Bu e-postayı siz istemediyseniz görmezden gelebilirsiniz."
              : "If you didn't request this, you can safely ignore this email."}
          </Text>
        </Container>
      </Body>
    </Html>
  )
}
