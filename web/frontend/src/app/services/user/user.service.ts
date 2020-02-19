import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {User} from "../../models/User";

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private httpClient: HttpClient) { }

  async fetchCurrentUser() {
    const res = await this.httpClient.get<UserResponse>('/api/users/me').toPromise()
    localStorage.setItem('user', JSON.stringify(res.user))
    return res
  }

  get currentUser() {
    return JSON.parse(localStorage.getItem('user'))
  }
}

interface UserResponse {
  id_from_session: string,
  user: User,
}
