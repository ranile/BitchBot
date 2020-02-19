import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {User} from "../../models/User";

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private httpClient: HttpClient) { }

  async fetchCurrentUser() {
    const res = await this.httpClient.get<UserResponse>('/api/auth/me').toPromise()
    localStorage.setItem('user', JSON.stringify(res.user))
    return res
  }
}

interface UserResponse {
  id_from_session: string,
  user: User,
}
