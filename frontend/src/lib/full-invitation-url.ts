export default function fullInvitationUrl(token: string) {
  return `${process.env.NEXT_PUBLIC_APP_URL}/invitation?token=${token}`;
}
