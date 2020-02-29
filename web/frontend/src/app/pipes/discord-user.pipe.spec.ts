import { DiscordUserPipe } from './discord-user.pipe';

describe('DiscordUserPipe', () => {
  it('create an instance', () => {
    const pipe = new DiscordUserPipe();
    expect(pipe).toBeTruthy();
  });
});
