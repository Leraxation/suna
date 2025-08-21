export function getAgentAvatar(id: string) {
  // Simple hash function to generate consistent avatar based on id
  const hash = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const avatars = ['🤖', '🦾', '🔮', '🌟', '⚡'];
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#D4A5A5'];
  const index = hash % avatars.length;
  return { avatar: avatars[index], color: colors[index] };
}