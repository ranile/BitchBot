import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(private httpClient: HttpClient) { }

  async login() {
    // localStorage.setItem('user', JSON.stringify(user))
    return await this.httpClient.get('/api/auth/login').toPromise()
  }
}
