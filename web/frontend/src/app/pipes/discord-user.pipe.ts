import { Pipe, PipeTransform } from '@angular/core';
import {User} from "../models/User";

@Pipe({
  name: 'discordUser'
})
export class DiscordUserPipe implements PipeTransform {

  transform(value: User, ...args: unknown[]): unknown {
    return `${value.name}#${value.discriminator}`;
  }

}
