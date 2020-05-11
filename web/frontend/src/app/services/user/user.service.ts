import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {User} from "../../models/User";
import {Guild} from "../../models/Guild";
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

    async fetchCurrentUser() {
        const res = await this.httpClient.get<UserResponse>('/api/users/me').toPromise()
        localStorage.setItem('user', JSON.stringify(res.user))
        return res
    }

    async fetch_guilds_i_mod() {
        const res = await this.httpClient.get<ModIn>('/api/mod/guilds').toPromise()
        localStorage.setItem('modIn', JSON.stringify({userId: res.id_from_session, guilds: res.guilds}))
        return res.guilds
    }

    fetchUser(userId: string) {
        return this.httpClient.get<User>(`/api/users/${userId}`).toPromise()
    }

    get currentUser() {
        return JSON.parse(localStorage.getItem('user'))
    }

    get modIn(): Promise<Guild[]> {
        const modIn = JSON.parse(localStorage.getItem('modIn'))
        if (!modIn) {
            return this.fetch_guilds_i_mod()
        }
        if (this.currentUser.id == modIn.userId) {
            return Promise.resolve(modIn.guilds)
        } else {
            throw 'User id in modIn does not match logged in user id'
        }
    }
}

interface UserResponse {
    id_from_session: string,
    user: User,
}

interface ModIn {
    id_from_session: string,
    guilds: Guild[],
}

