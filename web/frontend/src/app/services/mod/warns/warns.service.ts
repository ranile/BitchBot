import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Warn} from "../../../models/Warn";

@Injectable({
  providedIn: 'root'
})
export class WarnsService {

  constructor(private httpClient: HttpClient) {
  }

  async getGuildWarns(guildId: string, victimId: string = undefined) {
    let url = `/api/mod/${guildId}/warns`
    if (victimId) {
      url += '/?victim=${victimId}'
    }
    console.log(url)
    return (await this.httpClient.get<WarnsResponse>(url).toPromise()).warnings
  }
}

interface WarnsResponse {
  warnings: Warn[]
}
