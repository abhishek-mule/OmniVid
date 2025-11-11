// Using Resend as the email provider
import { Resend } from 'resend';

function getResend() {
  const apiKey = process.env.EMAIL_API_KEY;
  if (!apiKey) {
    console.warn('Email provider not configured: missing EMAIL_API_KEY');
    return null;
  }
  return new Resend(apiKey);
}

type EmailParams = {
  to: string;
  name: string;
  resetUrl: string;
};

export async function sendPasswordResetEmail({ to, name, resetUrl }: EmailParams) {
  const resend = getResend();
  if (!resend) return; // silently no-op when not configured
  try {
    await resend.emails.send({
      from: 'noreply@omnivid.app',
      to,
      subject: 'Reset Your Password',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2>Password Reset Request</h2>
          <p>Hello ${name},</p>
          <p>We received a request to reset your password. Click the button below to set a new password:</p>
          <p style="margin: 30px 0;">
            <a href="${resetUrl}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">
              Reset Password
            </a>
          </p>
          <p>If you didn't request this, you can safely ignore this email.</p>
          <p>Best regards,<br>The OmniVid Team</p>
          <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
          <p style="font-size: 12px; color: #6b7280;">
            This email was sent to ${to}. If you didn't request this, please ignore this email.
          </p>
        </div>
      `,
    });
  } catch (error) {
    console.error('Error sending password reset email:', error);
    // Do not throw, avoid failing build/runtime when provider is misconfigured
  }
}

export async function sendVerificationEmail({ to, name, verifyUrl }: { to: string; name: string; verifyUrl: string }) {
  const resend = getResend();
  if (!resend) return; // silently no-op when not configured
  try {
    await resend.emails.send({
      from: 'noreply@omnivid.app',
      to,
      subject: 'Verify Your Email Address',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2>Email Verification</h2>
          <p>Hello ${name},</p>
          <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
          <p style="margin: 30px 0;">
            <a href="${verifyUrl}" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">
              Verify Email
            </a>
          </p>
          <p>If you didn't create an account, you can safely ignore this email.</p>
          <p>Best regards,<br>The OmniVid Team</p>
        </div>
      `,
    });
  } catch (error) {
    console.error('Error sending verification email:', error);
    // Do not throw, avoid failing build/runtime when provider is misconfigured
  }
}
