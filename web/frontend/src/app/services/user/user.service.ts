import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Stats} from "../../models/Stats";

@Injectable({
    providedIn: 'root'
})
export class UserService {

    constructor(private httpClient: HttpClient) {
    }

    async fetchMyAvatarUrl(size: number) {
        const resp = await this.httpClient.get(`/api/icon?size=${size}`).toPromise()
        return resp['url']
    }

    async fetchMyStats() {
        return await this.httpClient.get<Stats>(`/api/stats`).toPromise()
    }
}
